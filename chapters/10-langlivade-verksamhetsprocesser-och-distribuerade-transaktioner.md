# 10. Långlivade verksamhetsprocesser och distribuerade transaktioner

Ett ärende kan pågå i veckor. Det registreras, kontrolleras, kompletteras och avgörs. Under tiden arbetar olika tjänster, och en extern aktör kan redan ha tagit emot information. Om systemet stannar mitt i flödet går det inte att hantera processen som en enda databastransaktion: flera steg har redan genomförts och blivit synliga.

I kapitel 8 och 9 såg vi hur enskilda meddelanden kan behandlas och publiceras säkert. Här flyttas perspektivet från **en tillförlitlig operation** till **en sammanhängande verksamhetsprocess**. Frågan är inte bara om ett steg utförts utan vilket nästa steg får vara efter en återställning.

## 10.1 En verksamhetsprocess är inte en lång databastransaktion

För ärende E-417 kan flödet beskrivas så här:

1. Ärendet registreras hos ärendetjänsten.
2. En kontrolltjänst begär uppgifter från ett externt register.
3. Handläggningstjänsten tar emot ett svar och förbereder ett beslut.
4. Beslutstjänsten fattar beslutet och publicerar resultatet.
5. En distributionstjänst skickar beslutet vidare.

Varje lokalt steg kan lagras atomärt i sin tjänst. Men mellan stegen finns tidsfördröjningar, nätverksfel och självständiga databaser. En global ACID-transaktion som hålls öppen genom hela handläggningen vore varken realistisk eller önskvärd. Ett ärende kan också legitimt invänta mänsklig handläggning eller svar från en tredje part.

Det här är **inte** ett argument för att alla distribuerade system måste använda Saga. En enkel process kan hanteras med ett fåtal robusta händelser och tydliga lokala ansvar. Men när flera beroende steg måste slutföras eller kompenseras behövs ett explicit processkontrakt.

## 10.2 Saga: en följd av lokala transaktioner

*Sagamönstret* organiserar ett verksamhetsflöde som en följd av lokala transaktioner. När ett steg har genomförts initieras nästa. Om ett senare steg misslyckas beslutar processen om den ska försöka fortsätta, kompensera redan genomförda steg eller överlämnas till manuell hantering.

En **kompensation** är inte en teknisk rollback till ett äldre databastillstånd. Det är en ny verksamhetshandling som syftar till att hantera följderna av den tidigare handlingen. Om en plats reserverats kan reservationen frisläppas. Om ett utkast har registrerats kan det markeras som återkallat. Ett redan expedierat myndighetsbeslut eller en redan genomförd utbetalning kan däremot kräva ett formellt ändringsbeslut eller en separat mottransaktion. Historiken ska normalt inte suddas ut.

Skillnaden mellan tre utfall är central:

| Utfall | Återhämtningsbeslut | Exempel |
|---|---|---|
| Tillfälligt tekniskt fel | Fortsätt framåt genom säkert återförsök | Registertjänsten svarar inte just nu |
| Verksamhetsregel stoppar fortsatt flöde | Kompensera där det är meningsfullt | Underlaget uppfyller inte kraven; släpp tillfällig reservation |
| Okänt resultat eller oåterkallelig handling | Pausa och stäm av innan nästa åtgärd | Beslut skickades men kvittens saknas |

Att automatiskt kompensera efter varje timeout är alltså farligt: timeout betyder inte nödvändigtvis att ett steg misslyckades. Återförsök är lika riskabelt om operationen inte har ett säkert idempotenskontrakt.

## 10.3 Orkestrering och koreografi

I en **orkestrerad Saga** håller en samordnare reda på processtillståndet: nästa steg, väntande svar, tidsgränser och kompensation. Den kan exempelvis registrera att E-417 väntar på registerkontroll och senare att beslut får expedieras. Fördelen är en synlig processmodell och ett naturligt ställe att styra återstart och avvikelser. Nackdelen är ytterligare en viktig komponent vars beständiga tillstånd och tillgänglighet måste skyddas.

I en **koreograferad Saga** reagerar tjänster på varandras händelser utan en central processledare. Det kan ge lösare koppling och fungera väl för korta, enkla förlopp. När antalet aktörer, alternativa vägar och kompensationer ökar kan det bli svårt att se vem som ansvarar för processens slutresultat. Då behövs ofta särskild korrelation, processövervakning och avvikelsehantering även utan orkestrator.

Valet bör grundas på processens komplexitet och kontrollbehov, inte på en förmodan att händelsedriven arkitektur alltid kräver koreografi. Båda alternativen förutsätter beständiga händelser eller processtillstånd och säkert återupptagande efter avbrott.

## 10.4 Vad måste sparas för att en process ska gå att återuppta?

När en Saga ska återställas måste vi kunna skilja mellan *planerad*, *påbörjad*, *bekräftad* och *osäker* handling. För varje viktig operation kan processen behöva lagra:

