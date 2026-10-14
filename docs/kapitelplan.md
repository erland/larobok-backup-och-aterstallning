# Detaljerad kapitelplan

## Redaktionellt upplägg – fördjupning utan upprepning

**Bokens huvudfråga:** Varför kan alla tekniska komponenter vara återställda utan att verksamhetstillståndet är korrekt, och vad behöver arkitekter och driftansvariga göra annorlunda?

Inledningen demonstrerar ett konkret återställningshaveri där alla databaser har återställts men ett externt verkställt beslut saknas lokalt. Den ska väcka frågan, inte föregripa samtliga lösningar.

**Progression:** Kapitel 1 etablerar kort de förutsättningar där traditionella metoder fungerar. Kapitel 2 bryter dessa antaganden när systemet delas upp. Kapitel 3 beskriver vad en verksamhetsmässigt korrekt återställning kräver. Kapitel 4–11 förklarar *varför* tillstånd, meddelanden och processer gör det svårt och *hur* applikationer kan utformas. Kapitel 12 syntetiserar arkitekturval utan att lära ut mönstren på nytt. Kapitel 13–16 omsätter konsekvenserna i drift- och backupsystem. Kapitel 17–20 visar tillämpning, verifiering, ansvar och förändringsresa, utan att återupprepa tidigare teknikförklaringar.

**Redaktionella principer:**
1. Varje kapitel ska ha en unik fråga, en ny slutsats och ett avgränsat kunskapsansvar. Om två kapitel gör samma arbete ska stoff flyttas eller strykas.
2. Begrepp får en primär förklaring på en bestämd plats. I senare kapitel används en kort påminnelse eller hänvisning – inte en ny fullständig introduktion.
3. Genomgången av traditionell backup koncentreras till kapitel 1. Därefter görs jämförelser endast när de tydliggör en *ny* skillnad.
4. Ärendeplattformens exempel utvecklas stegvis; återge inte hela arkitekturen i varje kapitel. Skilj konsekvent på teknisk återstart, dataintegritet och korrekt verksamhetsförlopp.
5. Använd inte en obligatorisk mall med »traditionell metod – varför den inte räcker – lösning« för varje kapitel. Variera med haveriberättelse, arkitekturbeslut, förklarande analys och driftfall efter ämnets behov.
6. Undvik upprepade sammanfattningar, kapitelintroduktioner som annonserar innehåll och allmänna varningar utan nytt sakvärde. En syntes får vara kort och endast besvara kapitlets centrala fråga.
7. Sidantal är ingen produktionskvot. Teknisk precision och begriplighet har företräde framför omfattning.

**Avstämning vid varje kapitel:** Vilken ny insikt får läsaren? Vilket tidigare stoff kan ersättas av en hänvisning? Kan läsaren med traditionell driftbakgrund följa orsak och konsekvens? Tillför exemplet något nytt? Går någon passage att ta bort utan kunskapsförlust?

### Kunskapsansvar och unik dramaturgisk funktion

