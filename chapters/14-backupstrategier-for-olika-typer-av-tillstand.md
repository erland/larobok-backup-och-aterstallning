# 14. Backupstrategier för olika typer av tillstånd

En gemensam nattlig backup av alla volymer kan vara enkel att administrera. För ärendeplattformen skulle den ändå lämna flera obesvarade frågor: Kan beslut återställas med rätt transaktionshistorik? Går det att få tillbaka en borttagen bilaga? Hur långt tillbaka finns händelser för återspelning? Var sparas konsumenternas positioner och dedupliceringsmarkörer?

Det är mer användbart att **välja skydd utifrån tillståndets funktion och återställningskrav** än utifrån vilken server det råkar ligga på.

## 14.1 Upprätta en backupmatris

Börja med inventeringen från kapitel 4 och komplettera med driftsansvar, RPO/RTO och teknisk återställningsväg.

| Tillstånd | Rekommenderad utgångspunkt | Viktig kontroll vid återställning |
|---|---|---|
| Auktoritativ relationsdatabas | Databasstödd fysisk eller logisk backup samt transaktionsloggar där PITR krävs | Konsistens, loggkedja, schema- och applikationsversion |
| Objekt och bilagor | Versionering, beständig backup/replikering enligt riskanalys och skydd mot oavsiktlig radering | Objektnycklar, versioner, åtkomsträttigheter, referenser från databasen |
| Händelselogg | Definierad retention, replikering och separat backup/export om loggen är återställningskälla | Fullständighet, ordning per nyckel, positioner och historiska scheman |
| Arbetskö och outbox | Beständiga meddelanden och en dokumenterad strategi för kvarvarande publiceringsavsikter | Ingen förlorad uppgift och kontrollerat återförsök |
| Inbox och konsumentpositioner | Bevara tillsammans med affärstillstånd när de utgör en gemensam lokal transaktion | Dubletter eller luckor efter återställning |
| Härledda vyer och sökindex | Återuppbyggnad från verifierad källa om tiden räcker | Fullständighet före trafikväxling |
| Cache och kortlivade arbetsdata | Ofta ingen traditionell backup; säker kallstart och återfyllning | Ingen användning av föråldrade värden |
| Konfiguration och hemligheter | Versionshanterad konfiguration, säkrad nyckelhantering och dokumenterad återutgivning | Rätt version, behörighet och förtroendekedja |

Matrisen är inte ett påstående om att en viss produkt alltid stöder en viss metod. Exempelvis varierar möjligheten att backa upp brokerdata och återställa konsumentpositioner mellan system och tjänstemodeller. Här krävs ett produkt- och versionsspecifikt återställningstest.

## 14.2 Relationsdatabaser: en återställningsbar loggkedja

För PostgreSQL kan en fysisk basbackup kombineras med arkiverade Write-Ahead Log-filer, WAL, för att möjliggöra point-in-time recovery (PITR). Då kan databasklustret återställas till en vald tidpunkt som omfattas av en fullständig och användbar loggkedja. Loggarkiveringens faktiska funktion måste övervakas: en basbackup räcker inte för att återställa till godtycklig senare tid.

En logisk export med `pg_dump` är något annat än en fysisk basbackup. Den kan vara användbar för portabilitet eller selektiv datahantering men kan inte användas som startpunkt för PostgreSQLs WAL-baserade PITR. Även en korrekt PITR för en databas ger bara databasens **lokala** konsistens; den samordnar inte automatiskt tidsläget med andra tjänster eller redan expedierade beslut.

Före återställning behöver man också veta hur schemaförändringar, databasmigreringar, krypteringsnycklar och applikationsversioner hänger ihop. En gammal databas kan vara tekniskt startbar men inkompatibel med dagens programversion.

## 14.3 Objektlagring har andra felmönster än en databas

Bilagan till E-417 kan ligga i objektlagring och refereras från en databasrad. Om databasen återställs till 10.00 men objektlagringen till 10.05 kan extra objekt finnas kvar. Om objektlagringen återställs till 09.55 kan databasen i stället peka på en bilaga som saknas.

Versionering och retention kan ge skydd mot radering och överskrivning, men ersätter inte alltid en separat backup med önskad isolering. Versionshantering kan också innebära att tidigare versioner omfattas av särskilda gallrings- och integritetskrav. För återställning behöver databasen och objekten kopplas samman via beständiga ID:n och kontrollerbar referensintegritet. Man ska varken anta att alla filer måste återställas till exakt samma klockslag eller att alla objekt kan återfinnas enbart genom senaste versionsnumret.

