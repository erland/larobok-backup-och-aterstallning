# 19. Styrning, ansvar och arkitekturstyrning

Ett återställningsprov av ärendeplattformen är godkänt: databaserna kan läsas tillbaka och alla tjänster går att starta. Ändå saknas en överenskommelse om vem som får godkänna återöppning av beslutsexpediering när utfallet hos en extern mottagare är oklart. Driftteamet kan starta tekniken; utvecklingsteamet kan förklara meddelandena; verksamheten ansvarar för besluten. Men ingen har mandat att avgöra den återstående risken.

Det är ett styrningsfel, inte ett nytt fel i backupverktyget. **Återställningsförmågan måste ha en ägare även där det tekniska ägarskapet är uppdelat.**

## 19.1 Börja med verksamhetsflödet, inte serverlistan

Den naturliga förvaltningsenheten för många IT-avtal är en applikation eller plattform. Återställningens konsekvenser följer däremot verksamhetsflöden: från registrering av E-417 till handläggning, beslut, expediering och kvittens. Ett flöde kan passera flera tjänster, team, leverantörer och informationsägare.

Verksamhetsansvarig behöver därför uttrycka vilket resultat som måste kunna återskapas: hur länge registrering får vara otillgänglig, vilka beslut som måste vara spårbara, hur okända expedieringsutfall ska hanteras och vilka tillfälliga arbetssätt som är acceptabla. Dessa mål översätts till tekniska kvalitetskrav och testbara påståenden. RPO och RTO är viktiga, men inte tillräckliga om det saknas ett kriterium för korrekt sammanhängande verksamhetstillstånd.

En verksamhetskonsekvensanalys, ofta kallad BIA, kan ge prioriteringar och konsekvensnivåer. Den behöver kompletteras med en karta över tjänster, auktoritativa informationsmängder, meddelandeberoenden och externa parter. Därmed blir det synligt vilka delar som kan återställas självständigt och vilka som kräver samordnade beslut.

## 19.2 Skilj ansvar för komponent från ansvar för förmåga

En användbar ansvarsfördelning är följande. Den är ett exempel, inte en obligatorisk organisationsmodell.

| Ansvar | Huvudsakligt åtagande | Konkret leverans |
|---|---|---|
| Verksamhets- och processägare | Fastställer acceptabelt avbrott, tolererbar informationsförlust och kriterier för återöppning | Godkända mål för verksamhetsflödet och beslutspunkter |
| System- eller tjänsteägare | Ansvarar för tjänstens data, återstartbarhet och ändringar som påverkar återställning | Tjänstens återställningskontrakt och provresultat |
| Lösnings- och integrationsarkitekt | Visar beroenden och översätter kraven till sammanhängande designbeslut | Beroendekarta, arkitekturbeslut och identifierade konsistensrisker |
| Plattform- och driftansvariga | Säkerställer återställbara miljöer, backup, behörigheter och utförbara procedurer | Återläsningsunderlag, driftprov och beredskap |
| Informations- och säkerhetsansvariga | Ställer krav på integritet, bevarande, konfidentialitet och tillit efter incident | Informationsklassning och säkerhetskriterier |
| Extern integrationspart | Utför de åtaganden som faktiskt har avtalats, exempelvis kvittens och statusfråga | Dokumenterat kontrakt och gemensamt testfall |

Tabellen beskriver ansvar, inte en automatisk rätt att fatta varje beslut. Den organisation som driver verksamheten måste också utse **en namngiven beslutsfunktion för återöppning** och en ersättare. En teknisk insatsledare kan rekommendera att trafik släpps på; den verksamhetsansvariga beslutsfunktionen accepterar konsekvenserna enligt gällande mandat.

## 19.3 Ett delat ansvar får inte bli ett ansvarsglapp

Det vanligaste gränsproblemet är inte att ingen ansvarar för sin egen del. Det är att alla gör det — men ingen ansvarar för det som sker *mellan* delarna.

