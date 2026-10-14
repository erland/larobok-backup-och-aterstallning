# 11. Integrationer med omvärlden

Beslutet för E-417 har fattats och skickats till en extern mottagare. Den egna tjänsten får timeout. Har beslutet kommit fram? Har mottagaren behandlat det? Svaret finns inte i avsändarens databas. Det kan finnas hos mottagaren – och samma sak gäller om vår egen miljö därefter återställs till en punkt före sändningen.

Det här kapitlet utgår från insikten i kapitel 10: ett osäkert utfall får inte behandlas som ett misslyckande utan vidare. Vi undersöker hur arkitektur och integrationsavtal kan göra externa effekter spårbara och möjliga att stämma av.

## 11.1 Den egna återställningspunkten stoppar inte omvärldens tid

En intern backup från 10.00 kan vara tekniskt felfri. Men klockan 10.03 tog ett annat system emot ett beslut, bokförde en transaktion eller skickade ett meddelande. När vi återställer den egna databasen till 10.00 följer inte omvärlden med bakåt.

Det betyder att två helt olika frågor måste få olika svar:

- **Vilken information kan vi återställa lokalt?** Här hjälper backup, loggar och intern rekonstruktion.
- **Vilken handling har faktiskt utförts hos någon annan?** Här behöver vi kvittenser, avläsningsbara statusar, mottagarens historik eller särskild avstämning.

Arkitekturen får inte blanda samman *inte registrerat hos oss* med *inte utfört hos dem*. Just den sammanblandningen orsakar många riskfyllda återförsök efter haverier.

## 11.2 Begäran, mottagning och verkställighet är skilda händelser

En teknisk HTTP 200 eller en kökvittens kan betyda att en begäran mottagits. Den bevisar inte generellt att den avsedda affärshandlingen är slutligt genomförd. Olika integrationskontrakt har olika garantier. Ett stabilt protokoll bör därför skilja mellan exempelvis:

1. **Begäran skapad** – vår tjänst har en beständig avsikt att göra något.
2. **Begäran överförd eller tekniskt mottagen** – transporten har gett en verifierbar signal.
3. **Begäran accepterad** – mottagaren har godkänt den för behandling.
4. **Åtgärd verkställd eller avslagen** – verksamhetsutfallet är känt.

Alla integrationer behöver inte fyra separata svar. Men den faktiska innebörden av varje kvittens ska dokumenteras. Saknas en slutlig kvittens måste det finnas ett annat sätt att fastställa utfallet.

För E-417 kan avsändaren ha lagrat att ett distributionskommando skickades. Mottagaren kan ha accepterat kommandot men ännu inte expedierat beslutet. En blind repris kan då orsaka en dubblett eller ett andra utskick när det första slutförs.

## 11.3 Ett idempotenskontrakt över organisationsgränsen

Det starkaste praktiska skyddet mot osäkra återförsök är ofta att båda parter delar en stabil operationsidentitet. Avsändaren skickar samma idempotensnyckel vid varje försök som avser **samma avsedda handling**. Mottagaren kan då identifiera upprepningen och returnera eller hänvisa till tidigare registrerat utfall, inom ett dokumenterat giltighetsfönster.

Detta kontrakt måste vara konkret. Det ska bland annat ange vilka operationer som stöder idempotens, hur länge nycklarna sparas, hur begärans innehåll kopplas till nyckeln, och vad som händer när mottagaren fortfarande bearbetar den första begäran. Nycklar kan inte antas sparas för evigt. Inte heller kan avsändaren räkna med att alla externa tjänster erbjuder en sådan funktion.

Om nyckeln har försvunnit ur mottagarens lagring efter en tidsgräns kan en långt senare återställning skapa en ny effekt även med samma identifierare. Därför behöver återställningsplanen innehålla gränser för när automatisk omleverans är tillåten och när status måste stämmas av först.

## 11.4 Vad gör vi när resultatet är okänt?

Anta att anropet `expediera(E-417, operation-92)` gav timeout. Efter återstart finns den ursprungliga avsikten kvar, men ingen slutlig kvittens. Ett säkert förfarande kan vara:

