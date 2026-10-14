# Faktakontroll

## Ej ännu verifierat
- Tillförlitlighetssemantik och förutsättningar för Kafka, RabbitMQ och molnköer.
- Hur snapshots och PITR samverkar med transaktionsloggar i respektive databasprodukt.
- Skydds- och återställningsgarantier för infrastrukturella snapshots, zon-/regionreplikering och immutable backups.
- Exakt omfattning och utgåva av relevanta standarder.

## Verifieringsmetod
För varje kapitel: lista centrala tekniska påståenden, förstahandskälla, kontrolltidpunkt, version, osäkerheter och godkännande. Kontrollera demonstrationsexempel mot verklig konfiguration före publicering.

## Revision 3 – inledning och kapitel 1 (2026-10-14)
- Granskat att PostgreSQL:s officiella dokumentation om PITR kräver basbackup och en komplett WAL-kedja; `pg_dump` är inte basbackup för WAL-baserad PITR. Källa: https://www.postgresql.org/docs/17/continuous-archiving.html (produktversion 17; principen måste verifieras för den valda driftversionen).
- RPO/RTO används i allmän mening som mål för acceptabel dataförlust respektive återställningstid. Mätgränser och verksamhetens omfattning ska preciseras vid tillämpning.
- Avsiktligt ingen leverantörsgaranti för applikationskonsistenta snapshots: samordning med applikation och tjänst är konfigurationsberoende.
- De angivna klockslagen och ärendena är konstruerade exempel, inte verifierade driftfall.
- Redaktionellt kontrollerat: inledningen förklarar frågan; kapitel 1 äger begreppen RPO, RTO, PITR och traditionella samordningsgränser; kapitel 2 lämnas för uppdelningen i tjänster.

## Revision 4 – kapitel 2–3 (2026-10-14)
- Kontroll av att självständiga datalager försvårar samordnad konsistens: Microsoft Learn, *Data considerations for microservices*: https://learn.microsoft.com/en-us/azure/architecture/microservices/design/data-considerations
- Kontroll av lokal transaktion kontra flera tjänsters verksamhetsprocess: Microsoft Learn, *Saga design pattern*: https://learn.microsoft.com/en-us/azure/architecture/patterns/saga
- Kontroll av risk mellan commit och publicering: Microsoft Learn, *Transactional Outbox*: https://learn.microsoft.com/en-us/azure/architecture/databases/guide/transactional-out-box-cosmos
- Arkitekturjämförelser är avsiktligt teknikneutrala. Exemplet E-417 och tidslinjerna är konstruerade och påstår inte produktspecifika leveransgarantier.
- Redaktionell kontroll: Kapitel 2 beskriver vad som förändras och introducerar inte lösningsmönster; kapitel 3 behandlar acceptanskriterier och avstämning, utan att repetera systemuppdelningen. Begrepp som outbox, saga och replay lämnas till planerade fördjupningar.


## Revision 5 – kapitel 4–6 (2026-10-14)

Faktakontroll mot primärkällor:
- Microsoft Azure Architecture Center, *Data considerations for microservices*: https://learn.microsoft.com/en-us/azure/architecture/microservices/design/data-considerations — separata dataägarskap, eventual consistency och förhållandet mellan logisk datagräns och fysisk lagring.
- RabbitMQ, *Consumer Acknowledgements and Publisher Confirms*: https://www.rabbitmq.com/docs/confirms — åtskillnad mellan publiceringsbekräftelser och konsumentkvittens samt vad en kvittens faktiskt garanterar.
- RabbitMQ, *Quorum Queues*: https://www.rabbitmq.com/docs/quorum-queues — hållbarhet, replication och begränsningar för dead lettering.
- Apache Kafka dokumentation: https://kafka.apache.org/documentation/ — partitionsordning, offsets och retention ska bedömas utifrån faktiskt installerad version och konfiguration.

Fortsatt granskningsbehov: produktspecifika inställningar och garantier kontrolleras vid framtida körbara exempel. Kapitel 4–6 gör inga löften om garanterad exakt-en-gång-bearbetning eller globalt konsistenta snapshots. Skillnaden mellan logisk, kausal och verksamhetsmässig konsistens har särskilt granskats.

## Revision 6 – kapitel 7–9 (2026-10-14)