| Kapitel | Ny fråga och huvudpoäng | Avgränsning mot andra kapitel |
|---|---|---|
| Inledning | Hur kan en tekniskt lyckad restore ge fel verksamhetsläge? | Väcker frågan; ingen lösningskatalog |
| 1 | Vilka antaganden gör traditionell restore hanterbar? | Kort referensram, inte backuphandbok |
| 2 | Vad bryts när monoliten delas upp? | Introducerar strukturen, inte lösningsmönstren |
| 3 | Hur vet vi om verksamheten faktiskt är återställd? | Definierar måltillstånd och avstämningsbehov |
| 4 | Vilka tillstånd är auktoritativa och vilka kan byggas om? | Dataägande, inte replayprocedur |
| 5 | Vad sparas och förloras i köer och eventströmmar? | Leveranssemantik, inte global konsistens |
| 6 | Varför kan individuellt korrekta återställningspunkter bli fel ihop? | Kausalitet och tid, inte generella brokerfunktioner |
| 7 | När fungerar replay och när är det farligt? | Rekonstruktion, inte idempotensens grundteknik |
| 8 | Hur gör vi en konsument säker att starta om? | Huvudförklaring av idempotens och deduplicering |
| 9 | Hur undviks gapet mellan commit och publicering? | Outbox/inbox och leveransgränser, inte allmän retrylära |
| 10 | Hur återhämtar sig pågående flerpartsprocesser? | Saga och kompensation inom egna tjänster |
| 11 | Vad gör vi när omvärlden redan agerat? | Externa effekter, kvittenser och avstämning |
| 12 | Vilka designbeslut och kvalitetskrav följer? | Syntes och beslut, inga nya grundförklaringar |
| 13 | Vad måste plattformen kunna återskapa? | Infrastruktur och deklarativt tillstånd |
| 14 | Vad måste säkerhetskopieras, och med vilken metod? | Backupmatris, inte detaljerad DR-ordning |
| 15 | I vilken ordning återställer vi landskapet utan nya fel? | Orkestrering, återöppning och failover |
| 16 | Hur vet vi att återställningen är säker efter intrång? | Tillit, identitet och ren miljö |
| 17 | Hur leder vi ett faktiskt återställningsförlopp? | Beslut, roller och runbooks |
| 18 | Hur bevisar vi återställningsförmåga? | Test och verifiering, inte en ny processbeskrivning |
| 19 | Vem ansvarar för förmågan över systemgränser? | Styrning och ansvar, inte tekniska mönster |
| 20 | Hur tar vi oss från dagens läge till önskat läge? | Mognadssteg och prioriterad förändring |

## Genomgående fall: Ärendeplattformen

Tjänsterna Ärende, Handläggning, Beslut, Avisering och Extern integration äger olika datalager. En eventplattform distribuerar verksamhetshändelser. Scenarier: återställning av en databas, förlust/förskjutning av köläge, regionbortfall och redan verkställt externt beslut.

## Från traditionell backup till distribuerad återställning

### Kapitel 1. Backup och återställning i traditionella IT-system
- **Syfte och huvudtes:** Kort etablera förutsättningarna för fungerande klassisk återställning, utan att repetera en fullständig backuphandbok.
- **Begrepp och teknisk täckning:** Databasbackup, WAL/loggbackup, filflöden, transaktionssamordning; RPO/RTO.
- **Genomgående exempel:** Återställ en monolit med nattlig batch och visa återstartsvillkor.
- **Faktakontroll:** Verifiera produktberoende garantier, felbeteenden, förutsättningar och begrepp i primärkällor.

### Kapitel 2. Vad förändras med moderna IT-arkitekturer?
- **Syfte och huvudtes:** Mikrotjänster, autonom datalagring och asynkrona flöden.
- **Begrepp och teknisk täckning:** API/event, eventual consistency, systemgränser, delad infrastruktur.
- **Genomgående exempel:** Bryt upp ärendesystemet i tjänster och kartlägg tillstånd.
- **Faktakontroll:** Verifiera produktberoende garantier, felbeteenden, förutsättningar och begrepp i primärkällor.

### Kapitel 3. Från teknisk återställning till verksamhetsmässig återställning
- **Syfte och huvudtes:** Skillnaden mellan körbar miljö, korrekt data och fungerande process.
- **Begrepp och teknisk täckning:** Verksamhetens återställningsmål, invarianta regler, avstämning.
- **Genomgående exempel:** Återskapad databas men beslut och aviseringar stämmer inte.
- **Faktakontroll:** Verifiera produktberoende garantier, felbeteenden, förutsättningar och begrepp i primärkällor.

## Data, händelser och konsistens

### Kapitel 4. Dataägarskap och tillstånd i distribuerade system
- **Syfte och huvudtes:** Primära data, derivat, vyer, cache och informationsägarskap.
- **Begrepp och teknisk täckning:** Service-owned data, materialiserade vyer, replikering, GDPR/radering.
- **Genomgående exempel:** Kartlägg primärdata och härledda ärendevyer.
- **Faktakontroll:** Verifiera produktberoende garantier, felbeteenden, förutsättningar och begrepp i primärkällor.

### Kapitel 5. Meddelandeköer och händelseströmmar
- **Syfte och huvudtes:** Semantik för köer och loggbaserade strömmar.
- **Begrepp och teknisk täckning:** Retention, durable subscriptions, acknowledgements, offsets, DLQ, ordering.
- **Genomgående exempel:** Fel vid publicering respektive konsumtion av ÄrendeRegistrerat.
- **Faktakontroll:** Verifiera produktberoende garantier, felbeteenden, förutsättningar och begrepp i primärkällor.

