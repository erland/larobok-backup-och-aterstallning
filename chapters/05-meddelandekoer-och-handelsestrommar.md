# 5. Meddelandeköer och händelseströmmar

Ärendet E-417 har registrerats och ärendetjänsten skickar händelsen `ÄrendeRegistrerat`. Handläggningstjänsten är tillfälligt nere. När den kommer tillbaka måste den få reda på att ärendet finns. Huruvida det sker beror inte bara på backup av databaserna, utan på **vilken sorts meddelandesystem vi använder och vilka garantier som faktiskt är konfigurerade**.

## 5.1 En kö och en logg ger olika återställningsmöjligheter

I en traditionell arbetskö fördelas meddelanden till konsumenter. Efter korrekt bekräftad bearbetning tas meddelanden typiskt bort från den aktiva kön eller blir inte längre tillgängliga som normalt köarbete. Om handläggningstjänsten behöver göra om jobbet flera dagar senare är det alltså inte säkert att samma meddelande finns kvar.

En loggbaserad händelseström, exempelvis i Kafka, behåller poster enligt konfigurerade regler för retention och eventuellt kompaktering. Olika konsumentgrupper kan där läsa samma poster med egna positioner. Det ger möjligheter att läsa om historik, men *inte* ett löfte om obegränsad historik eller en komplett revisionslogg.

| Fråga | Arbetskö | Loggbaserad ström |
|---|---|---|
| Vad styr normalt konsumtionen? | Leverans och bekräftelse av arbete | Position i en ordnad logg, typiskt per partition |
| Kan en konsument läsa om allt? | Inte utan särskild lagring eller omköning | Bara så länge relevanta poster finns kvar och kan läsas |
| Vilken risk måste bedömas? | Att meddelanden bekräftas för tidigt eller försvinner vid felaktig hantering | Att data förfaller, kompakteras eller att positioner hanteras fel |
| Vad måste skyddas? | Relevant köinnehåll och leveranstillstånd enligt brokerfunktioner | Relevanta loggposter, metadata och konsumentpositioner enligt återställningsstrategin |

En kö kan vara beständig, replikerad och mycket tillförlitlig; en ström kan ha kort retention. Produktnamnet räcker därför aldrig som bevis för en viss återställningsförmåga.

## 5.2 Publicerad är inte detsamma som säkert mottagen

Betrakta två tidpunkter. Klockan 10.01 committar ärendetjänsten E-417 till sin databas. Klockan 10.01.01 försöker den publicera `ÄrendeRegistrerat`. Om processen kraschar mellan dessa steg kan databasen visa registreringen medan ingen händelse har publicerats. Detta kallas ibland *dual-write-problemet*. Att göra databasskrivning och extern publicering som två separata steg ger normalt ingen gemensam atomär transaktion.

Även om applikationen skickar händelsen kan nätverket fallera innan den får svar. Ett uteblivet kvitto bevisar då inte att brokern saknar händelsen. Att skicka igen kan skapa ett duplikat.

På brokernivå behöver vi skilja mellan att meddelandet skickats till ett nätverksuttag, att en broker har accepterat det och att det lagrats med den hållbarhet som krävs. RabbitMQ:s *publisher confirms* är ett exempel på en mekanism för publiceringskvittenser. Exakt när kvittens lämnas varierar med kötyp och konfiguration. Bekräftelse från brokern är fortfarande inte bevis för att verksamhetsmottagaren har utfört sin åtgärd.

I kapitel 9 behandlar vi mönster som knyter ihop databasändringar och publiceringsavsikt på ett säkrare sätt. Här räcker det att se återställningskonsekvensen: **om ett affärsfaktum överlever men dess händelse saknas, kan en mottagartjänst bli permanent inaktuell**.

## 5.3 En bekräftelse från konsumenten måste ha rätt betydelse

Anta att handläggningstjänsten får meddelandet. Den läser det och svarar omedelbart med en bekräftelse, men kraschar sedan innan den lagrat arbetsuppgiften. Om brokern tolkar bekräftelsen som färdig bearbetning kan händelsen vara borta från arbetskön medan arbetet saknas i databasen.

Den omvända ordningen har ett annat fel: handläggningstjänsten lagrar arbetsuppgiften och kraschar innan den bekräftar. Då kan meddelandet levereras igen. Den vanliga säkra utgångspunkten är därför att acceptera möjligheten till **minst en leverans** och utforma behandlingen så att upprepningar inte orsakar dubbel verksamhetseffekt. Detta är grunden för idempotens och inkorgsmönster, som vi utvecklar i kapitel 8–9.

RabbitMQ:s konsumentbekräftelser och Kafkas commit av konsumentpositioner har olika mekanik. De bör inte beskrivas som om de vore samma sak. I Kafka kan offset-commit ske separat från applikationens databasskrivning. En för tidig commit kan leda till utebliven bearbetning efter omstart; en sen commit kan leda till ombearbetning.

## 5.4 Retention, dead-letter och ordning

När en händelse inte kan behandlas kan den hamna i en dead-letter queue, beroende på produkt och regler. Den kön måste själv ha ägarskap, retention, övervakning och rutiner. Att meddelandet flyttats dit betyder inte att verksamhetsflödet är räddat. Ingen återställning är färdig förrän vi vet om den aktuella händelsen ska repareras, spelas om, undantas eller eskaleras.

I loggbaserade strömmar är ordningen vanligtvis garanterad *inom en partition*, inte för hela systemet. För E-417 kan flera händelser därför behöva en stabil nyckel om deras inbördes ordning spelar roll. Men rätt partitionsnyckel kan inte ge atomisk samordning mellan två självständiga tjänster eller två olika strömmar.

En återställningsplan behöver också känna till att loggar kan ha begränsad retention. Om konsumenten återgår till en offset vars poster inte längre finns, hjälper det inte att dess gamla offset är väl dokumenterad. Ett retentionfönster ska därför relateras till realistisk återställningstid, avbrottslängd och behov av ombearbetning.

## 5.5 Vad vi måste kunna besvara efter haveriet

För händelsen `ÄrendeRegistrerat` behöver vi svar på fyra skilda frågor:

1. Finns registreringen säkert bevarad hos den som äger den?
2. Publicerades händelsen, och vilket pålitligt belägg har vi för det?
3. Finns händelsen fortfarande tillgänglig för den konsument som behöver den?
4. Har handläggningstjänsten utfört sin verksamhetsåtgärd, eller bara tagit emot meddelandet?

Vi får inte dra slutsatsen att allt är klart bara för att en kö är tom, eller att inget är gjort för att en offset ligger efter. Köinnehåll, positionsmetadata och verksamhetstillstånd svarar på olika frågor.

Nu kan vi se varför distribuerad återställning inte bara är en fråga om *vilka* data som bevaras. Vi måste också förstå *när* beroende händelser inträffade. Det är ämnet för kapitel 6.