- stabilt process- och ärende-ID, plus en unik identitet per kommando;
- processens tillåtna tillstånd och aktuell stegversion;
- vilka lokala steg som bekräftats och vilka externa kvittenser som finns;
- tidsgränser, väntande svar och eventuella försök att kompensera;
- referenser som krävs för efterföljande avstämning och mänskligt beslut.

Om samordnarens databas återställs till 10.00 medan beslutstjänsten genomförde sitt steg 10.03 får samordnaren **inte** reflexmässigt ge ett nytt beslutskommando. Först måste den hämta vad som faktiskt hände, med samma process- och operationsidentiteter som tidigare. Detsamma gäller koreografi: en sent återlevererad händelse får inte skapa en andra giltig verksamhetstransition.

En explicit tillståndsmaskin kan göra dessa regler begripliga. Exempel: `REGISTRERAD → KONTROLLERAS → BESLUTAD → EXPEDIERAD`, men med `UTFALL_OKÄNT` och `KRÄVER_AVSTÄMNING` som särskilda tillstånd. De sistnämnda är inte tekniska felkoder som får gömmas i loggar, utan verkliga tillstånd som påverkar vad verksamheten får göra.

## 10.5 Kompensation kräver verksamhetskunskap

Anta att kontrollen av E-417 underkänns efter att en preliminär handläggningsuppgift har skapats. En tillräcklig kompensation kan vara att stänga arbetsuppgiften med orsaken ”kontroll ej godkänd”. Vi bör inte radera uppgiften och låtsas att den aldrig funnits, om spårbarhet krävs. Om ett beslut redan kommunicerats är en administrativ upphävandeprocess något annat än att återställa ett fält från `BESLUTAD` till `UTKAST`.

Kompensationen kan i sin tur misslyckas. Då behövs återförsök, eskalering och ett bevarat spår av misslyckandet. Samtidiga processer kan också läsa ett mellanläge; Saga ger inte automatiskt samma isolering som en lokal databastransaktion. Temporära statusar, versionskontroller och affärsregler som hindrar otillåtna sidoprocesser kan därför behövas.

Det är här arkitektens och verksamhetens ansvar möts. Teknisk kod kan utföra en kompensation, men kan sällan ensam avgöra om den är verksamhetsmässigt eller rättsligt riktig.

## 10.6 Återställningsövningen som visar om designen håller

Prova tre haverier mot E-417. Först försvinner processmotorns tillstånd efter att ett lokalt steg genomförts; den ska hitta det genomförda steget och fortsätta utan dubbel effekt. Sedan misslyckas ett steg som är kompensationsbart; kompensationen ska synas som en ny, spårbar åtgärd. Slutligen får ett externt anrop timeout vid en oåterkallelig handling; processen ska stanna i ett kontrollerat osäkerhetsläge, inte gissa.

En lyckad övning verifierar inte bara att tjänsterna startar. Den visar att inget ärende tyst blir liggande, att inga otillåtna dubbla handlingar uppstår och att avvikelser går att förstå och avhjälpa.

**Kapitlets slutsats:** En distribuerad process måste kunna *fortsätta från det tillstånd som faktiskt uppnåtts*, inte från den punkt vi önskar att alla tjänster hade haft. Nästa kapitel fokuserar på den svåraste gränsen för detta: system vi inte själva kontrollerar.

## 10.7 Ett processkort med uttryckliga kompensationsgränser

För E-417 kan processen modelleras som `Registrerat → UnderlagKontrollerat → BeslutFastställt → Expedierat`. Varje steg har ett eget beständigt resultat och en ansvarig tjänst. Om kontrollen misslyckas före fastställt beslut kan systemet ofta återgå till väntande komplettering. Om beslutet redan expedierats är det däremot missvisande att beskriva en kompensation som en rollback: mottagaren kan redan ha agerat på uppgiften.

En återstartad processmotor behöver därför fatta ett av tre slag av beslut: *fortsätt* från senast verifierat steg, *kompensera* med en explicit ny affärshändelse, eller *pausa för manuell avstämning*. En övergång till `KompensationBegärd` är inte detsamma som `Kompenserad`; även kompensationen kan misslyckas eller vara försenad. Varje ny handling måste kunna spåras till det ursprungliga steget och ha egen idempotensidentitet.

| Verifierat läge | Tillåten åtgärd efter återställning | Förbjudet antagande |
|---|---|---|
| Kontroll av underlag klar, beslut saknas | Återuppta beslutssteget | Att hela processen måste startas om |
| Beslut fastställt, expediering ej påbörjad | Fortsätt expediering med stabil operationsnyckel | Att det gamla beslutet får skapas på nytt |
| Expedieringsanrop skickat, kvittens saknas | Fråga mottagaren och parkera vid okänt svar | Att timeout betyder att anropet inte utförts |
| Mottagaren bekräftar expedition | Markera expedierat och fortsätt nästa steg | Att en återläst äldre status motiverar ny expedition |

Tabellen visar varför processen behöver en beständig tillståndsmodell med tillåtna övergångar, inte en serie löst kopplade återförsök.
