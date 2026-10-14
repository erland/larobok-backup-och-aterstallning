# 18. Testning och verifiering av återställningsförmåga

Det är en sak att ha en återställningsplan som ser rimlig ut. Det är en annan att visa att den fungerar när systemet kraschar mellan två kritiska operationer. En övning där man återläser en databas och får en grön hälsokontroll visar att vissa tekniska steg fungerar. Den visar inte att E-417 förblir ett enda ärende, att beslut inte skickas dubbelt eller att den externa mottagaren och den interna historiken är överens.

En återställningsförmåga bör därför bedömas utifrån **observerbara verksamhetsresultat efter ett definierat fel**, inte enbart utifrån att backupjobbet lyckades.

## 18.1 Vad måste proven faktiskt visa?

Varje återställningsprov behöver ett uttryckligt påstående som kan falsifieras. Exempelvis: ''Efter en krasch mellan lokal databas-commit och brokerkvittens finns exakt en arbetsuppgift för händelsen E-417 och meddelandet kan säkert återlevereras.''

Ett användbart testfall innehåller fel som injiceras, inledande tillstånd, vilka återställningskällor som får användas, tidsgräns, förväntade dataposter och observerbara resultat. Ange också om testet omfattar intern konsistens, extern avstämning eller full verksamhetsåteröppning. Utan avgränsning kan ett godkänt tekniskt delprov felaktigt rapporteras som godkänd katastrofåterställning.

Krav som RTO och RPO ska mätas på förmågenivå: tiden fram till att definierade verksamhetsflöden fungerar, respektive den faktiska förlusten av information eller arbete som inte kunnat återskapas. Man bör dessutom mäta tiden för avstämning och återhämtning av kö-eftersläpning. I distribuerade system kan dessa dominera efter att infrastrukturen redan är uppe.

## 18.2 Bygg en provtrappa

Börja med återkommande, automatiserade kontroller och öka successivt komplexiteten:

| Nivå | Exempel på prov | Vad det styrker |
|---|---|---|
| Backup- och restoreprov | Återläs databas eller objekt från vald backup, kontrollera integritet | Kopian går att använda för den testade datatypen |
| Tjänsteprov | Avbryt behandling mellan commit och kvittens, återleverera samma händelse | Idempotens och återstartbarhet för en tjänst |
| Flödesprov | Stoppa producent, outbox-publicerare eller konsument vid definierade punkter | Kedjans förmåga att upptäcka och reparera mellanlägen |
| Systemprov | Återställ databaser och kö-/loggpositioner från olika tidpunkter | Avstämning av distribuerade tillstånd |
| Fullständig DR-övning | Återskapa reservmiljö, stäm av externa aktörer och återöppna verksamheten | Beslutsvägar, beroenden och uppmätt återställningsförmåga |

En högre nivå ersätter inte lägre nivåer. Ett sällsynt stort prov hittar andra fel än ett litet test som körs efter varje ändring. Verksamhetskritiska miljöer behöver både kontinuitet och realistisk övning.

## 18.3 Fel på fel sida om en transaktion

För händelsen `ÄrendeRegistrerat` finns särskilt lärorika avbrottspunkter: direkt efter att ärendet och dess outbox-rad skrivits; efter att meddelandet skickats men före markering som skickat; efter att mottagarens arbetsuppgift committats men före kvittens. Det är möjligt att samma händelse levereras flera gånger. Testets godkännandekriterium är därför inte ''endast en leverans'' utan ''ingen dubblerad verksamhetseffekt''.

Provet måste också kontrollera att dedupliceringsinformation och verksamhetsdata följs åt genom återställningen. Om mottagardatabasen backas till en punkt före markören men brokerpositionen ligger kvar senare, kan arbete tappas. Om brokerpositionen backas men markören inte gör det ska återleveransen tolereras. Sådana kombinationer behöver reproduceras avsiktligt.

Det är frestande att använda en enkel felinjektionsmetod som bara dödar en process. Mer realistiska varianter prövar förlorad nätkontakt, fördröjningar, utgångna identitetsuppgifter, otillgänglig nyckelhantering och en meddelandeplattform som återkommer med andra tillgängliga historikpositioner. Prov ska dock utföras i avgränsad miljö eller inom godkända skyddsräcken så att ingen oplanerad verksamhetsskada uppstår.

## 18.4 Ett sammanhängande övningsscenario

I övningen ''E-417 efter regionbortfall'' startar vi med ett registrerat ärende, en skapad arbetsuppgift och ett externt beslut som kan vara expedierat. Simulera att primärmiljön försvinner strax efter att beslutsanropet skickats. Reservmiljön innehåller äldre intern data, medan den externa testmottagaren behåller resultatet.

Övningsledningen ger inte teamet facit om beslutets utfall. Teamet ska upptäcka osäkerheten, säkra korrelations-ID, söka resultat hos testmottagaren och välja avstämning framför blind återleverans. Därefter ska det öppna registrering för nya ärenden utan att oavsiktligt återöppna de spärrade beslutsutskicken.

Övningen godkänns först när flera belägg finns samtidigt: återställningspunkterna är dokumenterade, E-417 har ett förklarligt och spårbart tillstånd i alla relevanta system, testmottagaren har inte fått ett extra beslut, nya ärenden fungerar enligt avtalat öppningsläge och beslutet om normaldrift har fattats av utsedd ansvarig. Faktiska tider och dataförluster jämförs med målen.

