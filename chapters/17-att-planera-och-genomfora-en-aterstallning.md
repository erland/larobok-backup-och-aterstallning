# 17. Att planera och genomföra en återställning

Klockan 09.14 upphör ärendeplattformens externa gränssnitt att svara. Driftteamet kan inom några minuter starta reservmiljön. Men vem avgör när beslutsflödet får öppnas? Är det säkert att återleverera händelserna i köerna? Och vem kontaktar den externa mottagare som kan ha tagit emot E-417 strax före avbrottet?

De frågorna visar skillnaden mellan en teknisk återställningsinstruktion och en **operativ återställningsförmåga**. Kapitel 15 beskrev vilka tillstånd som måste kunna återskapas. Här handlar det om hur människor, ansvar och verifierbara beslut förvandlar möjligheten till en kontrollerad insats.

## 17.1 Planera utifrån verksamhetsförmåga

En återställningsplan som enbart listar servrar och databaser saknar ofta besked om vad verksamheten faktiskt kan göra efteråt. Planens första nivå bör därför beskriva förmågorna *ta emot ärenden*, *handlägga*, *fatta beslut* och *expediera beslut*. För varje förmåga anges ansvarig beslutsfattare, prioritet, beroenden och mätbara acceptanskriterier. RPO och RTO ska avse den överenskomna förmågan, inte bara en enskild container eller databas.

Exempelvis kan verksamheten godta att nya ärenden tas emot med begränsad funktionalitet medan expediering hålls stängd för avstämning. Det måste vara bestämt i förväg: under ett haveri är det för sent att upptäcka att ingen har mandat att öppna en del av tjänsten.

Planen bör ange en möjlig degraderad driftform, hur man undviker att använda både primär- och reservmiljö samtidigt och vem som får besluta om ytterligare dataförlust när alternativa återställningspunkter finns. Den ska också specificera kontaktvägar som fungerar om den ordinarie identitets- eller samarbetsplattformen är nere.

## 17.2 En praktisk ansvarskedja

Flera roller kan innehas av samma person i en mindre organisation, men ansvaret behöver vara explicit:

| Ansvar | Huvuduppgift under återställning | Beslutsunderlag |
|---|---|---|
| Insatsledare | Samordnar lägesbild, tidslinje, kommunikation och beslut | Händelselogg och beroendekarta |
| Plattform- och driftansvarig | Återskapar körmiljö, åtkomst och beständiga lagringsresurser | Infrastrukturkontroller och backupstatus |
| Tjänsteansvariga utvecklings-/driftteam | Bedömer egna transaktioner, konsumentpositioner och återstartbarhet | Applikationsloggar, data- och meddelandemarkörer |
| Integrationsansvarig | Pausar, återöppnar och stämmer av externa flöden | Kvittenser, korrelations-ID och partnerkontakt |
| Informations- och verksamhetsansvarig | Godkänner konsekvenser för information och verksamhetsprocesser | Avvikelser, RPO-utfall och kontrollresultat |
| Säkerhetsansvarig vid misstänkt angrepp | Beslutar om isolering och säkerhetsgrindar | Incidentindikatorer och förtroendebedömning |

Insatsledaren tar inte automatiskt över verksamhetsägarens mandat. Om en förlorad återställningspunkt innebär att ärenden behöver rekonstrueras manuellt krävs ett verksamhetsbeslut. Vid personuppgifter eller rättsligt reglerade processer kan även andra funktioner behöva medverka.

## 17.3 Gör det osäkra läget synligt

När händelsen inträffar finns sällan fullständig kunskap. Därför ska insatsen föra en tidsstämplad lägeslogg som skiljer mellan **bekräftat**, **sannolikt** och **okänt**. För E-417 kan följande vara bekräftat: ärendedatabasen kan återställas till 09.08 och handläggningens kö är tillgänglig. Det kan vara okänt om en extern beslutsmottagare behandlat ett anrop 09.10.

Att markera utfallet som okänt är inte ett nederlag. Felet uppstår om man behandlar det som misslyckat och skickar om beslutet utan avstämning. En användbar lägesbild anger också vilken källa som stödjer påståendet, vem som äger undersökningen och när status senast kontrollerades.

