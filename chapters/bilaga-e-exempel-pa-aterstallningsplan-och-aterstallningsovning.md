# Bilaga E. Exempel på återställningsplan och återställningsövning

Detta är en illustrativ runbook för det fiktiva ärendehanteringssystemet. Den är inte avsedd att köras oförändrad i produktion. Ersätt samtliga mål, roller och kontrollsteg med verksamhetens beslutade nivåer.

## E.1 Utgångsläge och mål

En lagringsincident gör att ärendetjänstens primärdatabas måste återställas. Handläggningstjänsten och händelseförmedlaren har fortsatt bearbeta händelser. Ett externt expedierings-API kan redan ha mottagit beslut för E-417. Mål: återuppta registrering och handläggning utan borttappade ärenden, dubbel expediering eller oförklarade processlägen.

Övningsmål: återställd auktoritativ databas från verifierad backup och tillhörande loggar; identifierade skillnader mellan återställningspunkter; alla avvikande ärenden avstämda eller spärrade med ansvarig handläggare; utgående expediering återöppnad först efter verksamhetsgodkännande. Övningen mäter faktisk RTO och observerad dataförlust, utan att dessa fiktiva system tillskrivs ett allmängiltigt numeriskt mål.

## E.2 Roller och beslutsmandat

| Roll | Ansvar |
|---|---|
| Incidentledare | Lägesbild, prioritering, beslut om fortsatt isolering, protokoll och kommunikation. |
| Plattform-/databasansvarig | Återläsning, dataintegritet, loggpositioner och dokumenterad driftstart. |
| Tjänsteägare/utvecklingsansvarig | Konsumenternas återstart, idempotens, outbox/inbox och tekniska felkontroller. |
| Integrationsansvarig | Kontakter, kvittenser och avstämning mot extern mottagare. |
| Verksamhets-/informationsägare | Beslutar om avvikelser och godkänner verksamhetsmässig återöppning. |
| Säkerhetsfunktion | Bedömer om dataintegriteten kan betros; vid attack används separat incidentprocess. |

## E.3 Genomförandesteg

1. **Avgränsa:** Stoppa eller isolera nya skrivningar där de riskerar att förvärra läget. Spärra automatiska externa expedieringar, men bevara köer och granskningsloggar enligt beslutad rutin.
2. **Fastställ fakta:** Dokumentera senaste säkra backup, transaktionsloggar, brokerpositioner, outboxstatus, programversioner och tidpunkt för senast kända korrekta verksamhetsutfall.
3. **Välj återställningsmål:** Besluta om databastidpunkt, godtagbar dataförlust och metod för att stämma av sådant som redan hänt efter punkten.
4. **Återläs isolerat:** Återställ databas med korrekta loggar i kontrollerad miljö. Kontrollera schema, integritet, identitet och åtkomlighet utan att öppna konsumenterna.
5. **Jämför tillstånd:** Identifiera exempelvis ärenden vars handläggnings- eller expedieringsstatus ligger före ärendetjänstens återställda bild. Använd korrelations-ID, händelse-ID och externa kvittenser.
6. **Rekonstruera och avstäm:** Bygg om härledda vyer vid behov; återleverera bara händelser som enligt kontrakt får återlevereras. För E-417 frågar integrationsansvarig extern mottagare om beslut redan registrerats.
7. **Hantera okända utfall:** Där svar saknas förblir ärendet spärrat med utsedd beslutsägare. Varken timeout eller utebliven intern rad tolkas som bevis på att extern handling inte skett.
8. **Öppna stegvis:** Starta läsfunktioner, därefter kontrollerade konsumentgrupper och sist externa utskick. Logga gränserna mellan stegen och avbryt om dubletter eller konsistensfel uppstår.
9. **Godkänn:** Verksamhetsägaren granskar avvikelselista, stickprov och mätvärden innan driftläget förklaras återställt.
10. **Efterarbete:** Dokumentera faktisk återställningstid, informationsförlust, tillfälliga manuella åtgärder, brister och ansvariga förbättringar.

