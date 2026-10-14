# 13. Infrastruktur för distribuerade system

När ärendeplattformen flyttas från virtuella servrar till en containerplattform kan det se ut som om återställningen förenklas: en ny container kan startas automatiskt om den gamla försvinner. Men att *återskapa en process* och att *återskapa systemets tillstånd* är två olika driftuppgifter. En ny pod kan vara helt frisk samtidigt som dess databas, autentisering eller händelseposition saknas.

Den avgörande infrastrukturfrågan är därför **vilka resurser som är utbytbara och vilka som bär beständigt, verksamhetskritiskt tillstånd**.

## 13.1 Fyra lager måste fungera tillsammans

För en modern tjänst kan återstart delas upp i fyra beroenden:

1. **Körmiljö:** noder, container-runtime, orkestrering, nätverk och DNS.
2. **Deklarativ konfiguration:** images, versionslåsta manifest, distributionsinställningar, beroenden och infrastrukturkod.
3. **Beständigt tillstånd:** databaser, objekt, kö-/loggdata, volymer och behandlingsmarkörer.
4. **Tillit och anslutningar:** certifikat, nycklar, identiteter, externa åtkomster och nödvändiga tjänstekonton.

Det första lagret kan ofta nyetableras. Det andra kan återskapas om rätt versioner och beroenden finns bevarade. Det tredje kräver avsiktliga skydds- och återställningsmetoder. Det fjärde får inte behandlas som ett efterarbete: ett återställt system utan rätt nycklar eller med utgångna certifikat kan förbli obrukbart.

**Aha-punkten:** Infrastruktur som kod återställer hur miljön ska se ut, inte automatiskt vilka affärshändelser som har inträffat i den.

## 13.2 Vad Kubernetes återställer – och inte

Kubernetes kan ersätta misslyckade poddar och återskapa önskat antal instanser. En sådan självläkning motsvarar inte en backup. Har en databas fått en felaktig radering kommer ett nytt databas-Pod inte att återskapa de raderade uppgifterna från förr.

I ett självförvaltat Kubernetes-kluster är etcd kritiskt för klustrets kontrollplan och dess objekttillstånd. En etcd-snapshot kan behövas för katastrofåterställning av kontrollplanet, men den är **inte** en säkerhetskopia av applikationsdatabaser som ligger i externa databastjänster eller på persistent volumes. Att återställa etcd kan dessutom föra tillbaka äldre kontrollplansobjekt och måste samordnas med det faktiska tillståndet i lagring och externa resurser.

PersistentVolumeClaims beskriver en önskad lagringsrelation; exakt hur data skyddas beror på StorageClass, lagringsleverantör, snapshotkapabiliteter och tillhörande backupverktyg. En volymsnapshot kan vara kraschkonsekvent utan att vara applikationskonsekvent. Databaser kan behöva egna backupmekanismer eller koordinerade åtgärder. Det går inte att härleda en korrekt återställningsstrategi enbart från att resursen har `persistentVolumeClaim` i ett manifest.

För hanterade kluster är kontrollplanet och dess återställningsmöjligheter ofta leverantörsstyrda. Driftteamet måste därför skilja på vad leverantören garanterar, vad kunden ansvarar för och vilka resurser som ligger utanför klustret.

## 13.3 Flera tillgänglighetszoner är inte en historisk backup

Replikering över zoner kan göra en tjänst tålig mot att en nod eller en zon försvinner. Men en felaktig radering, korrupt uppdatering eller komprometterad applikation kan replikeras lika effektivt som en korrekt ändring. Repliker har dessutom en egen fel- och failoversemantik: synkron respektive asynkron replikering påverkar både tillgänglighet och potentiellt databortfall.

Tre förmågor måste därför bedömas separat:

| Förmåga | Primärt skydd | Typiskt missförstånd |
|---|---|---|
| Hög tillgänglighet | Fortsatt tjänst trots vissa komponentfel | ”Vi har tre repliker, alltså har vi backup” |
| Katastrofåterställning | Återstart vid större miljö- eller regionbortfall | ”Failover är alltid samma sak som återställning till rätt historiskt tillstånd” |
| Historisk återställning | Återgång efter radering, logiska fel eller intrång | ”En kopia i en annan zon innehåller den gamla korrekta informationen” |

En robust lösning kan behöva alla tre, men inte nödvändigtvis med samma teknik eller återställningstid.

## 13.4 Beroenden utanför containern

I ärendeplattformen kan en databas ligga i en hanterad tjänst, filer i objektlagring och händelser i en extern broker. När ett kluster återställs återkommer därför inte dessa beroenden automatiskt. Återställningsplanen behöver ha svar på vilka tjänster som nyetableras, vilka endpoints som byter adress, hur behörigheter återställs och vilka integrationer som måste vara spärrade under arbetet.

CI/CD, image-register och Git-repositorier är också operativa beroenden. Om imageversionen från katastroftillfället har gallrats ur registret kan en deklarativ deployment peka på en version som inte längre finns. Versionslåsta images och artefaktretention behöver utformas efter återställningsmålen. Samma sak gäller infrastrukturmoduler, DNS-konfiguration och dokumenterade nätverksregler.

