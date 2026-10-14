# 4. Dataägarskap och tillstånd i distribuerade system

Ett återställt ärende kan se korrekt ut i ärendetjänsten, men ändå saknas i handläggarens arbetslista. Ärendet finns; det är vyn som inte har uppdaterats. Det låter som ett mindre fel, tills någon använder arbetslistan som bevis för att ärendet aldrig kom in. För att kunna återställa ett distribuerat system måste vi skilja mellan **den information som beskriver vad som faktiskt gäller** och de representationer som andra tjänster använder för att utföra sitt arbete.

## 4.1 Ett ärende, flera sorters data

I vårt exempel registrerar ärendetjänsten E-417. Handläggningstjänsten behöver ärendets nummer och status för att fördela arbete. En söktjänst behöver rubrik, datum och sökbara attribut. Beslutstjänsten behöver underlag för prövningen. De kan lagra uppgifter om samma ärende utan att lagra *samma slags tillstånd*.

Anta att databaserna ser ut så här:

| Komponent | Innehåll | Roll vid återställning |
|---|---|---|
| Ärendetjänst | Registreringsuppgifter och registreringstid | Auktoritativt för registreringen enligt vår valda design |
| Handläggningstjänst | Tilldelning och handläggningsstatus | Auktoritativt för handläggningsarbetet |
| Sökindex | Sökbar kopia av ärendeuppgifter | Härlett; kan byggas om om underlaget finns |
| Cache | Tillfälligt lagrade svar | Normalt återuppbyggbar; ska inte användas som ensam källa |
| Revisionsspår | Registrerade beslut och ändringar | Kan vara kritiskt underlag, men hållbarheten beror på hur det lagras |

Tabellen är ett arkitekturval för vårt exempel, inte en universell modell. **Auktoritet måste bestämmas per uppgift och verksamhetshandling**, inte genom en regel om att en viss databas alltid är viktigast. Även en söktjänst kan äga egen, unik information, exempelvis manuella klassificeringar. Då är inte hela dess databas återuppbyggbar.

En mikroservice kan äga sitt schema eller sin dataåtkomst, men verksamhetens informationsansvar upphör inte. Att tekniken är decentraliserad innebär därför inte att sanningen får vara odefinierad.

## 4.2 En databas per tjänst är en gräns, inte en återställningsplan

En vanlig designprincip är att varje tjänst kontrollerar sin data och att andra tjänster använder dess API:er eller publicerade händelser. Det minskar kopplingen till interna tabeller och gör oberoende förändringar möjliga. Principen kräver inte en fysisk databasserver per tjänst: separata scheman och tydliga åtkomstgränser kan också förekomma.

Men uppdelningen skapar flera transaktionsgränser. Ärendetjänsten kan ha committat en registrering innan handläggningstjänsten hunnit ta emot beskedet. Därmed kan båda databaserna vara lokalt korrekta trots att de visar olika lägen. Under normal drift kan detta vara en avsiktlig, kortvarig fördröjning. Efter en återställning kan samma olikhet bli bestående om mekanismen för att sprida förändringen har gått förlorad.

Det är viktigt att inte tolka *eventual consistency* som att alla olikheter automatiskt läker. Konvergens förutsätter att nödvändiga uppdateringar faktiskt levereras, kan behandlas och inte blockeras av exempelvis felaktig ordning eller inkompatibla scheman. En återställd databas skapar inte i sig nya meddelanden som gått förlorade.

## 4.3 Primärt, härlett och temporärt – tre olika åtgärder

Vid ett omfattande avbrott bör drift och arkitektur kunna skilja tre frågor:

**Vilken information får inte förloras?** Registreringen, beslutsmotiveringen och spår som är nödvändiga för rättssäkerhet eller revision kan kräva backup, transaktionsloggar och särskild verifiering. En informationsklassning avgör vilka tillgänglighets-, integritets- och bevarandekrav som gäller.

**Vilken information kan återskapas?** Ett sökindex kan genereras på nytt från rätt källa, men bara om källan fortfarande finns, beräkningsreglerna är kompatibla och eventuella manuella tillägg hanteras. Rekonstruktion kan vara tidskrävande: ombyggnad under flera timmar påverkar verksamhetens RTO även om inget primärdata har förlorats.