## E.4 Injektioner under övningen

**Test A – förlorad outboxmarkering:** Låt producenten krascha efter brokerpublicering men innan outboxstatus säkrats. Förväntat: eventuell återpublicering identifieras och medför ingen dubbel verksamhetseffekt.

**Test B – förlorad mottagarkvittens:** Stoppa konsumenten efter databascommit men före brokerkvittens. Förväntat: återleverans blir ofarlig tack vare beständig deduplicering.

**Test C – okänt externt utfall:** Låt API-anropet genomföras hos mottagaren men ge avsändaren timeout. Förväntat: statusförfrågan/avstämning avgör nästa steg; ingen blind ny expediering.

**Test D – historiskt datagap:** Återställ en databas till en punkt tidigare än annan tjänsts. Förväntat: diskrepanslista och spärr innan kontrollerad återöppning.

## E.5 Godkännandemall

| Kontroll | Bevis | Resultat/ansvarig |
|---|---|---|
| Backup och loggkedja läsbara | Backup-ID, tidsstämpel, integritetsrapport | Fyll i |
| RPO/RTO uppmätt | Start-/sluttider och identifierad förlust | Fyll i |
| Ingen obehörig dubbelexpediering | Extern kvittensavstämning | Fyll i |
| Oförklarade ärenden spärrade | Avvikelselista med ägare | Fyll i |
| Replay och konsumentåterstart säkra | Händelse-ID, brokerposition och loggar | Fyll i |
| Verksamhetsmässig återöppning beslutad | Namn, tid, omfattning och villkor | Fyll i |

En övning kan bedömas som misslyckad trots att alla servrar startat; det är avsiktligt. Syftet är att identifiera återställningsbrister innan en verklig incident inträffar.

## E.7 Ifyllt övningsprotokoll – partiell återställning

Följande protokoll är ett **fiktivt exempel**, inte ett rapporterat utfall från en verklig produktionsövning. Det visar vilken spårbarhet som bör finnas mellan en plan och ett godkännandebeslut.

| Kontrollpunkt | Illustrativt utfall | Ansvarig roll | Godkänt när |
|---|---|---|---|
| 09.00: Fel injiceras | Handläggningsdatabas rullas tillbaka, brokerposition kvarstår | Testledare | Fel och återställningspunkt är dokumenterade |
| 09.12: Teknisk restore | Databasen startar, schema och grundintegritet godkända | Databasansvarig | Backuplogg och kontroller är dokumenterade |
| 09.18: Konsistenskontroll | E-417 saknar arbetsuppgift trots publicerad händelse | Tjänsteägare | Glappet upptäcks automatiskt |
| 09.27: Rekonstruktion | Händelsen återlevereras från bevarad källa | Integrationsansvarig | Exakt en arbetsuppgift finns |
| 09.34: Extern kontroll | Tidigare expedition bekräftas; inga nya utskick görs | Verksamhetsägare | Extern och intern status kan avstämmas |
| 09.40: Återöppning | En begränsad konsumentgrupp öppnas | Incidentledare | Övervakning och stoppvillkor är aktiva |

I en första provkörning utan glappkontroll bör testet bedömas som **underkänt** även om databasen återställts. Efter korrigering upprepas exakt samma felinjektion; godkännande kräver uppfyllda verksamhetsvillkor, inte bara ett lägre tidsmått. Dokumentera dessutom när källretentionen hade gjort återleverans omöjlig, eftersom ett godkänt test i en ideal miljö inte visar vad som händer när en verklig incident upptäcks sent.

Protokollet kompletteras med länkar till loggar, transaktions-/händelse-ID:n, ansvariga beslut, mätning av teknisk och verksamhetsmässig RTO samt en lista över kvarvarande risker. I en cyberincident räcker detta inte: då krävs också separat prövning av att återställda data och identiteter är betrodda.
