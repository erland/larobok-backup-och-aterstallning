# 6. Tidsmässig konsistens mellan tjänster

Klockan 10.00 tar vi en återställningspunkt av ärendetjänsten. Klockan 10.05 tar vi en av handläggningstjänsten. Det låter rimligt: båda kopiorna är lyckade. Men om handläggningstjänstens kopia innehåller en arbetsuppgift som skapades av en registrering efter ärendetjänstens återställningspunkt får vi efter återläsning en arbetsuppgift för ett ärende som inte längre existerar. **Två lokalt korrekta återställningspunkter kan tillsammans beskriva en historia som aldrig har funnits.**

## 6.1 Lokal tid är inte hela berättelsen

Vi använder E-417 igen, nu med fyra händelser:

| Händelse | Tid i exemplet | Konsekvens |
|---|---|---|
| A | 10.02 | Ärendetjänsten lagrar registreringen |
| B | 10.03 | `ÄrendeRegistrerat` blir tillgänglig för handläggningstjänsten |
| C | 10.04 | Handläggningstjänsten lagrar arbetsuppgiften |
| D | 10.06 | Handläggningstjänsten kvitterar sin behandling |

De angivna tiderna illustrerar en ordning i vårt exempel; i verkliga system kan klockor skilja sig åt och loggar få fördröjningar. Det viktigaste är den **kausala relationen**: C förutsätter information från B, och B förutsätter att A har inträffat i den valda designen.

En återställd handläggningsdatabas som innehåller C, medan den återställda ärendedatabasen saknar A, bryter mot denna relation. Det är en motsägelse som en normal databascheck inte behöver upptäcka, eftersom databaserna var för sig uppfyller sina egna begränsningar.

## 6.2 Vad innebär ett konsistent globalt snitt?

Ett sätt att tänka är att varje lokal återställningspunkt utgör ett snitt genom tjänstens egen historia. För att det sammanlagda snittet ska vara *kausalt konsistent* får det inte innehålla en effekt utan att också innehålla den orsak som effekten bygger på. I meddelandesystem betyder det exempelvis att vi inte får inkludera mottagandet av ett meddelande men utesluta motsvarande sändning från den observerade historien.

Det betyder inte att alla tjänster alltid måste återställas till samma väggklocktid. Tjänster som var frånkopplade kan ha haft olika senaste säkra punkter. Och en gemensam väggklocktid är ingen garanti för konsistens när säkerhetskopior tas utan koordinering, då data, loggar och köer inte nödvändigtvis representerar samma logiska ögonblick.

En annan fälla är att likställa kausal konsistens med verksamhetsmässig korrekthet. Ett snitt kan vara kausalt begripligt men fortfarande innehålla ett felaktigt beslut eller sakna en nödvändig extern kvittens. Kapitel 3:s verksamhetskriterier behövs fortfarande.

## 6.3 Meddelanden som befinner sig mitt emellan

Tänk att A finns i den återställda ärendedatabasen och att B skickades strax före avbrottet. Handläggningstjänsten har däremot en äldre återställningspunkt och saknar C. Var är B?

- Om meddelandet finns kvar i broker eller i en beständig, återspelbar logg kan det eventuellt behandlas på nytt.
- Om det levererats och kvitterats i en arbetskö innan handläggningstjänstens äldre databas återställdes kan det vara borta, trots att dess effekt nu också är borta.
- Om det återkommer två gånger måste mottagaren kunna avgöra om effekten redan finns, inte bara anta att varje leverans är ny.

Detta är ett *in-flight-problem*: meddelandets position i ett flöde och mottagarens beständiga tillstånd kan hamna på var sin sida av återställningsgränsen. Lösningen är inte alltid att stoppa alla meddelanden för alltid, men det krävs en medveten strategi för gränsen mellan återställd historik och fortsatt behandling.

## 6.4 Vattenmärken och avstämningsgränser

För vissa system kan man använda en dokumenterad avstämningsgräns: exempelvis att en viss källa har producerat händelser till och med en identifierad sekvens, eller att en konsument har bevisligen behandlat samtliga relevanta händelser till en viss position. Det är mer användbart än att säga ”allt före klockan 10 är klart”, förutsatt att sekvensens semantik verkligen är definierad.

Ett *watermark* kan i olika tekniker beteckna olika saker, särskilt inom strömbehandling med händelsetid och sen ankomst. Det får inte utan vidare tolkas som ett bevis på att samtliga affärstransaktioner före en tidpunkt är varaktigt genomförda. Man måste veta vilka källor, partitioner och konsumenter gränsen omfattar, samt vad som händer med sena meddelanden.

En praktisk avstämning kan kombinera beständiga händelseidentifierare, ursprungliga transaktions-ID, lokalt bekräftade bearbetnings-ID och externa mottagningskvittenser. Utan sådana sammanhängande identiteter kan en jämförelse stanna vid grova tidsstämplar och antal poster. Det ger svaga belägg.

## 6.5 En kontrollerad återöppning