Säkerhetskopior av hemligheter kräver särskild hantering. Nycklar kan vara icke-exporterbara, och då måste återställningsstrategin bygga på en dokumenterad väg för nyutgivning, nyckelrotation eller leverantörens särskilda skydd. Att dumpa hemligheter okrypterat till ett generellt backupmål är inte ett acceptabelt genvägsval.

## 13.5 En isolerad återställningsmiljö är ett arkitekturkrav

För att kunna testa återställning på riktigt behöver vi kunna starta miljön utan att skapa verkliga verksamhetseffekter. En kopia av ärendetjänsten som av misstag får produktionsbehörighet mot expedierings-API:et kan skicka gamla beslut på nytt.

En säker återställningsmiljö använder därför separata identiteter, spärrade utgående anrop eller testmottagare, kontrollerad åtkomst till känsliga data och tydlig märkning av återställd information. Vid säkerhetsincidenter måste även själva plattformen och leveranskedjan kunna betraktas som misstänkta; den frågan behandlas särskilt i kapitel 16.

## 13.6 Infrastrukturens återställningskontrakt

För varje beständig komponent bör driftunderlaget beskriva vem som ansvarar, vilken återställningsmetod som finns, vilken infrastruktur den kräver, vad som ingår och vad som uttryckligen **inte** ingår. Testa också om miljön verkligen går att bygga utan tillgång till den ursprungliga regionens kontrollplan, lagringskonto eller hemlighetstjänst.

Denna kartläggning leder naturligt till en mer konkret fråga: när resurserna väl har klassificerats, vilka data ska då säkerhetskopieras, hur ofta och med vilka bevis för att kopiorna går att använda? Det är ämnet för kapitel 14.

## 13.7 Exempel: en ny region är inte en ny kopia av den gamla

Klockan 08.12 blir primärregionen otillgänglig. Plattformsteamet kan skapa ett nytt Kuberneteskluster i reservregionen, men det löser bara delar av problemet. Ett fungerande återställningsscenario behöver etablera ett antal beroenden i en kontrollerad ordning.

Först måste beslut tas om den gamla regionen verkligen är isolerad, så att två miljöer inte samtidigt börjar skriva till samma verksamhetsprocesser vid ett partiellt nätavbrott. DNS-failover utan en sådan skrivspärr kan skapa ett split-brain-läge. Därefter behövs nätverk, routning, brandväggsregler och åtkomst till de register där containeravbilder lagras. Om image-registret finns enbart i den förlorade regionen kan klustret vara friskt utan att kunna starta applikationerna.

Nästa beroende är identitet och nyckelmaterial. En databasbackup kan vara fullständigt användbar men ändå inte kunna dekrypteras om nyckeltjänsten eller behörigheterna saknas. Samtidigt är det olämpligt att kopiera hemligheter okontrollerat till en ny miljö. Återställningsplanen måste därför visa hur nödvändiga certifikat, nycklar och tjänsteidentiteter finns tillgängliga under tydlig kontroll.

Sedan etableras beständiga resurser: databaser, objektlagring, eventuell självförvaltad broker och de lagringsklasser som applikationerna faktiskt kräver. En Kubernetes VolumeSnapshot är en mekanism för vissa volymtyper, inte en globalt transaktionskonsistent backup av databaser och köer. Snapshottens stöd beror på CSI-drivrutin, lagringsplattform och hur applikationens data görs konsistenta. Kubernetes etcd-säkerhetskopior återställer å sin sida kontrollplanets objekt, inte automatiskt alla underliggande applikationsdatabaser.

Slutligen behöver applikationsversioner och databasscheman passa ihop. Om infrastruktur deklareras som kod kan konfigurationen återskapas reproducerbart, men kodförrådet innehåller inte nödvändigtvis externa brandväggsöppningar, tredjepartsavtal, hemligheter eller verkliga data. Det bör finnas en versionsmärkt beskrivning av vilket återställningspaket som prövats med vilket applikationsbygge.

## 13.8 Hanterad tjänst flyttar ansvar – den tar inte bort det

Ett hanterat databaserbjudande kan ge inbyggd replikering, failover och backup, men kundens ansvar för dataklassning, återställningstid, behörighet, återställningspunkt, applikationskompatibilitet och övning kvarstår. Samma gäller en hanterad meddelandeplattform: leverantören kan hantera noder, medan kunden måste veta vad som händer med retention, konsumentpositioner och händelser vid ett regionbortfall.

För varje kritisk tjänst behövs därför ett kort ansvarskontrakt: vem återställer resursen, vem väljer återställningspunkt, vem återansluter klienterna och vem kontrollerar verksamhetsresultatet? Ett prov där man verkligen startar i reservregionen upptäcker ofta beroenden som inte syns i en resurslista: callback-URL:er, tillåtna IP-adresser, certifikatkedjor, DNS-cache och externa parters brandväggar.

**Det centrala skiftet för driftansvariga är att verifiera hela beroendekedjan, inte bara att orkestreringsplattformen kan starta nya instanser.**
