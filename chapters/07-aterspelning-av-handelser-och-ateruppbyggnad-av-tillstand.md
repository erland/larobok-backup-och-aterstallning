# 7. Återspelning av händelser och återuppbyggnad av tillstånd

Efter haveriet har ärendetjänsten återställts, men handläggningens sökvy är tom. I den beständiga händelseströmmen finns däremot registreringarna kvar. Kan vi läsa dem igen och bygga upp sökvyn? Ja, om händelserna innehåller tillräcklig information och deras behandling kan upprepas säkert. Men samma metod kan bli farlig om återspelningen också skickar beslut eller notifieringar till omvärlden.

Det avgörande är alltså **vilket tillstånd vi återskapar och vilka handlingar vi samtidigt riskerar att utföra**.

## 7.1 Tre olika slags återuppbyggnad

Ordet *replay* används ibland för tre skilda operationer:

- **Återskapa en projektion:** Läs tidigare händelser och beräkna en sökvy, rapport eller annan härledd datamängd på nytt.
- **Återskapa en tjänsts tillstånd:** Återskapa en tjänsts egna affärstillstånd utifrån en auktoritativ händelsehistorik, som vid event sourcing.
- **Bearbeta en integration på nytt:** Leverera tidigare händelser till en mottagare så att den kan komplettera förlorad behandling.

De är inte utbytbara. En projektion som kan raderas och beräknas på nytt innebär inte att alla tjänsters affärsdatabaser kan återskapas på samma sätt. En integrationshändelse kan bara innehålla några utvalda fält. Om den inte beskriver alla relevanta tillståndsförändringar är den ingen fullständig återställningskälla.

Anta att `ÄrendeRegistrerat` innehåller ärende-ID och registreringsdatum. Den räcker för att bygga ett register över inkomna ärenden. Den räcker inte för att återställa en handläggares senare anteckningar om dessa aldrig publicerats som händelser. Det som inte finns i en tillförlitlig källa kan inte återskapas genom att läsa samma källa fler gånger.

## 7.2 Event sourcing är ett särskilt arkitekturval

Med *event sourcing* lagras tillståndsförändringar som en ordnad historik av domänhändelser, i stället för att endast lagra den senaste bilden av ett objekt. Ärendet E-417 kan då ha en sekvens som `ÄrendeRegistrerat`, `UnderlagKompletterat` och `ÄrendeAvslutat`. En projektion tillämpar händelserna i rätt ordning för att räkna fram aktuell status.

Det förutsätter att historiken är tillräckligt fullständig, tillgänglig och tillförlitlig. Den måste skyddas och säkerhetskopieras: en händelselogg är inte automatiskt en backup. Loggens retention, borttagning, kompaktering, rättning av felaktiga uppgifter och åtkomstkontroll påverkar möjligheten att rekonstruera tillstånd. Inte heller innebär användning av Kafka eller en annan strömningsplattform automatiskt event sourcing.

En sådan historik ger goda möjligheter att återskapa alternativa läsvyer. Men arkitekturen blir mer komplex: schemaförändringar, händelseordning, historiska buggar och lång återspelningstid måste hanteras. Event sourcing är lämpligt för vissa verksamhetsdomäner, inte ett generellt krav på alla mikroservicetjänster.

## 7.3 En konkret återställning av E-417

Anta att handläggningstjänstens härledda kö tappas vid ett lagringsfel medan ärendetjänstens auktoritativa historik och händelselogg finns kvar. Vi genomför återuppbyggnaden i en avskild projektion:

1. Frys eller versionsmärk den avsedda källpositionen, exempelvis per partition, så att vi vet vilka händelser återuppbyggnaden omfattar.
2. Skapa en tom målprojektion och säkerställ att dess bearbetningskod kan tolka alla relevanta äldre händelseversioner.
3. Läs från en dokumenterad startpunkt och tillämpa händelser i den ordning som domänens regler kräver. En global ordning över oberoende partitioner får inte antas.
4. Spara projektionens förändring och dess bearbetningsposition på ett sätt som ger säkert återupptagande efter avbrott.
5. Jämför antal, identifierare, tillstånd och avvikande ärenden med den auktoritativa källan. Växla först därefter över lästrafiken.