- AWS Prescriptive Guidance, *Event sourcing pattern*: https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/event-sourcing-pattern.html — fullständig historik, replay, snapshots, versionshantering och risken för externa bieffekter.
- Microsoft Learn, *Transactional Outbox pattern*: https://learn.microsoft.com/en-us/power-platform/architecture/reference-architectures/transactional-outbox-pattern — atomär lokal lagring av affärsförändring och publiceringsavsikt; at-least-once och nödvändig deduplicering.
- Microsoft Learn, *Idempotent Consumer pattern*: https://learn.microsoft.com/en-us/azure/architecture/patterns/idempotent-consumer — atomär effekt och dedupliceringsmarkör samt race conditions vid konkurrens.
- SQL-exemplen är pedagogisk pseudokod av PostgreSQL-typ och kräver anpassning av tabeller, applikationsvillkor och transaktionsisolering innan körning.
- Redaktionell avgränsning: kapitel 7 äger rekonstruktion av tillstånd, kapitel 8 säker upprepning av lokalt arbete, kapitel 9 samspelet mellan publicering och mottagning. Externa kompensationer behandlas först i kapitel 10–11.

## Revision 7 – kapitel 10–11 (2026-10-14)
- Saga behandlas som en sekvens lokala transaktioner med framåtriktad återhämtning och kompensationsåtgärder. Kompensation beskrivs inte som att historiken raderas. Källor: https://learn.microsoft.com/en-us/azure/architecture/patterns/saga och https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-patterns.html (kontrollerade 2026-10-14).
- Orkestrering och koreografi beskrivs som alternativa samordningsmodeller, med skilda avvägningar för insyn och återstart. Källa: samma Microsoft- och AWS-dokumentation.
- Osäkert utfall vid timeout, teknisk mottagning kontra verksamhetsmässig verkställighet, idempotensfönster och avstämning beskrivs som integrationskontraktsfrågor. Garanti om automatisk exakt-en-gång-effekt över externa gränser görs inte.
- E-417 och operation-92 är konstruerade pedagogiska exempel. Specifika API-garantier behöver kontrolleras mot valda motparters faktiska avtal före publicering/tillämpning.
- Redaktionellt: kapitel 10 äger process-/kompensationsmodellen; kapitel 11 äger gränsen mot externa motparter. Outbox/inbox och tidigare principer återförklaras inte.

## Revision 8 – kapitel 12–14 (2026-10-14)
- Kapitel 12: arkitekturkrav och ADR som beslut, inga nya grundförklaringar. ADR-014 är fiktivt.
- Kapitel 13: etcd-backup av Kubernetes kontrollplan skiljs från beständiga applikationsdata och volymsnapshots. Kontrollkällor: https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/ och https://kubernetes.io/docs/concepts/storage/volume-snapshots/ . Produktkonfiguration och version ska verifieras vid tillämpning.
- Kapitel 14: PostgreSQL PITR bygger på fysisk basbackup och sammanhängande WAL-arkiv. pg_dump är inte fysisk basbackup för WAL-återspelning. Källa: https://www.postgresql.org/docs/17/continuous-archiving.html .
- Backupmatrisen är vägledning, inte garantier för enskilda brokertyper eller hanterade produkter. Specifik backup/replay-förmåga måste provas.
- Redaktionell avgränsning: kapitel 12 designbeslut, kapitel 13 körplattform och beroenden, kapitel 14 dataklassade backupmetoder. Kapitel 15 äger återställningsordningen.

## Revision 9 – kapitel 15–16 (2026-10-14)

- Kapitel 15 är en verksamhetsorienterad DR-process, inte en generell startordning. Exempel om failover, fencing, RPO/RTO, meddelandepositioner och gradvis öppning är arkitekturresonemang som behöver verifieras för vald teknisk plattform. Referens: NIST SP 800-34 Rev. 1, https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-34r1.pdf.
- Kapitel 16 skiljer komprometterat respektive rent tillstånd, informationsintegritet och säkerhet från generell DR. Källor: NIST SP 800-184 https://csrc.nist.gov/pubs/sp/800/184/final och CISA StopRansomware Guide https://www.cisa.gov/stopransomware/ransomware-guide. Notera att dessa källor är vägledningar, inte produktgarantier eller rättsliga bedömningar.
- Redaktionell gräns: kapitel 15 = återställningsberoenden, teknisk/affärsmässig ordning och kontrollerad återöppning; kapitel 16 = återställning av tillit efter cyberincident, ren miljö och bedömning av osäker data. Kapitel 17 sparas för runbooks och operativ styrning.
- Fall E-417 är fiktivt. Tidsangivelser och hypotetiska konsekvenser är pedagogiska exempel, inte empiriska observationer.

