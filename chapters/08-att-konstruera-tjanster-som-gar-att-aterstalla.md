# 8. Att konstruera tjänster som går att återställa

Handläggningstjänsten läser `ÄrendeRegistrerat` för E-417 och skapar arbetsuppgiften. Databasen bekräftar ändringen. Just då kraschar tjänsten, innan den hunnit kvittera meddelandet. Efter omstart skickar meddelandeförmedlaren samma händelse igen.

Har tjänsten nu ett problem med sin backup? Nej. Det som saknas är en **säker metod för att upprepa en operation vars tidigare resultat är osäkert**. Den egenskapen blir särskilt viktig vid återställning, när tjänster återgår till olika versioner av sitt lokala tillstånd och äldre meddelanden kan återkomma.

## 8.1 Vad betyder idempotens i praktiken?

En operation är idempotent om en upprepning med samma avsedda identitet inte skapar ytterligare verksamhetseffekt. Det betyder inte att servern måste lämna samma tekniska svar i varje situation eller att upprepningen är gratis.

För ärendehändelsen vill vi att två leveranser av samma unika händelse inte skapar två arbetsuppgifter. Vi vill däremot kunna hantera två *olika* händelser om samma ärende. Att bara använda ärende-ID som dedupliceringsnyckel kan därför vara fel: `ÄrendeRegistrerat` och `ÄrendeKompletterat` behöver kunna behandlas var för sig.

En beständig händelseidentitet, kombinerad med mottagarens behandlingstyp eller konsumentidentitet när det behövs, är ofta bättre. Nyckeln måste vara stabil över återleverans och återstart, och samma identitet får inte återanvändas för en annan avsedd operation.

## 8.2 Det kritiska ögonblicket mellan kontroll och skrivning

En naiv implementation frågar först om meddelandet har behandlats och skapar därefter arbetsuppgiften. Två konsumentinstanser kan samtidigt få svaret nej och båda skapa en uppgift.

En robust lokal design kräver därför att unikhetskontrollen och affärsändringen skyddas atomärt. Med en relationsdatabas kan det ske med en unik constraint och en gemensam transaktion. Förenklat kan logiken uttryckas så här:

```sql
BEGIN;

INSERT INTO processed_message (consumer, event_id)
VALUES ('handlaggning', :event_id)
ON CONFLICT DO NOTHING;

-- Skapa arbetsuppgiften endast om raden faktiskt infogades
-- och genomför ändringen i samma databastransaktion.

COMMIT;
```

SQL-utdraget visar principen, inte en komplett körbar konsument. Applikationen måste kontrollera om raden infogades och bara då utföra affärsändringen. Om transaktionen rullas tillbaka får varken markören eller arbetsuppgiften finnas kvar. Om den genomförs finns båda kvar. En unik begränsning är nödvändig för att konkurrerande konsumenter inte ska kunna passera kontrollen samtidigt.

**Aha-punkten:** Den beständiga kunskapen om *vad tjänsten redan har gjort* är lika viktig som den beständiga kunskapen om *vad tjänsten vet*. Om vi återställer arbetsuppgiften men inte motsvarande dedupliceringsmarkör — eller tvärtom — kan upprepningen bli fel.

## 8.3 Kvittera först när arbetet verkligen är säkrat

Vid köbaserad behandling finns normalt en kvittens eller en offset-position. Om meddelandet kvitteras innan lokal affärstransaktion är säkert genomförd finns risk att arbetet går förlorat vid krasch. Om det kvitteras efter commit kan samma meddelande komma tillbaka efter en krasch mellan commit och kvittens.

Den senare ordningen väljs ofta tillsammans med idempotent behandling: hellre att meddelandet kan levereras igen än att en obekräftad affärsändring tyst går förlorad. Det är emellertid ingen automatisk garanti för exakt-en-gång-effekt i andra databaser eller externa system. Produktens kvittensmodell, durable-konfiguration och felvägar måste kontrolleras.

Mottagarens beständiga behandlingsposition måste också tåla återställning. Om databasen återställs till en äldre tidpunkt men konsumentpositionen förblir senare kan förlorat arbete aldrig läsas om. Om positionen återställs längre bak upprepas arbete, vilket idempotensmekanismen måste tåla. Därför måste data och bearbetningsmarkörer ingå i samma återställningsresonemang.

## 8.4 Tre möjliga utfall vid ett osäkert avbrott

För en operation som stoppas mitt i behandlingen finns tre logiska lägen:

1. **Ingen beständig effekt:** Behandla om när händelsen återkommer.
2. **Beständig effekt och markör:** Identifiera återleveransen som redan genomförd.
3. **Okänt utfall utanför den lokala transaktionen:** Gör ingen blind repris; fråga den externa parten eller använd en dokumenterad avstämningsprocess.

De två första kan en välkonstruerad lokal transaktion hantera. Den tredje uppstår exempelvis när en tjänst anropar ett externt beslutssystem, får timeout och inte vet om mottagaren genomförde operationen. Idempotens på den egna databasen ger då inte ensam korrekthet i omvärlden. Vi behöver idempotensnycklar även i integrationskontraktet, eller en möjlighet att läsa tillbaka resultatet från mottagaren.

## 8.5 Återstartbar bearbetning i större arbetsflöden

Vissa jobb omfattar tusentals objekt och kan inte köras i en enda transaktion. Då behövs verifierbara kontrollpunkter. Ett importjobb kan till exempel registrera ett jobb-ID, version av indata och en beständig uppgift om vilka objekt som redan har genomförts.

Det räcker inte att spara ”rad 850 klar” om källfilen kan ha ändrats sedan första körningen. Då kan radnumret avse annan information. Återstartskontraktet behöver en beständig referens till just den indata som bearbetas, och resultatet för varje delsteg behöver kunna återfinnas.

Felhantering bör också skilja mellan tillfälliga fel som får försökas igen, permanenta valideringsfel som kräver rättning och okända externa utfall som kräver avstämning. Obegränsade retries kan förstärka skador, överbelasta beroenden och försvåra rekonstruktionen. Backoff, dead-letter-hantering och mänsklig åtgärd måste ha tydliga gränser.

## 8.6 Återställningskontrakt på tjänstenivå

En tjänst som ska kunna återställas bör kunna besvara dessa frågor med verifierbara uppgifter: Vilket tillstånd äger den? Vilka indata går att återskapa? Vilka identifierare förhindrar dubletter? Vad lagras tillsammans atomärt? Hur återupptas behandling efter en krasch? Vilka externa bieffekter kan inte ångras?

En tänkt katalogpost för handläggningstjänsten kan ange att databasen är auktoritativ för arbetsuppgifter, att mottagna händelse-ID lagras i samma transaktion som varje ny uppgift och att meddelanden kvitteras först efter lyckad commit. Den kan också ange att historiska händelser får återlevereras inom en definierad retention och att återstart testas genom att processen dödas i de kritiska tidsfönstren.

Vi har därmed gått från att hoppas att tjänsten ”startar igen” till att kunna visa *vad omstart betyder*. Nästa kapitel tar hand om den symmetriska risken hos den som **skickar** händelsen och binder ihop producentens och konsumentens garantier.
