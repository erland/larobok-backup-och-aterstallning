# Inledning – När en lyckad återställning ändå blir fel

Klockan 08.40 upptäcker driftteamet att en databas har skadats. En tjänst som hanterar beslut i ett ärendesystem går inte längre att använda. Teamet isolerar felet, återställer en säkerhetskopia och spelar fram de tillgängliga transaktionsloggarna till klockan 08.15. Databasen klarar integritetskontrollerna. Applikationen startar. Övervakningen visar grönt.

Klockan 09.20 ringer en handläggare. Ett beslut som hon nyss fick bekräftat från en extern mottagare går inte längre att hitta i systemet. En annan handläggare ser ett ärende som ser obeslutat ut, trots att ett meddelande om beslut redan har skickats. Driftteamet har inte gjort något uppenbart fel. Återställningen återskapade precis det tillstånd som backup- och loggmaterialet medgav. Ändå är verksamhetens läge oklart.

Detta är ett fiktivt scenario, men problemet är högst konkret: *vilket tillstånd var det egentligen som skulle återställas?* Databasen eller ärendets samlade historia, också den som redan påverkat andra system?

## Från återställd komponent till fungerande verksamhet

I många äldre system finns huvuddelen av ett verksamhetsförlopps data inom en databas eller ett tätt samordnat applikationslandskap. En kontrollerad återställningspunkt kan då ge en begriplig utgångspunkt: stoppa inflödet, återställ datan, återför identifierade filer eller batchar och kontrollera resultatet innan arbetet återupptas. Detta var aldrig helt problemfritt. Externa system, köer och filer kunde även då ligga i otakt. Men gränserna för vad som skulle samordnas var ofta tydliga och antalet självständiga tillståndslager relativt begränsat.

I ett modernt IT-stöd kan samma ärende beröras av flera mikrotjänster med egna databaser. En händelse om beslutet kan skickas till en meddelandeplattform, behandlas senare av en aviseringstjänst och dessutom vidarebefordras till en annan organisation. Vissa delar av processen är genomförda, andra pågår. Att återställa en tjänsts databas förändrar inte automatiskt det som redan har skett utanför den databasen.

Därför behöver vi skilja på tre resultat: en **tekniskt startbar miljö**, ett **datatillstånd som uppfyller systemets regler** och ett **verksamhetsförlopp som går att fortsätta på ett korrekt sätt**. Resultaten hänger ihop, men det ena garanterar inte det andra.

## Vad som faktiskt förändras

Vi behöver fortfarande fungerande säkerhetskopior, tillförlitlig lagring, dokumenterade återställningssteg och tydliga mål för acceptabel dataförlust och avbrottstid. Det nya är inte att backup slutar vara viktig. Det är att backup ensam inte beskriver hur ett fördelat verksamhetstillstånd kan återskapas.

Återställningsbarhet blir därför en gemensam arkitektur- och driftfråga. Applikationer behöver kunna känna igen tidigare behandlade meddelanden, återuppta avbruten bearbetning och stämma av mot externa mottagare. Plattformen behöver kunna återskapa både data och relevanta körförutsättningar. Driftorganisationen behöver veta i vilken ordning olika flöden kan öppnas och hur resultatet verifieras. Vilken åtgärd som behövs beror på systemets faktiska gränser och tekniska garantier.

Boken visar inte att traditionell backup är fel. Den visar *när dess antaganden är tillräckliga, när de inte längre är det och vilka kompletterande förmågor som då krävs*.

## Vem boken är till för

Boken vänder sig till lösnings- och IT-arkitekter, driftansvariga, plattformsansvariga och tekniska beslutsfattare som redan känner till grundläggande backup, databaser och integrationer. Du behöver inte ha byggt en mikrotjänstplattform eller administrerat en viss meddelandemäklare. Utgångspunkten är i stället dina befintliga kunskaper: vad brukar gå att säkerhetskopiera, vilken återställningspunkt kan vi nå och hur vet vi att systemet fungerar efteråt?

Vi använder genomgående en fiktiv ärendeplattform. Den börjar som ett relativt sammanhållet system och utvecklas senare till tjänster för ärenden, handläggning, beslut, aviseringar och externa integrationer. Fallen är förenklingar som låter oss isolera ett problem i taget. Särskilt viktigt är att skilja på en tekniks principiella möjligheter och vad en bestämd installation faktiskt garanterar.

De första kapitlen etablerar den traditionella referensramen och visar vad som händer när systemet delas upp. Därefter följer data, meddelanden och konsistens, applikationsmönster för återställning, plattforms- och backupfrågor samt praktisk återställning, testning och ansvar. Bilagorna ger checklistor och begreppsöversikter. Läs boken i ordning för att följa resonemanget, eller använd senare delar som stöd vid design och planering.

Vi börjar där många läsare redan är hemma: i ett system vars viktigaste data, transaktioner och integrationsfönster går att avgränsa. Vad är det egentligen som gör återställningen hanterbar där?