1. **Pausa nya försök** för just operationen medan utfallet är oklart. Andra oberoende ärenden kan fortsätta enligt ordinarie regler.
2. **Sök status hos mottagaren** med samma operations-ID, affärsnyckel eller kvittensreferens.
3. **Jämför uppgifterna** med den egna historiken: vad begärde vi, vad accepterades och vilken faktisk effekt registrerades?
4. **Besluta nästa handling:** markera bekräftat utfall, gör ett säkert återförsök enligt kontraktet eller eskalera för manuell utredning.
5. **Registrera avstämningen** som ett spårbart beslut med källreferens, tidpunkt och ansvar.

Om det saknas tekniskt status-API kan avstämningen ske genom regelbundna avräkningsfiler, mottagarjournaler eller manuell kontakt. Poängen är densamma: ett okänt utfall ska göras synligt och utredningsbart, inte döljas genom upprepade anrop.

## 11.5 Olika integrationsformer kräver olika bevis

En synkron API-integration kan lämna svar direkt men ändå ha osäkra effekter vid timeout. En asynkron köintegration ger ofta separata tekniska och affärsmässiga kvittenser. En filintegration kan behöva fil-ID, checksumma, versionsbeteckning, manifest och en separat mottagnings- eller bearbetningskvittens. Batchöverföring med tusentals poster kräver ofta avstämning på **postnivå**, inte bara ett ”fil mottagen”.

För integrationer där resultatet får rättslig eller ekonomisk betydelse kan revisionsspår, diarienummer, tidsstämplar och oföränderliga kvittenser behöva följa verksamhetens informationshanteringsregler. Arkitekturen måste ge stöd för spårbarhet och rättelse, men detaljerade bevarande- och rättsliga krav är verksamhets- och jurisdiktionsberoende.

En praktisk integrationsbeskrivning bör därför redovisa om avsändning, mottagning och verkställighet går att verifiera var för sig; vilka identifierare som överlever återställning; och vem som har auktoritet att avgöra ett motstridigt utfall.

## 11.6 Återstart i rätt ordning

Efter ett större driftavbrott är det lockande att starta alla konsumenter och publicerare så snabbt som möjligt. Men återställda outbox-poster och gamla meddelanden kan då ge en våg av dubletter mot omvärlden. För integrationer med känsliga effekter behöver återstarten styras.

En typisk ordning är att återställa interna tjänster och deras beständiga markörer, inventera utgående operationer med osäkert utfall, säkra kontaktvägar för statusfrågor, genomföra nödvändig avstämning och först därefter gradvis släppa på utskick eller konsumenter. Det är en **riskstyrd ordning**, inte en universell driftrutin; vissa system kan behöva ta emot nya ärenden medan gamla utgående flöden fortfarande är pausade.

Återställningsövningar bör även pröva gränsfall: samma meddelande före och efter återläsning, en kvittens som kommer mycket sent, ett försvunnet idempotensfönster och ett faktiskt dubbelt externt utfall. Målet är inte att varje fel ska kunna korrigeras automatiskt, utan att inga osäkra situationer får passera obemärkt.

## 11.7 Arkitekturarbete som behöver göras före haveriet

För varje kritisk extern integration bör vi kunna peka på ett avtal eller designbeslut som anger: stabila korrelations- och operations-ID:n; vilka kvittenser och statusfrågor som erbjuds; idempotensens räckvidd och livslängd; hur kompensation eller rättelse sker; vilken part som ansvarar för avstämning; samt hur man öppnar flödet igen efter återställning.

När detta saknas blir återställningen beroende av gissningar och personkunskap. När det finns kan drift och verksamhet arbeta tillsammans utifrån tydliga bevis. Det är därför **återställningsförmåga måste designas också i integrationskontrakten**, inte bara i de egna databaserna.

Kapitlen 10 och 11 kompletterar nu bilden: verksamhetsflödet måste kunna återupptas från sitt verkliga tillstånd, och externa handlingar måste kunna verifieras utan att systemet försöker skriva om det som redan hänt. I nästa kapitel samlas lärdomarna till praktiska arkitekturprinciper.
