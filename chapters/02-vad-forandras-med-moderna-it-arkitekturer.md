# 2. Vad förändras med moderna IT-arkitekturer?

I slutet av föregående kapitel gjorde vi en förändring i tanken: vi delade upp ärendesystemet i flera tjänster. Nu genomför vi den förändringen, steg för steg. Målet är inte att beskriva alla egenskaper hos mikrotjänster. Vi vill se vad som händer med förmågan att återställa systemet när det som tidigare kunde beslutas i en databastransaktion fördelas över flera självständiga komponenter.

## 2.1 Först ändrar vi organisationen av data

I det tidigare systemet låg ärende och beslut i samma databas. En handläggare kunde godkänna ett ärende och databasen kunde atomärt registrera både beslutet och den nya ärendestatusen. Antingen blev båda ändringarna bestående eller ingen av dem.

Anta att verksamheten nu vill kunna vidareutveckla ärendemottagningen och beslutsfattandet oberoende av varandra. Vi skapar två tjänster:

- **Ärendetjänsten** tar emot ärenden och äger datalagret för deras grunduppgifter och livscykel.
- **Beslutstjänsten** registrerar beslut och äger sin egen databas med beslutsunderlag och beslutshistorik.

Detta kan vara ett rimligt arkitekturbeslut. Tjänsterna får tydligare ansvar och kan förändras separat. Men en förändring som förr omfattades av en enda databastransaktion har nu blivit minst två lokala förändringar. Om beslutstjänsten registrerar ett beslut och ärendetjänsten uppdaterar ärendets status senare, finns ett tidsfönster då systemen vet olika mycket.

Tänk på vad en återställning betyder här. Vi kan återläsa varje databas korrekt, men det säger inte att kombinationen av deras tillstånd motsvarar ett sammanhängande händelseförlopp. **En fungerande säkerhetskopia för varje tjänst ger inte automatiskt en fungerande återställningspunkt för hela ärendet.**

Att tjänster har var sitt datalager är ett vanligt designval, inte en naturlag. Även system med en delad databas kan få motsvarande problem genom köer, externa effekter eller andra tillstånd som hanteras utanför databasen. Det avgörande är vilka förändringar som faktiskt kan samordnas atomärt.

## 2.2 Sedan ersätter vi det direkta anropet med ett meddelande

Anta att Ärendetjänsten efter registrering publicerar händelsen `ÄrendeRegistrerat`. Handläggningstjänsten tar emot den och startar sin bearbetning. Beslutstjänsten agerar när ett färdigt beslutsunderlag finns. Aviseringstjänsten meddelar berörda parter när beslutet är expedierat.

Varför gör man så? En registrering ska kanske kunna slutföras även när en annan tjänst tillfälligt är otillgänglig. Händelser gör att mottagare kan behandla arbetet senare och att nya konsumenter kan kopplas på utan att alla funktioner byggs in i Ärendetjänsten.

Men ett accepterat API-anrop, en committad databasskrivning, en publicerad händelse och en färdigbehandlad händelse är **fyra skilda observationer**. De måste inte inträffa samtidigt. Ett meddelande kan vara på väg, kvar i en kö, levererat men inte kvitterat eller behandlat av en tjänst vars svar ännu inte nått avsändaren.

Det skapar ett problem som inte syns i ett databasschema. Vid en återställning behöver vi veta mer än vilka rader som fanns i en databas. Vi behöver veta *vilka händelser andra komponenter kan ha hunnit reagera på*.

### En tidslinje där alla lokala steg lyckas

| Tid | Vad händer? | Vad finns kvar efter steget? |
|---|---|---|
| 10.01 | Ärendetjänsten lagrar ärende E-417. | Ärendet i databas A |
| 10.02 | Händelsen `ÄrendeRegistrerat` publiceras. | En händelse i meddelandeplattformen |
| 10.03 | Handläggningstjänsten registrerar en ny arbetsuppgift. | Uppgift i databas B |
| 10.04 | Ärendetjänsten får ett fel i sitt datalager. | Övriga tjänster fortsätter eventuellt |
| 10.10 | Databas A återställs till 10.00. | E-417 saknas i A men uppgiften finns i B |

Exemplet förutsätter att den lokala återställningen sker separat och att tjänst B inte återställs. Den beskrivna kombinationen är därför möjlig, inte ett oundvikligt utfall i alla arkitekturer. Den illustrerar varför en återställningsplan måste omfatta relationen mellan datalagren.

Det finns minst tre möjliga reaktioner: rekonstruera ärendet, återföra den andra tjänsten till ett lämpligt läge eller hantera avvikelsen som en särskild korrigering. Vilket alternativ som är riktigt beror på vad som är auktoritativ information och vilka effekter som redan uppstått. Vi avgör inte lösningen ännu.

## 2.3 Nya felgränser gör systemet både robustare och svårare att förstå