### Kapitel 6. Tidsmässig konsistens mellan tjänster
- **Syfte och huvudtes:** Lokala checkpoints skapar inte automatiskt global konsistens.
- **Begrepp och teknisk täckning:** Happens-before/kausalitet, in-flight-medddelanden, watermark, gränser.
- **Genomgående exempel:** Tjänst A efter händelsen, B före samma händelse.
- **Faktakontroll:** Verifiera produktberoende garantier, felbeteenden, förutsättningar och begrepp i primärkällor.

### Kapitel 7. Återspelning av händelser och återuppbyggnad av tillstånd
- **Syfte och huvudtes:** Rebuild och replay med kontrollerade sidoeffekter.
- **Begrepp och teknisk täckning:** Event sourcing/CQRS, schemaversioner, snapshots, lagring och bevarandetid.
- **Genomgående exempel:** Bygg om sökindex utan att skicka om notifieringar.
- **Faktakontroll:** Verifiera produktberoende garantier, felbeteenden, förutsättningar och begrepp i primärkällor.

## Applikationsarkitektur för återställningsbarhet

### Kapitel 8. Att konstruera tjänster som går att återställa
- **Syfte och huvudtes:** Startbarhet och felhantering som arkitekturkrav.
- **Begrepp och teknisk täckning:** Idempotency key, dedup, återupptagning, state machines.
- **Genomgående exempel:** En återstartad konsument behandlar ett ärende två gånger.
- **Faktakontroll:** Verifiera produktberoende garantier, felbeteenden, förutsättningar och begrepp i primärkällor.

### Kapitel 9. Tillförlitlig händelsehantering
- **Syfte och huvudtes:** Fånga gapet mellan databascommit och publicering.
- **Begrepp och teknisk täckning:** Transactional outbox, inbox, at-least-once, transaktionskoppling.
- **Genomgående exempel:** Databascommit lyckas men broker är nere.
- **Faktakontroll:** Verifiera produktberoende garantier, felbeteenden, förutsättningar och begrepp i primärkällor.

### Kapitel 10. Långlivade verksamhetsprocesser och distribuerade transaktioner
- **Syfte och huvudtes:** Processer som korsar tjänster kan inte backas som en ACID-transaktion.
- **Begrepp och teknisk täckning:** Saga, kompensation kontra återföring, processägare, tidsgränser.
- **Genomgående exempel:** Ärende har registrerats och beslut påbörjats.
- **Faktakontroll:** Verifiera produktberoende garantier, felbeteenden, förutsättningar och begrepp i primärkällor.

### Kapitel 11. Integrationer med omvärlden
- **Syfte och huvudtes:** Externa effekter är inte reversibla via lokal databasrestore.
- **Begrepp och teknisk täckning:** Avstämning, externa id:n, kontrakt, kvittenser, replay-safe gateways.
- **Genomgående exempel:** Extern mottagare har verkställt beslut trots lokal restore.
- **Faktakontroll:** Verifiera produktberoende garantier, felbeteenden, förutsättningar och begrepp i primärkällor.

### Kapitel 12. Arkitekturprinciper för återställningsbara system
- **Syfte och huvudtes:** Översätt lärdomar till kvalitetskrav och designbeslut.
- **Begrepp och teknisk täckning:** RPO/RTO per förmåga, data lineage, ADR, kontraktstest.
- **Genomgående exempel:** Arkitekturgranskning av hela ärendeflödet.
- **Faktakontroll:** Verifiera produktberoende garantier, felbeteenden, förutsättningar och begrepp i primärkällor.

## Infrastruktur, backup och drift

### Kapitel 13. Infrastruktur för distribuerade system
- **Syfte och huvudtes:** Noder, zoner och regioner; tillgänglighet kontra återställning.
- **Begrepp och teknisk täckning:** Kubernetes, stateful workloads, lagringsklasser, control plane.
- **Genomgående exempel:** Återskapa kluster och tjänster från deklarativt tillstånd.
- **Faktakontroll:** Verifiera produktberoende garantier, felbeteenden, förutsättningar och begrepp i primärkällor.

