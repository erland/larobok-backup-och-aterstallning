# 16. Säkerhet, cyberangrepp och återställning

Ärendeplattformen är otillgänglig. Först ser det ut som ett omfattande driftfel, men loggar visar att en angripare har använt ett administratörskonto för att ändra konfiguration, radera säkerhetskopior och manipulera vissa ärendeposter. En reservregion finns, och databasen kan tekniskt återställas. Problemet är att ingen säkert vet när intrånget började eller vilka autentiseringsuppgifter och datamängder som kan ha påverkats.

Vid ett vanligt driftavbrott behöver vi framför allt återfå funktion och konsistens. Efter ett cyberangrepp måste vi först också kunna svara på en annan fråga: **Varför skulle vi lita på det vi återställer?** Det förändrar både arbetsordningen och kriterierna för att verksamheten får öppnas igen.

## 16.1 Skydda återställningen från det som orsakat incidenten

Om angriparen fortfarande har tillgång till identiteter, administrationsverktyg eller repliker kan en för snabb återställning återskapa samma sårbarhet och leda till ett nytt angrepp. Incidenthantering och återställning måste därför samordnas. Åtgärder för inneslutning och bevarande av bevis kan behöva föregå återkoppling till produktion.

Det kan innebära att isolera drabbade miljöer, stoppa komprometterade konton, bevara relevanta loggar och systemavbilder samt identifiera kända intrångsvägar. Åtgärderna bör beslutas tillsammans med incidentledning och forensisk kompetens; att godtyckligt radera eller installera om drabbade system kan förstöra värdefull bevisning. Isolering innebär inte automatiskt att angriparen är borta.

Skillnaden mot kapitel 15 är därmed viktig: där handlar kontrollerna huvudsakligen om att få komponenter och verksamhetstillstånd att stämma. Här måste själva **tillitskedjan** etableras innan komponenterna åter får agera.

## 16.2 En fungerande backup kan innehålla fel eller angrepp

En säkerhetskopia kan vara tekniskt läsbar men innehålla angriparens bakdörrar, manipulerade data eller redan stulna autentiseringsuppgifter. Även en oföränderlig backup kan ha tagits efter att angriparen fått tillgång. Immutability skyddar främst mot att kopian i efterhand ändras eller raderas inom den definierade skyddsmodellen; den bevisar inte att innehållet är korrekt eller rent.

Därför behöver backupstrategin skilja på flera skyddsbehov:

- **Oberoende kopior:** Separata säkerhetsdomäner, konton eller miljöer som inte alla kan administreras med samma komprometterade behörighet.
- **Motstånd mot radering:** Oföränderlig lagring, offlinekopior eller tekniskt och organisatoriskt kontrollerade spärrar för borttagning.
- **Återställbarhet:** Dokumenterade nycklar, verktyg, läsbara format, återställningstester och tillgång till rätt applikationsversion.
- **Spårbar proveniens:** Tidpunkt, ursprung, verifierade kontrollsummor, åtkomstloggar och information om vilka system som var betrodda när kopian skapades.

En krypterad säkerhetskopia är värdefull för sekretess, men om krypteringsnyckeln förstörs eller blir otillgänglig kan kopian ändå vara oanvändbar. Om samma identitet kan radera både produktionsdata och backup riskerar en angripare att slå ut båda. Dessa frågor måste designas innan incidenten inträffar.

## 16.3 Välj en återställningspunkt som är tillräckligt betrodd

Anta att ärende E-417 ändrades den 12 oktober, att intrånget upptäcktes den 14 oktober och att den senaste rena återställningspunkten ännu inte är känd. Att enbart välja kopian med minst dataförlust riskerar att återinföra manipulationen. Att välja den äldsta kopian riskerar samtidigt att tappa legitima verksamhetshändelser och kan göra återställningen oacceptabel.

Analysen behöver därför kombinera tekniska indikatorer, revisionsspår, loggar och verksamhetskontroller. En äldre, mer betrodd databas kan återställas i en isolerad miljö. Legitima förändringar efter denna punkt kan sedan rekonstrueras från särskilt granskade, oberoende källor, exempelvis kvittenser från en extern mottagare eller bevarade journalposter. Händelseloggar som kan ha manipulerats får inte automatiskt behandlas som sanningskälla.

Det finns ingen allmän algoritm som alltid hittar ”sista rena kopian”. Resultatet måste beskriva vad som är styrkt, vad som är sannolikt och vad som fortfarande är osäkert. Ett beslut om att acceptera kvarvarande dataosäkerhet hör hemma hos den ansvariga verksamheten och incidentledningen, inte enbart hos den som utför restore-kommandot.

## 16.4 Bygg en ren återställningsmiljö – inte en kopia av den komprometterade