När en tjänst går ner kan en annan fortsätta arbeta. Det är ofta avsikten med den nya arkitekturen. Återställningsperspektivet förändras därmed från ett gemensamt stopp till **delvis framgång**: vissa steg har genomförts, andra väntar och ytterligare några kan ha misslyckats.

Ett fel kan också inträffa mellan två handlingar som var för sig är korrekta. Ärendetjänsten kan ha sparat en registrering men misslyckats med att publicera dess händelse. Eller en konsument kan ha skrivit till sin databas, kraschat före kvitteringen och senare få samma meddelande igen. Här uppstår inte bara frågan om *vilka data som finns*, utan också *vad som fortfarande kan hända när tjänsterna startar om*.

Det är en viktig skillnad mellan en **säkerhetskopia**, som beskriver lagrade data, och ett **pågående integrationsförlopp**, som omfattar meddelanden, väntande steg, försök och svar. Arkitekturen måste ha ett medvetet sätt att förhålla sig till båda. Hur man säkerställer publicering, återförsök och säker behandling av dubbletter behandlas längre fram i boken.

## 2.4 Asynkronitet förändrar betydelsen av »nu«

I ett synkront anrop väntar anroparen vanligen på ett svar innan den går vidare, även om svaret i sig inte garanterar att alla efterföljande effekter är färdiga. I ett asynkront flöde kan avsändaren vara klar långt före mottagaren. Olika tjänster kan därför ge olika svar på frågan om ett ärende är färdigt.

Det brukar kallas **eventual consistency** när systemet är utformat så att kopior eller härledda tillstånd under givna förutsättningar så småningom blir samstämmiga. Uttrycket är inte en ursäkt för godtyckliga fel. Man måste kunna ange vad som får släpa efter, vilka garantier som finns och vad som händer om en uppdatering aldrig når fram.

För återställning är denna skillnad avgörande. Efter ett haveri kan ett system se tillfälligt osammanhängande ut därför att normalt arbete ännu inte hunnit ikapp. Samma symptom kan också betyda att en händelse gått förlorad och att ingen komponent kommer att rätta till läget. **Att något är tillfälligt inkonsistent är inte detsamma som att det automatiskt blir korrekt.**

Det är därför återställning inte bör godkännas enbart utifrån att samtliga tjänster svarar på hälsokontroller. Vi behöver kunna skilja ett tillåtet mellanläge från ett fel som kräver åtgärd.

## 2.5 Lägg till omvärlden – och gränsen flyttas igen

Vi låter nu beslutstjänsten skicka ett beslut till en extern organisation via en integration. Den externa parten kvitterar och kan börja agera på beslutet. Kanske går ett beslut i nästa steg ut till en medborgare eller utlöser en faktisk utbetalning.

Om vår databas återställs till en tid före överföringen försvinner inte effekten hos mottagaren. Det gäller även om vi använder moderna containrar, geografiskt redundanta datalager och automatiserad återställning. Den externa parten befinner sig utanför vår tekniska återställningsgräns.

I ett äldre system fanns samma principiella risk vid filöverföring. Det nya är ofta att utbytet pågår fortlöpande och samtidigt över många gränser. Ett återställningsfönster kan därmed omfatta ett stort antal små, delvis avslutade verksamhetshändelser i stället för ett fåtal kända batchkörningar.

## 2.6 Vad är det egentligen som behöver skyddas?

När ärendesystemet nu är uppdelat har vi flera tillståndskategorier:

| Tillstånd | Exempel | Fråga vid återställning |
|---|---|---|
| Auktoritativa uppgifter | Ärenderegistrering, fastställt beslut | Vilken tjänst äger den giltiga uppgiften? |
| Härledda uppgifter | Arbetskö, sökvy, rapport | Kan de byggas om och ur vilket underlag? |
| Integrationsläge | Väntande händelse, kvittering, läsposition | Vilka steg har faktiskt utförts? |
| Extern effekt | Mottaget beslut, skickad avisering | Hur vet vi vad mottagaren har gjort? |
| Kör- och konfigurationstillstånd | Tjänsteversion, schema, behörighet | Kan vi återskapa en kompatibel miljö? |

Tabellen är inte en rekommendation att göra en fullständig backup av varje rad i varje kategori. I vissa fall är den rätta förmågan att *bygga om*, *läsa om*, *stämma av* eller *kompensera*. Infrastrukturens uppgift förändras därmed från att enbart skydda lagringsvolymer till att också stödja ett kontrollerat återställningsförfarande. Vilka data som ska säkerhetskopieras avgör vi först när deras roller är kända.

Den nya arkitekturen behöver alltså inte ha en enda gemensam återställningsklocka. Men den behöver ett sätt att avgöra vad som hänt och vad som måste ske innan verksamheten säkert kan fortsätta. Därmed kommer vi till nästa fråga: **hur känner vi igen ett korrekt återställt verksamhetstillstånd?**