### Kapitel 14. Backupstrategier för olika typer av tillstånd
- **Syfte och huvudtes:** Skydda rätt data med rätt återställningsmetod.
- **Begrepp och teknisk täckning:** PITR, objektversionering, immutable kopior, broker-replikering ≠ backup.
- **Genomgående exempel:** Backupmatris med databas, objekt, logg och metadata.
- **Faktakontroll:** Verifiera produktberoende garantier, felbeteenden, förutsättningar och begrepp i primärkällor.

### Kapitel 15. Disaster Recovery och återställning av hela systemlandskap
- **Syfte och huvudtes:** Återställningsordning som tar hänsyn till integrationsberoenden.
- **Begrepp och teknisk täckning:** Quiesce/fencing, koordinering, kontrollpunkter, failover/failback.
- **Genomgående exempel:** Regionbortfall med osynkroniserad broker och databaser.
- **Faktakontroll:** Verifiera produktberoende garantier, felbeteenden, förutsättningar och begrepp i primärkällor.

### Kapitel 16. Säkerhet, cyberangrepp och återställning
- **Syfte och huvudtes:** Rena kopior och tillitskedjor vid kompromettering.
- **Begrepp och teknisk täckning:** Air-gap/logisk isolering, identiteter, nycklar, rena miljöer.
- **Genomgående exempel:** Ransomware och osäker återställningspunkt.
- **Faktakontroll:** Verifiera produktberoende garantier, felbeteenden, förutsättningar och begrepp i primärkällor.

## Från design till verifierad förmåga

### Kapitel 17. Att planera och genomföra en återställning
- **Syfte och huvudtes:** Beslutsmodell från incident till verifierat verksamhetsläge.
- **Begrepp och teknisk täckning:** Runbook, triage, datakonsistens, startordning, kommunikation.
- **Genomgående exempel:** Tidslinje för samlad återställning av ärendesystemet.
- **Faktakontroll:** Verifiera produktberoende garantier, felbeteenden, förutsättningar och begrepp i primärkällor.

### Kapitel 18. Testning och verifiering av återställningsförmåga
- **Syfte och huvudtes:** Verifiera data, process och externa kontrakt.
- **Begrepp och teknisk täckning:** Restore drill, fault injection, verifieringsfrågor, bevis.
- **Genomgående exempel:** Övning med bortfallen databas och aktiva in-flight-events.
- **Faktakontroll:** Verifiera produktberoende garantier, felbeteenden, förutsättningar och begrepp i primärkällor.

### Kapitel 19. Styrning, ansvar och arkitekturstyrning
- **Syfte och huvudtes:** Vem äger den återställbara verksamhetsförmågan?.
- **Begrepp och teknisk täckning:** SLA/SLO, BIA, RACI, processägare, plattform och leverantör.
- **Genomgående exempel:** Kravspårning och gemensam återställningsövning.
- **Faktakontroll:** Verifiera produktberoende garantier, felbeteenden, förutsättningar och begrepp i primärkällor.

### Kapitel 20. Vägen från traditionell backup till modern återställningsförmåga
- **Syfte och huvudtes:** Mognadssteg för hybrida systemlandskap.
- **Begrepp och teknisk täckning:** Prioritering, förmågekarta, migrationssteg, investeringsanalys.
- **Genomgående exempel:** Roadmap för organisation med både monolit och tjänstelandskap.
- **Faktakontroll:** Verifiera produktberoende garantier, felbeteenden, förutsättningar och begrepp i primärkällor.

## Bilagor

- **Begrepp och definitioner:** Definitioner av bl.a. RPO, RTO, PITR, replay, idempotens, DLQ, återställningsbarhet.
- **Arkitekturprinciper och designmönster:** Outbox/inbox, saga, CQRS, idempotency keys, avstämning och återställningsgränser.
- **Checklista för lösningsarkitekter:** Bedöm dataägarskap, beroenden, externa effekter, replay och verifiering.
- **Checklista för drift- och plattformsansvariga:** Backupinventering, isolering, nycklar, återställningsordning och tester.
- **Exempel på återställningsplan och återställningsövning:** Runbook och övningsscenario för ärendehanteringssystemet.
- **Referenser och vidare läsning:** Källregister färdigställs parallellt med kapiteltexterna.