## 14.4 Köer och händelseloggar kräver ett särskilt beslut

Det som en kö eller ström lagrar kan vara antingen tillfälligt arbetsmaterial eller den enda bevarade historiken över en väsentlig verksamhetshändelse. I det senare fallet får man inte behandla retentionen som en ren prestandainställning.

I en loggbaserad ström är replikering, retention, kompaktering, konsumentpositioner och eventuell export av loggdata separata begrepp. Ett återspelbart intervall måste faktiskt finnas kvar. En kompakterad logg kan vara bra för att återskapa senaste värdet per nyckel men är inte nödvändigtvis en fullständig historik över alla händelser. I arbetsköer kan kvitterade meddelanden redan ha tagits bort; då är en annan beständig källa nödvändig om man vill rekonstruera avslutat arbete.

Om broker eller kötjänst inte har en understödd återställningsmetod behöver systemarkitekturen uttryckligen beskriva hur data kan återskapas på annat sätt. Att kopiera interna brokerfiler eller en aktiv volym utan leverantörens dokumenterade procedur är ingen allmänt säker backupmetod.

## 14.5 Backup och konsumtionsposition måste passa ihop

Anta att handläggningstjänstens databas återställs till 10.00, men den sparade broker-offseten pekar på 10.10. Då kan tio minuters arbetsuppgifter vara borta samtidigt som konsumenten tror att meddelandena redan har behandlats. Om offseten flyttas tillbaka till 10.00 kan händelserna behandlas igen, vilket kräver fungerande deduplicering och ett tillräckligt återspelbart händelseintervall.

Lösningen är inte alltid en global backup vid en gemensam klocktid. I vissa system sparas bearbetningsposition och affärseffekt atomärt i samma databas; i andra krävs en dokumenterad återstartspunkt, konsumentstyrd återspelning och avstämning. Det viktiga är att backupplanen beskriver **hur konsumenternas kunskap om utfört arbete överlever återställningen**.

## 14.6 Förvaring, skydd och testbarhet

En backupstrategi är ofullständig utan krav på integritet, kryptering, åtkomstkontroll och skydd mot samtidiga fel och angrepp. Oberoende kopior, geografisk åtskillnad och oföränderliga lagringsmekanismer kan begränsa riskerna, men deras effekt beror på vem som kan radera, ändra eller låsa upp kopiorna och på vilken återställningsmiljö som finns tillgänglig.

Backupfrekvens väljs utifrån tolererbart dataförlustfönster, förändringstakt och kostnad. Retention avgör vilka äldre tillstånd som kan återställas. RTO påverkas dessutom av mängden data, överföringshastighet, nyckelåtkomst, återuppspelning, ombyggnad av vyer och verksamhetskontroller. En teoretisk backupkapacitet säger därför lite om den faktiska återställningstiden förrän hela kedjan har provats.

En återställningsövning bör åtminstone kunna visa att en vald säkerhetskopia går att öppna i en isolerad miljö, att relevanta loggar eller objekt kan kopplas till den, och att centrala verksamhetsregler håller efter rekonstruktionen. Detaljerad ordning för en större disaster-recovery-insats behandlas i kapitel 15, och testprogrammet utvecklas i kapitel 18.

## 14.7 Från filkatalog till återställningspaket

För ärendeplattformen kan ett återställningspaket bestå av:

- En inventering av auktoritativa databaser och objekt med ägare och tillgängliga återställningspunkter.
- En beskrivning av händelsekällor, deras retention och en verifierad möjlighet att återläsa nödvändiga intervall.
- Information om applikations- och schemaversioner, infrastrukturnivå och nyckelberoenden.
- En uppsättning verksamhetskontroller som avgör om ärenden, beslut och externa kvittenser kan anses avstämda.

Detta är inte en enda teknik eller en enda zipfil. Det är ett kontrakt mellan backup, plattform, applikation och verksamhet om vad som faktiskt kan återskapas. **Det bästa backupupplägget är det som ger ett verifierbart användbart resultat vid återställning, inte det som producerar flest gröna backupjobb.**

## 14.8 Praktiskt exempel: PostgreSQL och en exakt återställningspunkt

Anta att ärendetjänsten använder PostgreSQL och att ett felaktigt administrativt kommando genomfördes 10.07. Verksamheten vill återställa databasens innehåll till tillståndet precis före kommandot. En logisk export från föregående natt kan inte i sig erbjuda sådan punktåterställning. Med fysisk basbackup och en obruten kedja av WAL-segment (*write-ahead log*) kan PostgreSQL däremot återspela loggen till en vald målpunkt, förutsatt att rätt backup, tidslinje och loggar finns.

