# 3. Från teknisk återställning till verksamhetsmässig återställning

Klockan 10.10 har driftteamet återställt Ärendetjänstens databas och startat dess instanser. Databasen svarar, integrationernas nätverksanslutningar fungerar och övervakningen visar grönt. Ändå finns ärende E-417 i Handläggningstjänstens arbetskö men inte i Ärendetjänsten. Vad ska driftteamet rapportera: återställt eller inte återställt?

Svaret beror på vad vi lovade att återställa. Detta kapitel handlar om hur det löftet behöver formuleras och hur vi avgör om det är uppfyllt. Kapitel 2 visade varför olika tjänster kan befinna sig i olika skeden; här skiljer vi mellan ett **tillåtet mellanläge**, en **återställbar avvikelse** och ett **verksamhetsmässigt oacceptabelt resultat**.

## 3.1 Tre olika frågor som ofta förväxlas

När en incidentrapport anger att en tjänst har återställts kan påståendet avse minst tre skilda nivåer:

**Teknisk återställning:** Kör tjänsten, är databasen läsbar och finns nödvändiga nätverksvägar, hemligheter och behörigheter? Detta är avgörande, men säger inget fullständigt om verksamhetens data.

**Datamässig återställning:** Är lagrade data strukturellt och semantiskt rimliga? Finns de poster som borde finnas inom vald återställningsgräns, går referenser att följa och kan vi förklara förändringar som saknas? Databasens egen integritetskontroll kan godkänna en databas även när dess innehåll inte stämmer med tillståndet i en annan tjänst.

**Verksamhetsmässig återställning:** Kan viktiga verksamhetsprocesser fortsätta på ett korrekt och spårbart sätt, inklusive hantering av redan utförda externa åtgärder? Detta kan kräva komplettering av data, avstämning eller särskilt beslut om en avvikelse, inte bara teknisk omstart.

Dessa nivåer är inte tre alltid separata faser. Teknik och datakontroller kan behöva upprepas under återhämtningsarbetet. Poängen är att vi inte får använda en uppnådd nivå som bevis för de andra.

## 3.2 Definiera det som aldrig får bli fel

För vårt ärendesystem kan verksamheten formulera några grundläggande regler:

1. Varje fastställt beslut ska kunna knytas till ett identifierbart ärende och rätt beslutsunderlag.
2. Ett beslut får inte expedieras två gånger med oavsiktligt dubbla rättsverkningar.
3. Om en extern mottagare har kvitterat ett beslut måste det kunna spåras internt, även om en lokal databas har återställts.
4. Ett ärende får inte markeras som avslutat om nödvändiga verksamhetssteg fortfarande saknas, såvida processen uttryckligen medger detta.

Sådana regler kan beskrivas som **verksamhetsinvarianter**: egenskaper som måste gälla i ett godtagbart tillstånd. De är en brygga mellan verksamhetens krav och tekniska kontroller. Alla regler kan inte garanteras av en ensam databas. Flera kräver kunskap om flera tjänster och kanske en extern part.

Reglerna behöver också vara korrekta för den aktuella verksamheten. Exempelvis kan en omexpediering vara fullt tillåten om den uttryckligen är markerad som ersättningsbeslut. Kravet är alltså inte att en händelse aldrig får upprepas, utan att systemet aldrig utför en **oavsiktlig eller otillåten** upprepning.

### Pröva reglerna på E-417

Vi har följande observationer efter återställningen:

- Ärendetjänsten saknar E-417 eftersom dess databas återställts till före registreringen.
- Handläggningstjänsten har en arbetsuppgift kopplad till E-417.
- Händelseplattformen kan eventuellt fortfarande innehålla registreringshändelsen, men dess bevarandetid och faktisk tillgänglighet måste kontrolleras.
- Vi vet ännu inte om andra tjänster har gjort något med ärendet.

Arbetsuppgiften är inte automatiskt ett fel. Den är ett **tecken på att olika komponenter har olika historia**. Den korrekta åtgärden börjar med att utreda vilket förlopp som kan beläggas. Att radera arbetsuppgiften kan förvärra felet. Att skapa ärendet på nytt kan vara rätt, men bara om vi vet hur det påverkar eventuella redan utförda handlingar.

## 3.3 Den gemensamma klockan är inte samma sak som en gemensam historia

Anta att två databaser kan återställas till klockan 10.02. Det kan se samordnat ut på papperet. Men klockslag i backup- och loggsystem säger inte nödvändigtvis om en meddelandeöverföring hann behandlas före eller efter en viss lokal ändring. Två databaskopior som var för sig är giltiga kan fortfarande representera ett förlopp som aldrig existerade som globalt verksamhetstillstånd.

Det beror inte enbart på felaktigt synkroniserade klockor. Den avgörande frågan är **orsak och verkan**: om en mottagare har behandlat ett meddelande, vilket underlag hos avsändaren måste då kunna beläggas? Hur förklarar vi en kvittering när den händelse som kvitterades inte längre finns i den återställda avsändardatabasen?

För att hantera frågan behöver organisationen lämpliga identifierare och spår. Exempel är ärende-ID, händelse-ID, versionsnummer, korrelations-ID, leverans- och kvittensinformation samt beständiga processloggar. De ska kunna koppla samman ett förlopp; enbart detaljerade tekniska loggar med kort retention räcker inte alltid. Vi återkommer till kausalitet och tekniska avgränsningar i kapitel 6.

