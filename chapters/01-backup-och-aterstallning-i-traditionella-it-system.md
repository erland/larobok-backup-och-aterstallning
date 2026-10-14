# 1. Backup och återställning i traditionella IT-system

En erfaren driftansvarig känner igen situationen: nattens säkerhetskopiering är godkänd, databasens transaktionsloggar arkiveras och för varje kritiskt system finns en dokumenterad återställningsplan. Om något går sönder kan man identifiera en återställningspunkt, genomföra återläsningen och kontrollera att applikationen fungerar. Ofta är detta ett välgrundat arbetssätt. För att förstå vad som förändras i moderna system behöver vi först förstå *varför* det fungerar.

Det avgörande är inte att systemet är gammalt eller monolitiskt. Det är att dess tillstånd, förändringar och beroenden kan avgränsas och samordnas på ett sätt som gör återställningen begriplig.

## 1.1 En välkänd driftmodell

Tänk dig ett ärendehanteringssystem med en central relationsdatabas, ett applikationslager och två planerade integrationsflöden. Under dagen registrerar handläggare ärenden och beslut. På kvällen läser systemet en fil med uppdateringar från en annan organisation. Varje natt skapas en fil med dagens avslutade ärenden och skickas vidare till ett mottagande system.

Kärnan i den löpande bearbetningen finns i applikationen och databasen. En ärendetransaktion kan exempelvis lägga till ett beslut och ändra ärendets status inom samma databastransaktion. Om transaktionen avbryts ska databasen antingen bevara det tidigare tillståndet eller genomföra hela förändringen enligt databasens transaktionsgarantier. Den egenskapen gör en väsentlig skillnad: man behöver inte själv sammanställa ett giltigt beslutstillstånd ur flera halvfärdiga databasuppdateringar.

Filutbytena ligger däremot utanför databasens transaktion. De kräver redan här egna regler för spårbarhet och återkörning. Om en exportfil levererats men databasen senare återställs till före exporten är mottagarens kopia inte automatiskt återställd. Traditionella lösningar har därför ofta avstämningslistor, körningsjournaler, kontrollsummeringar och rutiner för omleverans. Dessa är viktiga föregångare till de mekanismer som senare blir centrala i händelsedrivna system.

## 1.2 Vad en säkerhetskopia faktiskt ger

En backup är ett underlag för att återskapa data. Den är inte i sig ett bevis på att hela verksamhetssystemet kan tas i bruk. Återställning förutsätter också att säkerhetskopian är tillgänglig, att rätt verktyg och behörigheter finns, att versioner och beroenden passar ihop och att resultatet kan kontrolleras.

Förenklat finns tre vanliga former av återställningsunderlag:

- **Fullständiga säkerhetskopior** ger en avgränsad bas att återläsa. Om en kopia tas medan data förändras måste metoden hantera dessa samtidiga skrivningar korrekt.
- **Inkrementella eller differentiella säkerhetskopior** kan minska mängden data som behöver kopieras men skapar beroenden till andra säkerhetskopior. Exakt terminologi och återställningsordning beror på produkten.
- **Transaktions- eller ändringsloggar** kan i många databassystem användas för att föra återläst data framåt från en basbackup. Hur långt det går beror bland annat på om loggkedjan är komplett och om tekniken stödjer önskad återställningspunkt.

I PostgreSQL går det exempelvis att kombinera en basbackup med arkiverade WAL-filer (*write-ahead log*) för point-in-time recovery, PITR. Förfarandet kräver relevant och sammanhängande loggmaterial. En vanlig logisk export från `pg_dump` är inte samma slags basbackup och kan inte användas som startpunkt för WAL-baserad PITR. Detta är en produktspecifik illustration, inte en regel för alla databaser.

En viktig distinktion är **krasch-konsistent** kontra **applikationskonsistent** kopia. En krasch-konsistent kopia kan motsvara tillståndet efter ett plötsligt strömavbrott; databasen kan i många fall behöva använda sin egen återställningslogik. En applikationskonsistent kopia är tagen med sådan samordning att berörda applikationer har nått ett avsett konsistent läge. En lagringssnapshot av flera volymer är inte automatiskt en samordnad verksamhetsmässig ögonblicksbild. Man måste veta vilken garanti backupmetoden verkligen erbjuder.

## 1.3 Att välja återställningspunkt

Två välkända mått ramar in arbetet:

**RPO (Recovery Point Objective)** beskriver den högsta acceptabla dataförlusten uttryckt som tid mellan den senaste återställbara punkten och störningen. Ett RPO på 15 minuter betyder alltså inte att exakt 15 minuters data går förlorade, utan att lösningen är avsedd att begränsa förlusten till högst den nivån under de antagna förutsättningarna.

**RTO (Recovery Time Objective)** beskriver den målsatta längsta tiden tills den definierade verksamhetsfunktionen ska vara återställd efter en störning. Start- och slutpunkt måste vara tydligt definierade; att databasen startar är inte nödvändigtvis samma sak som att tjänsten åter är användbar.

