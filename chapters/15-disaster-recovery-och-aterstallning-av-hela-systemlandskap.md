# 15. Disaster Recovery och återställning av hela systemlandskap

Klockan 08.12 förlorar ärendeplattformen sin primära driftmiljö. En reservmiljö kan startas och de senaste databassäkerhetskopiorna finns tillgängliga. Inom en timme svarar samtliga tjänsters hälsokontroller grönt. Ändå hålls tjänsten stängd. Ärendedatabasen har återställts till 08.05, handläggningens databas till 08.08 och meddelandeplattformen har kvar händelser som redan har levererats till externa mottagare. Att öppna för nya ärenden nu kan göra det svårare att reda ut vilka beslut som faktiskt skickats.

Det är detta som gör katastrofåterställning (*Disaster Recovery*, DR) i ett distribuerat system till mer än en fråga om reservservrar. **DR är en kontrollerad övergång från ett otillgängligt och delvis känt tillstånd till ett verifierat läge där verksamheten säkert kan fortsätta.**

## 15.1 Börja med den tjänst som verksamheten behöver

Ett systemlandskap är ofta organiserat efter tekniska ägare: databasteam, integrationsplattform, containerplattform och tjänsteteam. Återställningen måste däremot styras av en sammanhängande verksamhetsförmåga, exempelvis *ta emot ärende*, *fatta beslut* eller *expediera beslut*. Dessa har olika beroenden och kan ibland öppnas i olika ordning.

För varje sådan förmåga behöver ansvariga i förväg ha beslutat vilken informationsförlust som kan accepteras (RPO), hur länge den får vara otillgänglig (RTO), och vilka felaktiga eller osäkra verksamhetstillstånd som aldrig får släppas igenom. Ett kort RTO för en containerplattform säger väldigt lite om tiden för att återställa en tjänst vars data måste stämmas av mot tre andra tjänster.

Vi skiljer därför mellan tre milstolpar: **tekniskt återställd** (komponenterna kan köras), **datamässigt avstämd** (kritiska samband och utestående operationer är kända) och **verksamhetsmässigt öppnad** (godkända flöden får återupptas). Ibland kan läsning tillåtas innan nya skrivningar och externa utskick öppnas. Dessa graderade öppningslägen måste vara medvetna arkitekturbeslut.

## 15.2 Beroendeordningen är inte samma sak som startordningen

En praktisk återställningskarta behöver visa både tekniska och verksamhetsmässiga beroenden. För ärendeplattformen kan den omfatta identitetstjänst och nyckelhantering, nät och DNS, klusterkonfiguration, beständiga datalager, meddelandeplattform, tjänster, externa anslutningar och övervakning. Att databasen står först i ett driftmanus betyder inte att dess återställningspunkt alltid är rätt i förhållande till broker och mottagande tjänster.

En möjlig ordning är att först återupprätta en betrodd kontrollmiljö med fungerande identiteter och observerbarhet. Därefter återställs de auktoritativa datakällorna och nödvändiga historikerna. Konsumenter hålls pausade tills databaspositioner, köer och återställningsgränser har bedömts. Först därefter öppnas interna flöden och till sist kontrollerat utbyte med omvärlden.

Detta är ingen allmängiltig startsekvens. Ett system med en broker som själv är auktoritativ källa kan kräva att loggen återskapas före härledda databaser. Ett annat system kan behöva återställa en extern katalog för att över huvud taget kunna verifiera sina referenser. **Beroendekartan måste visa vad som är auktoritativt och vad som kan rekonstrueras, inte bara vilka tjänster som anropar varandra.**

## 15.3 Välj återställningspunkter som hör ihop

Vid ett avbrott finns ofta flera återställningsalternativ: databasens senaste konsistenta PITR-punkt, en volymsnapshot, en bevarad händelselogg eller en annan regions replik. Inget av dessa utgör automatiskt en gemensam konsistent ögonblicksbild av hela systemet.