## 3.4 Sätt mål för ett verksamhetsflöde, inte bara för servrar

De klassiska måtten RPO och RTO från kapitel 1 är fortfarande relevanta. Men vi måste definiera *vad* de mäter.

En databas kan exempelvis ha RPO 15 minuter och en tjänst RTO två timmar, samtidigt som ett kritiskt beslutflöde kräver att inga fastställda beslut förloras utan upptäckt. Detta behöver inte betyda att beslutstjänstens databas måste ha RPO noll. Det kan betyda att en förlorad lokal post måste kunna rekonstrueras och verifieras från ett annat beständigt underlag inom en avtalad tid. Om verksamhetens krav verkligen är noll dataförlust måste arkitekturens garantier och felantaganden prövas särskilt; det går inte att uppnå genom att bara skriva »RPO 0« i en plan.

En användbar återställningsdefinition kan därför innehålla:

| Dimension | Exempel på beslutad acceptans |
|---|---|
| Tekniskt | Tjänster och nödvändiga beroenden kan startas i kompatibla versioner. |
| Informationsmässigt | Alla saknade ärenden inom det valda återställningsintervallet har identifierats. |
| Processmässigt | Inga fastställda beslut saknar spårbar processstatus. |
| Integrationsmässigt | Skickade och kvitterade beslut är avstämda mot externa mottagare. |
| Operativt | Nya ärenden släpps in först när återstående avvikelser är kontrollerade eller uttryckligen accepterade. |

Detta är exempel på kriterier, inte universella gränsvärden. Verksamhetsansvariga behöver ange vilka undantag som kan tolereras och vem som får acceptera dem.

## 3.5 En avstämning som går att genomföra

Återvänd till E-417. Innan ett beslut om återöppning kan fattas behöver vi en sammanhållen bild av vad som hänt. Ett möjligt undersökningsförfarande är:

**Fastställ räckvidden.** Vilka databaser och tjänster återställdes? Vilken tidpunkt och vilket loggmaterial användes? Vilka delar har fortsatt köra? Ett felaktigt antagande här kan få avstämningen att missa händelser.

**Samla belägg.** Ta fram ärende- och korrelationsidentifierare från oberoende tillgängliga underlag: beständiga händelser, revisionsspår, mottagningskvittenser och andra berörda tjänster. Separera verifierade fakta från antaganden. Det är viktigt att inte förväxla ett övervakningsspår med ett arkiv som garanterat överlevt händelsen.

**Klassificera avvikelser.** Finns informationen bara i fel tjänst, väntar ett meddelande på behandling eller saknas ett auktoritativt beslut? Skilj oskadliga fördröjningar från risk för fel rättsverkningar. Enstaka poster kan kräva manuell utredning.

**Besluta om åtgärd och ansvar.** Det kan handla om att rekonstruera en saknad post, bearbeta om en händelse, korrigera en processstatus eller kontakta extern part. Varje åtgärd måste bedömas för risken att orsaka nya bieffekter. Vi går in på mekanismerna för detta i senare kapitel.

**Verifiera innan flödet öppnas.** Kontrollera att verksamhetsreglerna håller för den berörda mängden och att eventuella kvarstående undantag är dokumenterade. Bestäm också hur uppföljning ska göras efter återstart.

En viktig princip är att avstämning inte bara ska bygga på att jämföra antal poster. Två system kan innehålla lika många ärenden men olika ärenden. Kontroll behöver ske med relevanta identiteter, tillstånd och kopplingar till utförda handlingar.

## 3.6 Tre möjliga resultat – inte bara grönt eller rött

Det finns situationer där allt kan återställas och avstämmas innan någon användare släpps in. Det är det enklaste fallet. Men för ett stort distribuerat system kan det vara rimligare att skilja mellan:

- **Fullt återställt:** De definierade verksamhetsreglerna är verifierade och kritiska processer kan återupptas utan särskilda begränsningar.
- **Kontrollerat begränsat läge:** Vissa funktioner öppnas medan identifierade avvikelser hanteras, med beslutade spärrar, övervakning och ansvar.
- **Ej godkänt för återöppning:** Underlag saknas, riskerna är okända eller viktiga verksamhetsregler kan inte verifieras.

En sådan modell kräver förstås att behöriga roller har mandat att avgöra vilken risk som kan accepteras. Den får inte användas för att normalisera okända dataförluster. Om ett beslut kan ge juridiska eller ekonomiska konsekvenser kan kravet på kontroll vara betydligt strängare än för en försenad sökvy.

Det är här återställningsförmåga tydligt övergår från att vara en fråga om driftverktyg till att vara en **egenskap hos systemets och verksamhetens samlade utformning**. Om arkitekturen inte lagrar användbara identifierare, om den saknar beständiga spår eller om den kan utlösa externa effekter utan möjlighet till avstämning, går problemet inte att reparera med enbart bättre backupmjukvara.

Vi behöver alltså veta vilket tillstånd som är auktoritativt, vilka tillstånd som bara är härledda och vilka processer som måste kunna rekonstrueras. Det tar oss vidare till kapitel 4: vem äger egentligen data i det distribuerade systemet?
