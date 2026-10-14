# Bilaga D. Checklista för drift- och plattformsansvariga

Denna lista avser operativ beredskap och kompletterar arkitektens kontrakt i bilaga C.

## Inventering och skydd

- [ ] Det finns en aktuell inventering av databaser, objektlagring, brokerkonfiguration, volymer, nycklar, hemligheter, konfiguration och beroenden.
- [ ] Backupmetod och återställningsmål anges för varje auktoritativ informationsmängd.
- [ ] Backup och ändrings-/transaktionsloggar skyddas med kontrollerad åtkomst och dokumenterad retention.
- [ ] Isolerad eller oföränderlig kopia finns där hotmodellen kräver det.
- [ ] Återställningsbehörigheter och nyckelmaterial är åtkomliga även när ordinarie identitetsplattform är nere.
- [ ] Replikering, snapshots och backup har särskilda syften och kontrolleras separat.

## Plattform och beroenden

- [ ] Ordningen för identitet, nät, DNS, certifikat, konfiguration, lagring och datatjänster är dokumenterad.
- [ ] Även Kubernetes-kontrollplan och dess lagring skyddas där driftmodellen kräver det.
- [ ] För hanterade tjänster är leverantörens faktiska export-, backup- och restore-garantier kända.
- [ ] Kapacitet, bandbredd och återläsningstid är uppmätta med realistiska datavolymer.
- [ ] Tjänster kan startas med konsumenter och externa utskick spärrade under avstämning.

## Övning och driftbeslut

- [ ] Det finns en aktuell och åtkomlig runbook, inklusive alternativ kommunikationsväg.
- [ ] Ett fullständigt återställningstest har verifierat konsistens och verksamhetsflöden, inte bara processuppstart.
- [ ] Utfall för RPO/RTO, förlorade och upprepade händelser, och externa kvittenser dokumenteras.
- [ ] Det finns beslutsägare för återöppning, rollback av återställningsförsök och eskalering.
- [ ] Vid misstänkt intrång finns separat rutin för bevisbevarande, identitetsrotation och ren miljö.

## Bevis som ska bevaras

Protokollför backup-ID, logg-/offsetgränser, återställd kod- och schemaversion, dataintegritetskontroller, observerade fel, godkännande av informationsägare samt ansvarig för efterarbete. Lagra övningsunderlaget utanför den miljö som kan behöva återställas.
