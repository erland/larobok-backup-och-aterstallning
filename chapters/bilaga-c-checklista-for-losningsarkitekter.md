# Bilaga C. Checklista för lösningsarkitekter

Använd checklistan vid designgranskning, betydande förändringar och före produktionssättning. Ett ja behöver vara styrkt av kontrakt, kod, test eller beslutsdokument.

## Verksamhetsflöde och informationsansvar

- [ ] De viktigaste verksamhetsprocesserna och deras tekniska beroenden är kartlagda.
- [ ] Auktoritativa data och återuppbyggbara projektioner är särskilda från cache och temporär data.
- [ ] För varje tjänst framgår vilka egna databaser, meddelanden och offsets som behöver skyddas.
- [ ] RPO och RTO är satta för verksamhetsförlopp, inte bara för enskild databas.
- [ ] Konsistenskrav och acceptabla avvikelser vid återstart är dokumenterade.

## Händelser och integrering

- [ ] Händelser har beständig unik identitet samt hanterad schema-/versionsutveckling.
- [ ] Producentens dual-write-risk är löst eller uttryckligen accepterad.
- [ ] Konsumenter kan hantera dubletter och redovisa hur dedupliceringsdata bevaras.
- [ ] Konsumentposition, affärsändring och kvittens har en dokumenterad ordning.
- [ ] Retention och replay-förmåga räcker för beslutad återställningshorisont.
- [ ] Externa API-anrop har avtalat idempotens- och återfrågningsförfarande eller manuell avstämning.
- [ ] Oåterkalleliga sidoeffekter kan isoleras under replay och katastrofåterställning.

## Design och verifiering

- [ ] Återbyggnad av projektioner och snapshots har testats med historiska scheman.
- [ ] Sagor och långlivade processer har vägar för okända, partiella och kompenserade utfall.
- [ ] Säker återstart, avstämning och återöppning har verifierbara godkännandekriterier.
- [ ] Åtgärdsansvar och beslutsmandat finns för tillstånd som inte går att reparera automatiskt.
- [ ] Minst ett test har avbrutits mellan lokal commit och meddelandekvittens/publicering.

## Granskningsbeslut

Ange per brist: risk, verksamhetspåverkan, föreslagen kontroll, ansvarig, tidsplan och vem som accepterar kvarstående risk. En omarkerad ruta är inte i sig ett fel; en okänd eller oägd risk är det.