I ärendeplattformen kan ärendetjänsten garantera en återställbar databas, meddelandeplattformen garantera sin dokumenterade retention och handläggningstjänsten garantera att dubletter inte skapar dubbla uppgifter. Vem har då verifierat att E-417 kan följas hela vägen genom kedjan efter en gemensam störning? Det måste finnas en uttalad flödesägare eller en delegerad samordnande funktion med mandat att kräva den verifieringen.

För varje kritiskt verksamhetsflöde bör organisationen ha ett enkelt register som besvarar fyra frågor: vem äger resultatet, vilka tjänster och externa beroenden ingår, vilken återställningsnivå har accepterats och var finns det senast godkända sammanhängande provet? Registret ska vara tillräckligt litet för att faktiskt underhållas. Ett storskaligt inventarium som inte uppdateras vid förändring ger falsk trygghet.

## 19.4 Skriv krav som går att motbevisa

Kravet »systemet ska kunna återställas« är omöjligt att bedöma rättvist. Ett bättre krav beskriver gräns, händelse och verifierbart resultat:

> Vid återstart efter förlust av handläggningstjänstens databas ska ärenden som redan mottagits kunna rekonstrueras från angivna beständiga källor. Återleverans får inte skapa dubbla arbetsuppgifter, och ofullständigt rekonstruerade ärenden får inte automatiskt gå vidare till beslut.

Ett sådant krav säger inte vilket fabrikat av backupverktyg som måste användas. Det visar vad arkitektur, implementering och drift tillsammans ska uppnå. För tjänster och integrationer kan krav kompletteras med återställningskontrakt som anger källor, retention, versionsberoenden, dedupliceringsfönster, externa sidoeffekter och begränsningar. Särskilt viktiga är uttryckliga uppgifter om vad som **inte** kan garanteras.

Vid anskaffning och avtal med externa parter är frågor om statusuppslag, transaktionsidentifierare, kvittenser, avbrottsrutiner och gemensamma övningar ofta mer avgörande än en allmän formulering om hög tillgänglighet. Kravet måste förstås också anpassas till rättsliga villkor och faktiska kontraktsmöjligheter.

## 19.5 Arkitekturbeslut måste överleva projektet

En viktig arkitekturfråga ska resultera i ett spårbart beslut, inte bara en bild i ett projektmaterial. Om beslutskedjan för E-417 förutsätter att händelser sparas i minst en viss tid måste det framgå *varför* denna tid valts, vilket återställningsscenario den täcker, vem som ansvarar för inställningen och vilket test som kan visa om antagandet fortfarande håller.

Beslutet bör omprövas när någon ändrar exempelvis meddelanderetention, tjänstegränser, schema, extern leverantör, driftregion, krypteringsnycklar eller användningsmönster. Det är i dessa vardagliga förändringar som återställningsförmågan annars långsamt försvagas.

En proportionerlig styrning kopplar därför arkitekturgranskning och produktionsändring till en enkel kontroll: *Ändrar detta vilka tillstånd som kan förloras, återskapas, upprepas eller måste stämmas av?* Vid ja ska återställningskontrakt, dokumentation och relevanta prov justeras innan ändringen betraktas som avslutad.

## 19.6 Följ upp det som spelar roll

Antal genomförda backupjobb eller andelen gröna övervakningslampor visar bara delar av förmågan. Ledningen behöver också förstå täckningen av kritiska flöden, ålder på senast godkända återställningsprov, tid för återställning inklusive avstämning och antal öppna brister utan accepterad riskägare.

Avvikelser ska inte automatiskt leda till ett krav på maximal teknisk redundans. Organisationen behöver göra riskbaserade avvägningar mellan kostnad, återställningstid, möjlig dataförlust och verksamhetskonsekvens. En arkitektur som kan reparera en härledd sökvy på några timmar kan vara helt tillräcklig, medan en osäker beslutsexpediering kan kräva omedelbar spärr och mänsklig avstämning.

Det avslutande styrningsprovet är enkelt att formulera: **Kan organisationen visa vem som får säga att ett kritiskt verksamhetsflöde är återställt — och på vilka belägg det beslutet vilar?** Om svaret är oklart saknas fortfarande en del av återställningsförmågan, oavsett hur moderna verktygen är.