Återvänd till E-417. Ärendet skapades 08.06, en handläggningsuppgift bildades 08.07 och ett externt svar togs emot 08.09. Om ärendetjänsten återställs till 08.05 men handläggningstjänsten till 08.08 finns ett föräldralöst uppdrag. Om allt återställs till 08.05 kan svaret från omvärlden ändå inte göras ogjort.

Återställningsteamet behöver då pröva minst följande frågor i sak: Vilka händelser har nått vilka konsumenter? Vilka positioner och dedupliceringsmarkörer följer med återställda databaser? Är journalen eller händelsehistoriken tillräcklig för att återspela förlorad intern behandling? Vilka externa transaktioner måste stämmas av och vilka är osäkra?

Ibland går det att välja en logiskt sammanhängande skärning av de interna tillstånden. I andra fall är det bättre att ta tillbaka en äldre teknisk kopia och sedan *reparera framåt* genom återspelning och avstämning. En möjlig återställningspunkt i varje komponent är alltså bara råmaterial; den beslutade återställningsgränsen gäller ett verksamhetsförlopp.

## 15.4 Failover kan sprida fel om den sker för snabbt

Automatisk överkoppling från en region till en annan kan minska avbrottstiden, men synkroniserad felaktig data, försenad replikering, gamla klientanslutningar och dubbla aktiva producenter kan göra utfallet farligt. En replik är inte en historiskt oberoende backup. Den kan redan ha tagit emot korruption eller oönskad radering.

Tänk att reservregionen blir aktiv medan den gamla miljön fortfarande kan publicera meddelanden. Båda regionerna kan då genomföra samma verksamhetsoperation. Arkitekturen behöver ett kontrollerat ägarskapsbyte: exempelvis fencing, tidsbegränsade ledarskapsrättigheter eller annan mekanism som förhindrar att tidigare ägare fortsätter skriva. DNS-ändring ensam garanterar inte detta; långlivade anslutningar kan dröja kvar.

RPO och RTO måste därför verifieras med verkliga prov där fel uppstår vid ogynnsamma tidpunkter, inte enbart utifrån replikeringens normala fördröjning och hur snabbt en container startar.

## 15.5 Återstarten sker i kontrollerade steg

En användbar återöppning kan ha följande kontrollpunkter:

1. **Stabilisera och isolera:** Stoppa inkommande skrivningar eller dirigera dem till ett dokumenterat kö-/stoppförfarande. Kontrollera att den gamla miljön inte längre kan agera som aktiv producent.
2. **Återskapa beroenden:** Återställ åtkomst, nycklar, nät, övervakning och beständiga datakällor. Verifiera integriteten för valda återställningspunkter.
3. **Avgränsa händelseflödet:** Dokumentera brokerpositioner, konsumentmarkörer, outbox-köer och eventuella okända operationer. Pausa de konsumenter som ännu inte säkert får fortsätta.
4. **Avstäm tillstånd:** Jämför auktoritativa poster och härledda data, identifiera luckor och dubletter och reparera dem med avsiktligt valda metoder.
5. **Återöppna stegvis:** Tillåt exempelvis läsning före nya registreringar och registreringar före irreversibla externa utskick. Övervaka fel, eftersläpning och avvikelser.
6. **Besluta om normaldrift:** Dokumentera återstående osäkerheter och vem som accepterar dem. Behåll möjlighet att stoppa flödet igen.

Detta är en principsekvens, inte ett färdigt körschema. Kapitel 17 behandlar hur sekvensen omsätts i en operativ återställningsplan med ansvar, beslut och kommunikation.

## 15.6 Mät återställd förmåga, inte bara uppstart

För att säga att E-417 kan hanteras igen räcker inte ett HTTP 200 från varje tjänst. Ett prov behöver visa att ett nytt ärende får en enda handläggningsuppgift, att tidigare expedierade beslut inte skickas om, att bilagor är åtkomliga och att en stannad konsument kan arbeta ikapp utan att skapa dubletter. Avvikelseköer och outbox-eftersläpning ska ha begripliga nivåer och en ägare.