En separat återställningsmiljö bör etableras från betrodda, versionsstyrda installationskällor. Infrastrukturkod, images, paket och beroenden måste kontrolleras så att den återuppbyggda miljön inte använder angriparens ändrade konfiguration. Nödvändiga identiteter och hemligheter behöver roteras eller utfärdas på nytt utifrån en riskbedömning, särskilt om privilegierade konton kan ha exponerats.

En typisk kontrollerad process omfattar:

1. Etablera isolerat nät och administrationsvägar med betrodda identiteter.
2. Återskapa plattformen från granskade artefakter och kända konfigurationsversioner.
3. Välj och kontrollera säkerhetskopior utan att ge den tidigare miljön tillgång till den nya.
4. Återställ data och verifiera både teknisk integritet och verksamhetsmässig rimlighet.
5. Inventera osäkra externa åtgärder och genomför avstämning innan motsvarande integrationer öppnas.
6. Aktivera övervakning, spårbarhet och förstärkta skyddskontroller innan begränsad produktionsdrift återupptas.

Vilka steg som kan parallelliseras beror på incidentens omfattning. Det kritiska är att återställningen inte oavsiktligt ansluter betrodda resurser till kvarvarande komprometterade delar. CISA:s vägledning om ransomware betonar bland annat offline- och skyddade säkerhetskopior, testade restore-förfaranden och försiktighet så att rena miljöer inte återinfekteras.

## 16.5 Händelsedrivna system har särskilda angreppsytor vid återställning

I en distribuerad arkitektur kan meddelandekön innehålla både legitima och manipulerade händelser. En automatiserad replay kan därför återskapa oönskade databasändringar eller initiera handlingar med externa följder. En outbox kan bära ännu opublicerade instruktioner från en angripares session. Konsumentpositioner och dedupliceringsmarkörer kan dessutom ha ändrats för att dölja eller upprepa behandling.

Efter en cyberincident bör teamet därför kunna sätta meddelandeflöden i karantän och analysera källidentitet, tidslinje, händelseinnehåll och beroenden före eventuell återleverans. Alla händelser kan inte automatiskt klassas som skadliga eller ofarliga utifrån en tidsgräns: en angripare kan ha varit närvarande långt före upptäckten. Att rensa hela strömmen kan å andra sidan förstöra viktig historik.

Samma princip gäller externa integrationer. Om ett beslut skickats under den komprometterade perioden kan det krävas kontakt med motparten för att fastställa mottaget och verkställt resultat. Att lokalt backa en databas återkallar inte en redan genomförd handling. I vissa verksamheter kan korrigering dessutom kräva formella beslut och särskild dokumentation.

## 16.6 Vad är ett godtagbart återställningsbevis?

En lyckad restore från en backupfil är bara ett delresultat. Innan öppning bör organisationen kunna redovisa vilka delar av intrånget som identifierats och inneslutits, varför installationskällor och kopior bedöms tillräckligt tillförlitliga, vilka uppgifter som kontrollerats mot oberoende källor och vilka risker som kvarstår.

För E-417 innebär detta till exempel att ärendets historik går att följa, att bilagorna är tillgängliga och rimliga, att en eventuell extern expediering är avstämd och att tjänsten inte längre använder komprometterade identiteter. Ett grönt tekniskt test är inte liktydigt med att informationen är autentisk eller att all dataexfiltration har kartlagts.

Det krävs ofta en dokumenterad verksamhets- och säkerhetsmässig acceptans innan systemet kan öppnas stegvis. Krav på incidentrapportering, bevarande av bevis, dataskydd eller särskilda verksamhetsbeslut måste bedömas enligt de regelverk som gäller för organisationen; de följer inte automatiskt av en generell DR-metod.

## 16.7 Förberedelserna avgör hur mycket som går att rädda

När ett cyberangrepp har inträffat kan det vara för sent att införa oberoende backupbehörigheter, kontrollera gamla installationspaket eller försöka skapa ett tillförlitligt revisionsspår. Därför bör återställningsarkitekturen på förhand innefatta en administrativt separerad backupmiljö, testad tillgång till krypteringsnycklar, versionsstyrda byggartefakter, skyddade loggar och en plan för isolerad återuppbyggnad.

NIST SP 800-184 behandlar hur återhämtningsplanering efter cyberincidenter behöver omfatta beroenden, ansvar, realistiska scenarier och kontinuerlig förbättring. Den poängen är särskilt relevant i moderna arkitekturer: det räcker inte att kunna återskapa servrarna; man måste också kunna **återupprätta förtroendet för informationen och för de processer som ska använda den**.

I nästa del av boken går vi från tekniska och arkitektoniska förutsättningar till genomförande: hur återställningsarbetet planeras, övas och styrs så att det går att fatta rätt beslut under tidspress.