Före varje större ingrepp bör teamet säkra sådan evidens som behövs för att förstå tillståndet: relevanta loggar, konfigurationer, valda backup- och WAL-positioner, meddelandepositioner och leveransbekräftelser. Insamlingen får inte fördröja nödvändiga säkerhetsåtgärder; vid misstänkt kompromettering gäller kapitel 16:s särskilda förutsättningar.

## 17.4 En beslutsstyrd återställningssekvens

En *runbook* är ett kort exekverbart stöd, inte en essä. Den ska för varje kritiskt steg ange förutsättning, handling, kontroll och ansvarig. För ärendeplattformen kan den innehålla följande beslutspunkter:

1. **Deklarera läge:** Besluta om incidentnivå, prioriterade verksamhetsförmågor, kommunikationskanaler och om skrivningar ska stoppas.
2. **Avgränsa aktiv miljö:** Säkerställ att en gammal producent inte fortsätter skriva parallellt med reservmiljön. Bekräfta styrning av externa anslutningar.
3. **Välj datagrund:** Dokumentera vilka återställningspunkter och historiker som används, uppskattad dataförlust och beroenden som kräver avstämning.
4. **Återskapa och validera:** Starta tekniska beroenden, återställ auktoritativ data och verifiera resultatet. Konsumenter med oklara positioner förblir pausade.
5. **Hantera mellanlägen:** Identifiera händelser som publicerats men ännu inte säkert behandlats, öppna outbox/inbox-kontroller och skapa åtgärdslista över externa okända utfall.
6. **Öppna per förmåga:** Släpp först de flöden vars kontroller har godkänts. Besluta särskilt om externa utskick, efterbearbetning och eventuella manuella arbetsrutiner.
7. **Överlämna:** Dokumentera olösta avvikelser, bevakning, ansvar för uppföljning och formellt beslut om normaldrift.

Varje beslutspunkt måste ha ett tydligt nej-alternativ: vad händer om avstämningen inte går att slutföra? Möjliga svar är fortsatt stopp, begränsad drift eller manuell hantering med dokumenterad riskacceptans — inte att systemet öppnas på chans.

## 17.5 Exempel: E-417 blir ett öppningsvillkor

Efter återstart visas E-417 i handläggningstjänsten men inte i ärendetjänsten. Dessutom finns en osäker extern leverans. Insatsledaren ger tjänsteansvariga i uppdrag att klarlägga relationen mellan ärendets registrering, handläggningsuppgiften och det externa svaret. Integrationsansvarig kontrollerar mottagarens transaktionsstatus med ursprunglig korrelationsnyckel.

Tre utfall är tänkbara. Om mottagaren säkert har behandlat beslutet ska den interna historiken kompletteras genom en spårbar återställningsåtgärd — inte genom att sända samma beslut igen. Om mottagaren säkert inte har behandlat det kan ett kontrollerat nytt försök övervägas enligt integrationskontraktet. Om utfallet fortfarande är okänt får expedieringsflödet för just detta ärende förbli spärrat tills utredning eller godkänt manuellt förfarande finns.

**Aha-punkten:** Det är inte nödvändigt att hela systemet väntar på en enda svårutredd transaktion. Arkitekturen och runbooken kan möjliggöra selektiv återöppning, där osäkra ärenden hålls avskilda medan säkra ärenden hanteras vidare.

## 17.6 Kommunikation och avslut

Kommunikationen ska innehålla vad som är påverkat, vilken verksamhetsförmåga som återkommit, kända begränsningar, nästa beslutspunkt och hur användare eller integrationsparter ska agera. Ett meddelande om att ''alla servrar är gröna'' är sällan tillräckligt.

När incidenten avslutas ska återställningsloggen visa vilka tekniska kopior som användes, vad som rekonstruerades, vilka externa avstämningar som gjordes, uppmätt återställningstid och eventuell avvikelse mot RPO/RTO. Öppna datakvalitetsärenden och manuella korrigeringar ska ha ägare. Denna dokumentation blir dessutom underlag för nästa övning.

En återställningsplan är därmed mer än en ordningsföljd av kommandon: den är **ett kontrakt mellan teknik och verksamhet om när ett system får betraktas som återställt**. Hur vi säkerställer att kontraktet håller i praktiken är ämnet för nästa kapitel.