Anta att ärendesystemet havererar klockan 10.00. Basbackupen från natten är användbar och loggar finns till 09.55. Det kan vara möjligt att återställa databasen nära 09.55, alltså med omkring fem minuters förlust av databasskrivningar. Men vad händer med filen som skickades 09.58? Den kan innehålla uppgifter som inte längre finns i den återställda databasen. Även när ett databassystem uppfyller ett femminuters-RPO kan verksamheten behöva en avstämning utanför databasen.

Här ser vi den första avgränsningen som följer oss genom boken: **ett RPO för en databas är inte automatiskt ett RPO för ett helt verksamhetsflöde**.

## 1.4 En kontrollerad återställning av ärendesystemet

Vi använder nu ett avgränsat exempel. Klockan 13.00 orsakar ett fel i ärendesystemets databas att nya registreringar stoppas. Driftteamet beslutar att återställa till 12.45. Under förmiddagen har ett inkommande filflöde körts klart klockan 11.00. Nästa export sker först på kvällen.

Återställningsarbetet kan då organiseras kring tydliga gränser:

1. **Stoppa förändringar och dokumentera läget.** Stäng av ny ärendehantering och tillhörande batchjobb, men bevara spår som behövs för att förstå vad som hunnit göras.
2. **Välj en verifierbart återställbar punkt.** Kontrollera basbackup, loggar, kompatibla systemversioner och att stopptidpunkten är tekniskt möjlig.
3. **Återskapa databasen och beroenden.** Återläs materialet enligt databasteknikens procedur; kontrollera databasintegritet och applikationens förutsättningar.
4. **Stäm av integrationsgränserna.** Kontrollera särskilt att filen från 11.00 är hanterad och att ingen export eller annan extern effekt har skett efter den valda återställningspunkten utan att det kan förklaras.
5. **Verifiera och öppna kontrollerat.** Genomför både tekniska tester och ett urval verksamhetskontroller innan inflöde och planerade jobb återupptas.

Det här är inte en universell körinstruktion, utan en modell för vad som behöver vara känt. Om filen hade skickats klockan 12.55 skulle återställningen bli svårare. Man måste då identifiera vilket innehåll mottagaren fått och avgöra om data ska återföras, exporten korrigeras eller förloppet hanteras på annat sätt. Att köra om filen utan avstämning kan skapa dubbletter. Problemet fanns alltså redan i den traditionella modellen; det var bara oftare avgränsat till ett identifierbart fil- eller batchfönster.

## 1.5 Varför modellen ofta är hanterbar

I det beskrivna systemet finns ett antal egenskaper som förenklar återställningen:

**En central transaktionsgräns.** Många viktiga förändringar görs atomärt i samma databas. Man behöver inte samordna separata databaser för att avgöra om ett beslut har registrerats.

**Kända integrationsfönster.** Ett filutbyte sker på planerade tider. Det blir möjligt att dokumentera vilka externa effekter som kan ha inträffat efter den valda återställningspunkten.

**Begränsat antal auktoritativa datakällor.** Det går normalt att identifiera vilken databas som bär originaluppgifter och vilka rapporter eller sökindex som kan återskapas ur den.

**Tydliga återstartspunkter.** Batchjobb och filöverföringar kan ofta pausas, spåras och återupptas utifrån dokumenterade körnings-ID:n, kontrollposter eller kvittenser.

Dessa egenskaper är inte garanterade bara för att ett system är en monolit. Ett äldre system med många externa beroenden, asynkrona integrationsköer eller svårspårade sidoeffekter kan vara lika komplicerat att återställa som ett nyare system. Omvänt kan en modern tjänst med ett enda datalager vara relativt enkel att återställa. Det är därför bättre att tala om **samordningsbarhet och tillståndsgränser** än att dela upp världen i enkelt gammalt och svårt nytt.

## 1.6 När förutsättningarna börjar försvinna

Föreställ dig nu att ärendehanteringen delas upp. En tjänst tar emot ärenden i en databas. En annan registrerar beslut i sin egen databas. En tredje tar emot händelser och skickar aviseringar. Integrationer med andra organisationer sker löpande i stället för en gång per dygn.

I detta landskap är det fortfarande möjligt att säkerhetskopiera varje databas. Problemet är vad kopiorna *tillsammans* betyder. Beslutstjänsten kan återställas till före ett beslut medan ärendetjänsten och en extern mottagare redan har gått vidare. Ett meddelande kan vara avsänt, levererat eller behandlat på en annan tidslinje än databaskopian. Det går inte att förutsätta att samma klockslag i alla system motsvarar en gemensam, verksamhetsmässigt giltig återställningspunkt.

Det är inte ett argument mot mikroservicetjänster eller asynkrona integrationer. De kan ge god skalbarhet, självständighet och robusthet. Men de flyttar en del ansvar från en central transaktions- och återställningsgräns till systemets arkitektur: hur förändringar spåras, hur meddelanden behandlas och hur processer kan fortsätta när komponenter ligger i otakt.

Det är precis denna förskjutning som nästa kapitel undersöker. Vi tar det bekanta ärendesystemet och bryter upp det stegvis, utan att ännu introducera en katalog av lösningsmönster. Först behöver vi se var de gamla antagandena slutar hålla.