**Vilken information ska hellre kastas?** En cache kan innehålla utdaterade kopior. Att återställa den från en äldre säkerhetskopia kan skapa fler fel än att tömma den, värma upp den på nytt och kontrollera hur tjänster hanterar tillfälligt cachebortfall.

Det följer en praktisk princip: **samma backupstrategi för alla datalager är sällan rätt återställningsstrategi**. Den konkreta klassningen, lagringsplattformarna och skyddsmekanismerna återkommer i kapitel 14.

## 4.4 Repliker löser ett annat problem

Anta att ärendedatabasen är replikerad mellan flera tillgänglighetszoner. Om en nod försvinner kan systemet fortsätta på en annan nod. Det är värdefullt, men säger inget säkert om förmågan att gå tillbaka efter ett felaktigt massuppdateringskommando. Replikering kan även föra det felaktiga tillståndet vidare.

En replika kan dessutom ligga efter den primära noden. Vid failover måste vi veta vilka skrivningar som faktiskt finns bevarade. Garantierna beror på synkron respektive asynkron replikering, konfiguration, felmodell och vilka bekräftelser som har lämnats. Att datat finns i två instanser är inte liktydigt med två oberoende historiska återställningspunkter.

Det är därför användbart att skilja mellan redundans för fortsatt drift, backup för att kunna återvända till äldre information och tillståndsrekonstruktion för att återfå en verksamhetsmässigt riktig bild.

## 4.5 Informationslivscykeln påverkar återställningen

Återställning av äldre data kan också återinföra uppgifter som tidigare har raderats eller rättats. En tekniskt korrekt restore måste därför följas av kontroller som återapplicerar giltiga raderings- och rättelsebeslut där det krävs. Det gäller både primära lagringsplatser och härledda kopior, inklusive sökindex. Kraven på bevarande, gallring och personuppgiftsbehandling måste analyseras utifrån tillämpliga regler och verksamhetens ändamål; det finns ingen enkel generell regel om att en säkerhetskopia ska raderas omedelbart när en enskild post tas bort i primärsystemet.

I E-417-fallet behöver vi alltså veta mer än om ärendedatabasen kunde startas: vilken komponent äger registreringsfaktumet, vad är en kopia, vad går att återskapa och hur hanteras förändringar som skedde efter backupögonblicket? Dessa frågor bestämmer vilket innehåll som måste skyddas. Nästa fråga är hur förändringarna färdas mellan tjänsterna.

## 4.6 När samma databas innehåller data med olika återställningskrav

En vanlig förenkling är att klassificera en hel databas som antingen auktoritativ eller härledd. Handläggningstjänstens databas visar varför det inte alltid fungerar. Tabellen `arbetsuppgift` kan innehålla beslut om ansvarig handläggare och sista svarsdatum som endast tjänsten äger. Tabellen `arende_sokvy` innehåller en kopia av ärendets rubrik och status, som kan byggas om från ärendetjänstens händelser. Tabellen `processed_message` visar vilka händelser som redan har påverkat arbetsuppgifterna.

Om samtliga tabeller återställs till klockan 10.00 förloras både lokala verksamhetsbeslut och kopierade data. Men deras återställningsvägar är olika: arbetsuppgifterna kräver backup eller en uttryckligt komplett auktoritativ historik; sökvyn kan rekonstrueras; behandlingsmarkörerna måste samordnas med både arbetsuppgifterna och återstartspunkten för konsumenten. Att bara återskapa sökvyn löser inte förlusten av ett handläggarbeslut.

En praktisk inventering behöver därför klassificera *datamängder* och deras beroenden, inte enbart applikationer och servrar. Frågorna är: Vem äger uppgiften? Vilken källa är bindande? Hur gammal får kopian vara? Vilken versions- eller positionsinformation krävs för säker rekonstruktion? Resultatet kan dokumenteras som ett kort återställningskontrakt för varje datamängd. Det ger driftteamet en karta över vad som måste läsas tillbaka och vad som med säkerhet kan beräknas om.