Här framträder skillnaden mellan **att genomföra en återställning** och **att visa att den blev korrekt**. Ett team kan följa varje steg i en runbook och ändå misslyckas om kriterierna är felaktiga eller ofullständiga.

## 18.5 Testdata, evidens och externa parter

En testmiljö med verkliga integrationer kräver särskild försiktighet. Automatiserade tester ska som huvudregel använda avgränsade testmottagare, syntetiska identiteter och förutsägbara bieffekter. Att återspela produktionshändelser till verkliga mottagare kan ge oavsiktliga utskick eller transaktioner, även om de avser gamla händelser.

Samla tillräcklig evidens för att kunna bedöma utfallet: loggar med korrelations-ID, event- och aggregate-ID, backupidentifierare, offsets eller motsvarande positioner, jämförelser av affärsobjekt samt tidpunkter för beslut och öppning. Evidensen ska hanteras med relevant åtkomstskydd och dataminimering. Övningen behöver också dokumentera vad som *inte* gick att verifiera, till exempel ett externt system som inte tillhandahåller återläsning av transaktionsstatus.

Övningar med en integrationspart bör på förhand definiera hur parterna spärrar testtrafik mot produktion, hur status efterfrågas, vem som får ge kvittens och hur man hanterar ett avbrutet test. Att ett gränssnitt returnerar ett tekniskt lyckat svar är inte alltid likvärdigt med att en verksamhetshändelse verkställts.

## 18.6 Från testresultat till bättre arkitektur

Efter varje övning bör avvikelser klassificeras: saknad återställningskälla, otillräcklig retention, oklar tillståndsägare, brist på idempotens, okänt externt utfall, ogenomförbar runbook eller otillräckligt mandat. Åtgärderna måste få en teknisk eller verksamhetsmässig ägare och ett omprov som visar att felet är rättat.

En mätbar förbättring kan exempelvis vara att tiden för att reda ut okända externa beslut minskar genom ett nytt status-API, eller att återuppbyggnadstiden för en projektion minskar genom verifierade snapshots. Det är bättre mått än antal utförda övningar. Övningens värde ligger i **vad organisationen nu vet och kan bevisa**.

Återställningsbarhet är aldrig slutgiltigt verifierad. Nya versioner, integrationer, scheman, retentionstider och tjänsteägare förändrar förutsättningarna. En riskbaserad testportfölj behöver därför ingå i den vanliga förändringsprocessen. När arkitekturen ändras ska även antaganden, runbooks och återställningsprov uppdateras.

Bokens följande kapitel tar upp hur en organisation fördelar det långsiktiga ansvaret för just denna förmåga, så att den inte försvinner mellan utveckling, plattform och verksamhet.

## 18.7 Ett prov som först misslyckas – och därför är värdefullt

Övningen startar med ett känt dataset: tre nya ärenden, varav E-417 har en handläggningsuppgift och ett externt beslutskvitto. Testteamet dokumenterar händelse-ID, förväntade arbetsuppgifter och faktiskt mottagna kvittenser. Därefter återställs handläggningens databas till en punkt före händelsen som skapade uppgiften, medan brokerpositionen lämnas på sitt senare värde.

Det första testresultatet ser lovande ut: databasen går att starta, applikationen svarar på hälsokontroller och backupjobbet har grönt resultat. Men verifieringen mot ärendetjänstens auktoritativa register visar att E-417 saknar arbetsuppgift trots att händelsen `ÄrendeRegistrerat` tidigare har publicerats. Det är inte ett test av backupverktygets förmåga att läsa filer; det är ett test av **tjänstens förmåga att återuppta ett verksamhetsflöde**.

Teamet formulerar en rotorsak: konsumentpositionen förvaras i brokern oberoende av tjänstens lokala databas och återställs inte konsekvent med dess effekt. Att ”starta om igen” kan inte avhjälpa problemet. En åtgärd blir att dokumentera och automatisera identifiering av glapp mellan lokal behandling och tillgänglig händelsehistorik samt återleverera berörda händelser under idempotensskydd. Om tillräcklig händelsehistorik saknas ska testet i stället visa att processen spärras och avvikelser eskaleras, inte att data magiskt återskapas.

Vid omtestet utförs samma felinjektion med samma startdata. Testet får nu lyckat resultat först när E-417 har exakt en arbetsuppgift, övriga ärenden stämmer med källan, inga externa beslut har skickats på nytt och avvikelserapporten visar noll oförklarade fall. Driftteamet visar återställningssteget, utvecklingsteamet visar idempotens- och glappkontrollerna och verksamhetsägaren godkänner affärsutfallet. Det är ett verifierat arkitekturbeteende, inte en demonstration av ett grönt övervakningsinstrument.

## 18.8 Mät det som avslöjar arkitektursvagheter

För varje övning bör resultatet omfatta mätpunkter som kan jämföras över tid: startpunkt för incidenten, tid till återställd teknisk kapacitet, tid till avstämda affärsflöden, uppmätt dataförlust, antal dubbelbehandlade händelser, antal glapp, antal okända externa utfall och antal manuellt korrigerade ärenden. En övning kan vara tekniskt godkänd men verksamhetsmässigt underkänd. Det behöver synas tydligt i rapporten.

Ett praktiskt förbättringsbeslut innehåller en ansvarig tjänsteägare, en ändring i design eller återställningsmetod, ett upprepat testfall och ett sista datum för verifiering. Om testet aldrig körs om är bristen fortfarande öppen. Det är på detta sätt återställningsövningar blir återkommande arkitekturgranskningar.