## Revision 10: kapitel 17–18 (2026-10-14)

- Kapitel 17 beskriver en rekommenderad besluts- och ansvarsfördelning, inte ett standardiserat organisationsschema. Återställningssekvensen avgränsas mot de tekniska beroenden som förklaras i kapitel 15.
- Kapitel 18 skiljer backup-/restore-test, tjänstetest, flödestest och verksamhetsmässig DR-övning. Godkänt tekniskt test är inte likvärdigt med verifierad verksamhetsåterställning.
- Tekniska återhämtningsscenarier och grundbegrepp jämförda med NIST SP 800-34 Rev. 1 (Contingency Planning Guide for Federal Information Systems), https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final, och NIST SP 800-184 (Guide for Cybersecurity Event Recovery), https://csrc.nist.gov/pubs/sp/800/184/final. Ramverken används som vägledning, inte som bevis att ett visst system uppfyller standardkrav.
- Exempel och tider i E-417-scenarierna är konstruerade och ska inte tolkas som faktiska driftdata.
- Redaktionellt: Kapitel 17 fokuserar på beslut, ledning och operativ runbook; kapitel 18 på falsifierbara prov, evidens och förbättringar. Tidigare designmönster förklaras inte om.

## Revision 11 – kapitel 19–20 (2026-10-14)

- Kapitel 19: exempel på ansvarsfördelning är en rekommendation och ingen normativ organisationsmodell. Skillnaden mellan komponentansvar, flödesansvar, mandat och accepterad risk är avsiktlig.
- Kapitel 20: fyrastegsmodellen är ett egenutformat analysstöd, inte en etablerad certifierings- eller branschstandard.
- Externt verifierade bakgrundskällor: NIST SP 800-34 Rev. 1 (2010, uppdaterad 2010), https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final ; NIST CSF 2.0, https://www.nist.gov/cyberframework (Govern, Recover). Källorna används för principer om kontinuitetsplanering, ansvar, övning och uppföljning, inte för bokprojektets egen mognadsmodell.
- Redaktionell avgränsning: kapitel 19 = styrning, mandat och krav; kapitel 20 = prioritering och stegvis införande. Återställningsprocedurer och felinjektionsmetodik återförklaras inte.

## Revision 12 – bilagor och samlad manusgranskning
Bilaga F innehåller primärlänkar. NIST SP 800-61 Rev. 3 från april 2025 är den gällande referensen i källurvalet. AWS Transactional Outbox omfattar dual-write och förutsätter hantering av dubbla meddelanden. Övningsfallen är konstruerade och ska inte förväxlas med observerade incidenter. Se docs/helhetsgranskning.md för redaktionell kontroll och öppna frågor.


## Revision 13 – riktad fördjupning

Fördjupade kapitel: 4, 6, 10, 12, 13, 14, 15 och 18 samt bilaga E. Genomgående exempel är konstruerade, inklusive tider och övningsutfall.

- PostgreSQL 17: https://www.postgresql.org/docs/17/continuous-archiving.html (fysisk basbackup + sammanhängande WAL-kedja för PITR; recovery targets, tidslinjer och arkiv). En logisk dump är inte en fysisk WAL-baserad basbackup.
- Kubernetes: https://kubernetes.io/docs/concepts/storage/volume-snapshots/ och https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/ (volymsnapshots och etcd avser olika skikt; applikationskonsistens måste bedömas separat).
- Kafka: https://kafka.apache.org/documentation/ (retention, konsumentpositioner, transaktionsgarantier inom avgränsade gränser).
- RabbitMQ: https://www.rabbitmq.com/docs/confirms (acknowledgements och publisher confirms har distinkta roller).

Redaktionell kontroll: varje tillägg svarar på en ny praktisk fråga; tidigare introduktioner upprepas inte. Kapitel 13 behandlar beroenden, 14 skydd och rekonstruktion, 15 ledningens återöppningsbeslut, 18 verifiering. Bilaga E är en operativ referens, inte ett ytterligare teorikapitel.
