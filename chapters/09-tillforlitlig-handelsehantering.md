# 9. Tillförlitlig händelsehantering

Ärendetjänsten har lagrat E-417 och ska publicera `ÄrendeRegistrerat`. Om den först skriver till databasen och därefter publicerar meddelandet kan den krascha mellan stegen. Ärendet finns då, men handläggningstjänsten får aldrig veta det. Om vi i stället skickar meddelandet först och skriver databasen sedan kan mottagaren börja arbeta med ett ärende som aldrig blev registrerat.

Detta är **dual-write-problemet**: två självständiga system ska uppdateras som om de vore en operation, trots att de saknar en gemensam lokal transaktion.

## 9.1 En outbox flyttar gränsen

Mönstret *Transactional Outbox* låter ärendetjänsten i en och samma lokala databastransaktion lagra både ärendet och en rad som beskriver den händelse som ska publiceras.

```sql
BEGIN;

INSERT INTO arende (id, status)
VALUES (:arende_id, 'registrerat');

INSERT INTO outbox (event_id, aggregate_id, event_type, payload)
VALUES (:event_id, :arende_id, 'ArendeRegistrerat', :payload);

COMMIT;
```

En separat publicerare läser outbox-poster och skickar dem till meddelandeförmedlaren. Misslyckas publiceringen ligger posten kvar för nytt försök. Källan behöver därmed inte välja mellan att förlora affärsändringen och att glömma händelsen.

Men outboxen löser inte alla frågor: den gör inte databasen och förmedlaren till en gemensam transaktion, och den garanterar inte att en viss händelse publiceras endast en gång. Publiceraren kan hinna skicka meddelandet men krascha innan den markerat raden som skickad. Nästa försök kan därför ge en dublett. Det är ett förväntat tillstånd, inte en trasig implementation.

## 9.2 Producentens och mottagarens ansvar möts

På sändarsidan skyddar outboxen mot att en genomförd affärsändring saknar beständig publiceringsavsikt. På mottagarsidan skyddar en *Inbox* eller motsvarande deduplicering mot att samma händelse orsakar flera lokala effekter.

För E-417 kan kedjan beskrivas så här:

| Steg | Beständigt spår | Vad det skyddar |
|---|---|---|
| Registrera ärende | Ärende och outbox-rad i samma commit | Avsikten att publicera försvinner inte vid krasch efter commit |
| Publicera | Publiceringsförsök och bekräftelse enligt förmedlarens kontrakt | Tillfälliga överföringsfel kan hanteras |
| Ta emot | Inbox-/dedupliceringsmarkör och arbetsuppgift i samma commit | Upprepad leverans ger inte två arbetsuppgifter |
| Kvittera | Kvittens efter beständig behandling | Obehandlat arbete kan levereras igen |

Denna konstruktion ger ett tydligt sätt att **fortsätta trots osäkra avbrott**, men löftet beror på detaljerna. Outbox-rader måste kunna återfinnas efter backup och failover. Publiceraren måste övervakas så att den inte står stilla. Mottagarens markörer får inte städas bort innan de kan behövas för sena dubletter eller återställning. Brokerretention och dedupliceringsfönster kan vara kortare än affärsprocessens livslängd.

## 9.3 Varför exakt-en-gång är ett missvisande helhetslöfte

Vissa plattformar erbjuder transaktionell behandling eller specifika exactly-once-semantiker inom en avgränsad miljö. Det är värdefullt men ska inte tolkas som att en extern databasändring, ett API-anrop och ett utskick till en tredje part automatiskt blir en enda odelbar transaktion.

Om en tjänst både uppdaterar sin databas och skickar ett e-postmeddelande kan inget internt offsetprotokoll garantera att mottagaren får precis ett brev. Vi måste definiera gränsen för garantin: inom vilken broker, vilka topics, vilka konsumenter, vilka databaser och vilka externa effekter? Utan sådan avgränsning är ordet exakt-en-gång mer marknadsföring än återställningskontrakt.

## 9.4 Ordning, versionering och publiceringsförsening

Två händelser för samma ärende kan publiceras i en annan ordning än databasens uppdateringar om flera outbox-publicerare arbetar parallellt. En design som kräver ordning behöver välja mekanism: exempelvis versionsnummer per ärende, en konsekvent partitionsnyckel och en publicerare som respekterar den avsedda sekvensen. En partition ger inte automatiskt en global ordning och en sekvens kan inte förutsättas utan design.

En möjlig kontroll är att varje händelse bär `aggregate_id`, `aggregate_version`, `event_id`, `schema_version` och spårbar korrelationsidentitet. Exakt uppsättning är ett kontraktsbeslut, inte en universell standard. En konsument som ser version 7 före version 6 behöver veta om den får fortsätta, avvakta eller registrera en avvikelse.

Likaså behöver förändrade meddelandeformat hanteras explicit. Vid återställning kan det finnas outbox-poster skapade av en äldre applikationsversion. En ny publicerare måste antingen kunna publicera dessa korrekt eller genomföra en kontrollerad migrering.

## 9.5 Återställning av outbox och inbox

Anta nu att ärendetjänstens databas återställs till en punkt före en viss händelse men att broker redan har levererat den till handläggningen. Då kan mottagarens tillstånd ligga före producentens återställda historia. Varken outbox eller inbox gör det tillståndet automatiskt konsekvent. Det krävs avstämning med de logiska beroenden som kapitel 6 beskriver.

Det omvända läget är lika viktigt. En återställd producent kan innehålla en outbox-rad som redan publicerats före haveriet, medan uppgiften om skickad status har försvunnit. Den kan då publiceras på nytt. Mottagaren måste tåla detta, och man måste veta hur länge dess dedupliceringsmarkörer finns kvar.

En praktisk återställningsövning bör därför inkludera tre avbrottspunkter: **efter att ärende och outbox har committats men före publicering; efter publicering men före outboxmarkering; efter mottagarens commit men före kvittens**. För varje avbrott ska man kunna förutsäga vilket tillstånd som finns kvar och kontrollera att återhämtningen inte tappar händelser eller skapar dubbla verksamhetseffekter.

## 9.6 Vad lösningen faktiskt åstadkommer

Det centrala arkitekturresultatet är inte att alla system plötsligt delar en global transaktion. Resultatet är att varje lokalt steg får ett beständigt spår som kan identifieras, återupptas och kontrolleras efter avbrott. Vi ersätter ett skört antagande om samtidig framgång med en kedja av hanterbara, verifierbara åtaganden.

Det finns ändå ett återstående problem. En verksamhetsprocess kan bestå av många steg över lång tid, och ibland måste ett redan utfört steg kompenseras. Där börjar nästa kapitel: sagor, långlivade processer och de beslut som inte kan lösas med bara outbox, inbox och återförsök.