Låt oss anta att ärendetjänstens återställningspunkt är 10.00 och handläggningstjänstens 10.05. Ett ansvarsfullt återställningsarbete skulle inte omedelbart öppna nya registreringar och hoppas att tjänsterna kommer ikapp.

Först måste man fastställa vilka datakällor som är auktoritativa och vilka förändringar som finns efter respektive återställningspunkt. Därefter identifieras berörda ärenden och meddelanden – i synnerhet sådana som enligt det återställda tillståndet saknar sin orsak eller sin effekt. Sedan väljer man en dokumenterad åtgärd per avvikelse: rekonstruera, bearbeta om på ett säkert sätt, avstå från en felaktig effekt eller utreda manuellt.

Medan avstämningen pågår kan nya konsumenter eller integrationer behöva pausas eller köras i ett avgränsat läge. Det handlar inte om ett universellt krav på total nedstängning, utan om att förhindra att okända historiska avvikelser blandas med ny verksamhet. Återöppning beslutas enligt de acceptanskriterier vi beskrev i kapitel 3.

## 6.6 Från tidpunkt till återställningskontrakt

En återställningspunkt är alltså inte bara ett datum och klockslag. För ett distribuerat flöde behöver vi även beskriva vilka händelser som säkert finns kvar, vilka lokala effekter som genomförts, vilka beroenden som återstår och vilka externa handlingar som kan vara oåterkalleliga.

Detta är ingen uppmaning att bygga en global transaktion över allt. I många system är det varken möjligt eller önskvärt. Målet är i stället att kunna redovisa ett *sammanhängande* läge och veta vilka avvikelser som återstår att reparera.

Vi har nu tre byggstenar: var sanningen finns (kapitel 4), hur förändringar förflyttas (kapitel 5) och hur deras ordning påverkar en återställning (detta kapitel). Med den grunden kan nästa kapitel undersöka när tidigare händelser faktiskt kan spelas om för att bygga upp förlorat tillstånd – och när det inte räcker.

## 6.7 Ett genomräknat exempel: kausala snitt är inte klockslag

Tre tjänster samverkar när E-417 registreras: A (ärende), B (handläggning) och C (expediering). Följande tider är illustrativa och klockorna antas vara synkroniserade; poängen gäller även då.

| Tid | Tjänst A | Tjänst B | Tjänst C |
|---|---|---|---|
| 10.01 | Lagrar E-417 och händelse H1 | – | – |
| 10.02 | – | Tar emot H1 och skapar arbetsuppgift | – |
| 10.03 | – | Publicerar H2: klart för expedition | – |
| 10.04 | – | – | Tar emot H2 och registrerar expeditionsavsikt |
| 10.05 | Backup A:s loggposition omfattar H1 | Backup B tas från 10.03 | Backup C tas från 10.04 |

En möjlig kombination av återställningspunkter är A kl. 10.00, B kl. 10.03 och C kl. 10.04. Då finns H1:s följder i B och H2:s följder i C, men själva registreringen i A saknas. Det är ett inkonsistent snitt: effekten har bevarats, men orsaken har försvunnit. Att samtliga tre filer är var för sig korrekta ändrar inte detta.

En annan kombination är A kl. 10.01, B kl. 10.01 och C kl. 10.01. Där finns H1:s källa men ingen mottagning. Den kan vara återställningsbar om H1 fortfarande kan levereras och dess behandling är idempotent. Om H1 har raderats ur förmedlaren och ingen producent-outbox finns kvar blir kombinationen tekniskt konsistent som ögonblicksbild men otillräcklig för att verksamhetsflödet ska slutföras. Det skiljer *konsistens* från *återställningsbarhet*.

En tredje kombination är A kl. 10.01, B kl. 10.03 och C kl. 10.04. Den bevarar hela orsakskedjan, men även då måste vi kontrollera om C hunnit utföra en extern handling efter sin backup. Ett konsistent internt snitt är inte bevis för att omvärlden är avstämd.

## 6.8 Så hittar man en användbar avstämningsgräns

I praktiken finns sällan en knapp för att ta ett perfekt globalt snitt över självständiga tjänster. I stället dokumenterar vi vilka affärshändelser som ska vara inkluderade och vilka spår som visar att deras följder är kända. För E-417 blir frågan inte bara ”vilken tid har databasen?” utan ”finns H1 i A, är den behandlad i B, finns H2 i B och vilken status har den i C och utanför systemet?”.

Det kan kräva en kombination av transaktionsloggposition, outbox-ID, konsumentposition, tjänstens beständiga dedupliceringsmarkör och extern kvittens. Positioner från olika system kan inte jämföras som om de var en enda global sekvens. De är evidens som måste kopplas genom korrelations-ID och orsakssamband.

Om en länk i kedjan är osäker bör de berörda ärendena isoleras från automatisk fortsättning tills avstämningen är klar. Resten av verksamheten kan ofta öppnas stegvis. En exakt global återställningspunkt är därför inte alltid målet; målet är ett kontrollerat, förklarbart tillstånd där saknade eller tvetydiga samband kan identifieras och hanteras. **Ett säkert återstartstillstånd är ett tillstånd vi kan motivera, inte bara tidsstämpla.**
