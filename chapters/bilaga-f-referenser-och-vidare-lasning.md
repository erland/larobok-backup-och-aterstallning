# Bilaga F. Referenser och vidare läsning

Källorna nedan är urval av primärdokumentation och etablerade ramverk. Hänvisningarna är avsedda som ingångar; plattformsbeteenden och stöd kan förändras mellan versioner. Kontrollera alltid produktversion och driftmodell före införande.

## Återställning och kontinuitet

- NIST SP 800-34 Rev. 1, *Contingency Planning Guide for Federal Information Systems*: https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final
- NIST SP 800-184, *Guide for Cybersecurity Event Recovery*: https://csrc.nist.gov/pubs/sp/800/184/final
- NIST SP 800-61 Rev. 3, *Incident Response Recommendations and Considerations for Cybersecurity Risk Management*: https://csrc.nist.gov/pubs/sp/800/61/r3/final
- CISA, *Ransomware Guide*: https://www.cisa.gov/stopransomware/ransomware-guide

## Infrastruktur och databas

- PostgreSQL 17, *Continuous Archiving and Point-in-Time Recovery (PITR)*: https://www.postgresql.org/docs/17/continuous-archiving.html
- Kubernetes, *Backing up an etcd cluster*: https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/
- Kubernetes, *Volume Snapshots*: https://kubernetes.io/docs/concepts/storage/volume-snapshots/

## Meddelanden, konsistens och designmönster

- RabbitMQ, *Consumer Acknowledgements and Publisher Confirms*: https://www.rabbitmq.com/docs/confirms
- Apache Kafka, *Documentation*: https://kafka.apache.org/documentation/
- Microsoft Azure Architecture Center, *Saga pattern*: https://learn.microsoft.com/en-us/azure/architecture/patterns/saga
- Microsoft Azure Architecture Center, *CQRS pattern*: https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs
- AWS Prescriptive Guidance, *Transactional outbox pattern*: https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html
- AWS Prescriptive Guidance, *Event sourcing pattern*: https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/event-sourcing.html

## Så används referenserna

Produktdokumentation beskriver funktioner inom särskilda gränser, inte automatiska end-to-end-garantier för hela verksamhetsprocesser. Ramverk ger terminologi och arbetssätt men ersätter inte organisationsspecifika krav, testprotokoll eller avtal med integrationsparter. Fiktiva scenarier i denna bok är förklarande konstruktioner och inte dokumenterade incidentfall.