Nya händelser kan fortsätta komma medan arbetet pågår. Då behövs en strategi för att hinna ikapp utan glapp eller dubbel effekt, exempelvis en spårad källa och en kontrollerad växling mellan den gamla och nya projektionen.

**Aha-punkten:** Vi återställer inte en gammal säkerhetskopia av sökvyn. Vi *beräknar om* den från en mer auktoritativ källa. Det kan ge bättre återhämtning, men bara om den källan fortfarande är intakt.

## 7.4 Snapshots förkortar inte historien, de förkortar arbetet

Att läsa miljontals händelser kan ta längre tid än verksamhetens RTO tillåter. En snapshot av beräknat tillstånd kan vara en startpunkt: läs en verifierad snapshot till och med exempelvis sekvens 20 000, och applicera därefter händelser från sekvens 20 001.

Det kräver ett tydligt kontrakt mellan snapshot och logg: samma objektsidentitet, rätt händelseversioner, känd sekvensgräns och kontroll av att historiken inte har luckor. En snapshot som inte går att koppla till rätt loggposition kan skapa lika stora problem som en felaktigt samordnad databasbackup.

Snapshots är dessutom skyddsvärda data. Deras integritet, åtkomst, kryptering och återställningstid behöver testas. Om historiken har rättats eller migrerats måste man förstå om en äldre snapshot fortfarande kan användas.

## 7.5 Replay får inte betyda ”gör om allt”

Föreställ dig att händelsen `BeslutFattat` för E-417 redan lett till att ett brev skickats. Vid återspelning vill vi bygga upp vyn över beslut, inte skicka brevet en gång till.

En användbar design skiljer därför mellan **tillståndsberäkning** och **verkliga bieffekter**. Projektioner kan köras i ett uttryckligt återuppbyggnadsläge där externa anrop, notifieringar och kommando-publicering är avstängda. Ett sådant läge får inte enbart förlita sig på att en utvecklare kommer ihåg att inte anropa en viss funktion. Arkitekturen bör tydligt avgränsa vilka konsumenter som bara bygger vyer och vilka som initierar handlingar.

Det räcker inte heller att stänga av utskick för alltid. Om ett meddelande faktiskt måste återlevereras efter haveriet behöver vi veta om den externa mottagaren redan har agerat. Återställning kan då kräva avstämning och ett nytt beslutat handlingssteg, snarare än blind återspelning. Den frågan fördjupas i kapitel 11.

## 7.6 Historisk kod är en del av återställningsförmågan

Den kod som behandlar dagens händelser kanske inte förstår fält och betydelser från förra året. Vi behöver antingen behålla kompatibla läsare, använda dokumenterade migreringar eller omvandla äldre händelser till ett fördefinierat, versionshanterat format.

Ett allvarligare problem är att ett historiskt fel i beräkningslogiken kan ha lett till ett felaktigt tillstånd. Om vi spelar upp historiken med exakt samma felaktiga kod får vi samma fel igen. Om vi använder ny kod kan resultatet skilja sig från tidigare beslut. Det är då nödvändigt att skilja på att *rekonstruera den dåvarande historiken* och att *korrigera verksamhetstillståndet*. En sådan korrigering behöver spårbarhet och ibland ett uttryckligt nytt verksamhetsbeslut.

## 7.7 När är återspelning rätt metod?

Återspelning passar när den auktoritativa historiken är komplett nog, tillgänglig under tillräckligt lång tid, behandlingslogiken är kompatibel och resultatet kan valideras. Den passar sämre när viktiga förändringar saknas i historiken, när retentionen har löpt ut eller när konsumenten blandar projektioner med oåterkalleliga externa handlingar.

En viktig arkitekturprincip kan nu formuleras: **Designa återuppbyggbara tillstånd som återuppbyggbara från början; anta inte att alla förlorade data kan återspelas i efterhand.**

Nästa kapitel behandlar den andra halvan av återställningsbarheten: hur en tjänst kan tåla att samma arbete startar om eller kommer tillbaka utan att skapa en ny, felaktig effekt.
