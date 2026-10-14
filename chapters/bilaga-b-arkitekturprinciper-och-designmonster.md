# Bilaga B. Arkitekturprinciper och designmönster

Bilagan är ett stöd vid designbeslut, inte en katalog av obligatoriska mönster. Välj utifrån dataägarskap, felmodell, externa sidoeffekter och verifierbarhet.

| Problem | Mönster eller princip | Villkor och risk |
|---|---|---|
| Databasändring får inte förlora sin publiceringsavsikt | Transactional Outbox | Kräver atomisk lokal commit, leveransövervakning och tolerans för dubletter. |
| Återlevererat meddelande skapar dubbla arbetsuppgifter | Inbox eller idempotent konsument | Beständig identitet och affärsändring måste skyddas i samma transaktionsgräns. |
| Förlorad sökvy behöver byggas om | Återbyggbar projektion / CQRS | Kräver fullständig auktoritativ källa, versionskompatibilitet och säkert replay-läge. |
| Hela domäntillståndet rekonstrueras från händelser | Event sourcing | Historiken är skyddsvärd primärdata och måste säkerhetskopieras. |
| Verksamhetsflöde omfattar flera transaktioner | Saga / processhanterare | Steg och kompensationer behöver explicit definierade utfall och spårbarhet. |
| Okänt utfall efter API-timeout | Idempotensnyckel + statusförfrågan + avstämning | Retry utan identifierare kan dubblera en extern handling. |
| Olika databaser återställs till olika tidpunkter | Kausalt återställningskontrakt | Kontrollera förlorade/överskjutande effekter och avstämningsprocedur. |
| Lång replay överskrider RTO | Snapshot + händelseloggar | Kräver känd sekvensgräns och kontrollerad kompatibilitet. |
| Fel sprids via automatiska återförsök | Begränsade retries, backoff, DLQ | Permanent fel kräver åtgärd, inte obegränsad återleverans. |

## Arkitekturbeslut att dokumentera

För varje verksamhetskritiskt flöde: dokumentera ägare, auktoritativa tillstånd, händelse- och integrationskontrakt, tillåtna tillståndsskillnader, maximal dataförlust, uppskattad återuppbyggnadstid, externa irreversibla effekter och verifieringskriterier. Ange dessutom vilka risker som är accepterade och av vem.

## Exempel på ett arkitekturbeslut

**ADR: Kontrollerad återupptagning av E-417**. Ärendetjänsten lagrar ärende och outbox i samma transaktion. Handläggningstjänsten lagrar mottaget event-ID och arbetsuppgift i samma lokala transaktion. Vid katastrofåterställning spärras utgående expediering tills oklara externa kvittenser har stämts av. Beslutet ska omprövas om meddelanderetention eller kontrakt ändras. Verifiering sker med felinjektion efter var och en av tre kritiska commit-/kvittensgränser.

Se kapitel 7–12 för resonemanget bakom valen. Principen är att **varje lokal garanti ska ha en kontrollerbar gräns, och återställning över gränserna ska vara en uttrycklig process**.