Det första beslutet är inte att starta återläsningen, utan att välja **vilken oåterkallelig ändring som ska uteslutas**. En klocktid kan vara osäker om loggar har annan tidszon eller om flera transaktioner sker nära varandra. En namngiven återställningspunkt kan vara tydligare när en sådan skapats i förväg; val av recovery target måste alltid verifieras mot databasens faktiska logg och produktversion. Återställningen genomförs isolerat och originalmiljön bevaras enligt incidentrutinen.

Det praktiska arbetsflödet omfattar att verifiera basbackupen, tillgången till samtliga nödvändiga WAL-filer och kompatibel PostgreSQL-version; starta en separat instans med dokumenterad återställningskonfiguration; kontrollera att recovery nått den valda punkten; och jämföra ett antal kända ärenden före och efter felhändelsen. **En lyckad databasstart är inte detsamma som ett verifierat återställningsresultat.**

Om en händelse om E-417 skickades 10.05 men mottagarens databas återställdes till 10.03 behöver integrationen dessutom hantera redan publicerade respektive mottagna effekter. PITR skyddar databasens historik, inte hela tjänstekedjans gemensamma tidsläge. När en PITR-återställd instans öppnas för produktion behöver dess nya tidslinje, repliker, reservkopior och loggarkivering hanteras så att framtida återställningar inte förlorar spårbarhet.

## 14.9 Praktiskt exempel: broker och konsumentpositioner

En broker med retention i sju dygn är inte likvärdig med sju dygns garanterad återställningsbarhet för varje affärsprocess. En arbetskö kan radera kvitterade meddelanden, medan en loggbaserad ström kan behålla poster enligt separata regler för retention, kompaktering och partitionering. Vilka historiska poster som faktiskt kan återläsas måste bekräftas för den valda produkten och dess konfiguration.

Anta att handläggningens lokala databas återställs till 10.00, medan dess senast committade brokerposition ligger vid en post som bearbetades 10.10. Om konsumenten fortsätter från brokerpositionen lämnas arbetsuppgifterna från perioden däremellan borta. Om positionen flyttas bakåt upprepas även vissa händelser som redan har haft effekt i andra system. Den säkra vägen är att jämföra händelsehistorik, lokal beständig behandlingsinformation och verksamhetsdata, välja en godtagbar startposition samt verifiera återleveransen under idempotenta regler.

I en Kafka-liknande ström kan man behöva hantera offset per partition och konsumentgrupp. Dessa offsets är inte ett gemensamt verksamhetskvitto; de anger läspositioner. I en RabbitMQ-liknande arbetskö får man i stället ta ställning till persistens, kvittenser, omleverans och om redan kvitterade meddelanden alls finns kvar. Därför behöver en backupplan skilja mellan att återställa själva brokern och att rekonstruera det verksamhetsarbete som passerat brokern.

| Felbild | Otillräckligt svar | Återställningsbar väg |
|---|---|---|
| Databas rullas tillbaka men offset ligger före | Starta bara om konsumenten | Identifiera glapp, återleverera från bevarad källa och stäm av |
| Broker återställs äldre än konsumentens effekt | Spela upp alla poster blint | Deduplicera, kontrollera affärstillstånd och yttre bieffekter |
| Retention har raderat nödvändiga händelser | Flytta offset bakåt | Återskapa från annan auktoritativ källa eller hantera manuell rekonstruktion |

Det gemensamma kravet är att återställning av applikationsdata, meddelandehistorik och behandlingspositioner ingår i **en provad sammanhängande metod**.

## 14.10 Testa en backupmatris som ett system

En backupmatris ska kunna följas till konkreta prov: återställ en vald PostgreSQL-tidpunkt med tillhörande loggar; hämta tillbaka en objektversion och kontrollera checksumma; kör en kontrollerad återleverans av historiska händelser; återskapa nödvändiga hemligheter med godkända rättigheter; och avstäm ett urval av ärenden mot externa kvittenser. För varje prov registreras faktisk datatillgång, tid till teknisk start, tid till verksamhetsgodkännande och vilka data som inte gick att rekonstruera.

Ingen enskild mekanism behöver lösa alla delarna. Arkitekturens uppgift är att beskriva hur mekanismerna hänger ihop och vilken verksamhetsrisk som återstår.