En särskilt värdefull DR-övning är att låta ett fel inträffa just när ett meddelande har publicerats men mottagarens kvittens ännu inte är säker. Det är i dessa mellanlägen som systemets verkliga återställningsbarhet syns.

**Slutsatsen:** Ett återställningsbart systemlandskap är inte det där varje komponent kan startas snabbast, utan det där verksamheten kan återupptas med kända, kontrollerade och accepterade konsekvenser. Nästa kapitel skärper villkoren ytterligare: tänk om vi inte kan lita på den miljö eller den backup som ska återställas?

## 15.7 Ett regionalt haveri – återställning i beslutade faser

**08.12 – Stopp och isolering.** Primärregionen upphör att svara. Incidentledaren beslutar att nya skrivningar stoppas även i potentiella reservanslutningar tills det är klarlagt om den ursprungliga miljön fortfarande kan ta emot trafik. Inkomna integrationer sätts i kontrollerat vänteläge, och externa parter får besked om hur leveranser ska hanteras under avbrottet. Det förhindrar att automatiserad failover skapar två konkurrerande sanningskällor.

**08.25 – Skapa en verifierbar lägesbild.** Databasansvarig redovisar senast återställningsbara punkt för varje auktoritativ databas. Plattformsteamet redovisar nycklar, konfiguration och nätverksberoenden. Integrationsansvarig kartlägger vilka meddelanden som kvarstår och vilka externa expedieringar som kan ha genomförts efter respektive databas återställningspunkt. Tiderna bildar inte en enda global tidpunkt: avvikelserna registreras uttryckligen.

**08.40 – Etablera återställningsmiljö.** Reservregionen får körplattform, identiteter och tillgång till rätt containeravbilder. Databaser och objekt återläses i isolerade resurser. Utgående konsumenter och notifieringsfunktioner hålls avstängda. Hälsokontroller visar nu om infrastrukturen fungerar, men de används inte som beslut om att verksamheten får öppna.

**09.10 – Avstäm verksamhetstillstånd.** För E-417 finns beslutshändelsen i en outbox, men ärendets status har återgått till ”under handläggning”. Den externa parten bekräftar att beslutet redan mottagits. Teamet markerar att beslutet inte ska skickas igen, återställer intern spårbarhet genom en godkänd korrigerande åtgärd och dokumenterar avvikelsen. Ärenden utan tillförlitlig extern bekräftelse spärras för automatisk expedition, medan övriga kan fortsätta.

**09.35 – Stegvis öppning.** Först öppnas läsning och sökfunktioner. Därefter aktiveras en begränsad konsumentgrupp med övervakning av dubbelbehandling och uteblivna händelser. Till sist öppnas nyregistrering och externa utskick efter ett uttryckligt verksamhetsbeslut. Vid avvikelse finns dokumenterade stoppvillkor, exempelvis okända externa utfall eller ett ökande antal oavstämda ärenden.

Tiderna är fiktiva och beskriver ordning, inte generella RTO-löften. De gör däremot något viktigt synligt: **tiden till grön infrastruktur och tiden till godkänd verksamhetsdrift är två olika mätvärden**.

## 15.8 När automatiken ska stoppas

Automatisk failover passar väl när den kan garanteras inte ge konkurrerande skrivningar och när data- och beroendekontrakten stöder växlingen. Men vid partiell informationsförlust eller oklart externt utfall kan snabb återstart förvärra skadan. En mogen plan innehåller därför särskilda spärrar för publicering, konsumentstart och externa affärshandlingar; tydliga mandat för att lyfta spärrarna; och en avvikelselista som kan hanteras utan att hela systemet hålls stängt.

Ett konkret beslut kan vara att läsfunktioner får öppnas när databasintegritet är kontrollerad, medan externa beslut kräver en avstämd kvittenslista. Det är inte ineffektivitet utan en avsiktlig uppdelning mellan säker kapacitet och osäker kapacitet. Först när dessa gränser är uttalade kan återställningsordningen automatiseras på ett ansvarsfullt sätt.
