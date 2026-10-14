# Samlad manusgranskning – revision 12

Granskningen omfattar inledning, kapitel 1–20 och bilaga A–F. Huvudkapitlen är oförändrade i denna revision; eventuella framtida innehållsändringar ska få separat revision.

## Progression och avgränsning

- Inledning–3: läsarens övergång från teknisk återläsning till verksamhetsmässigt korrekt återställning.
- 4–6: auktoritativa data, händelsebärare och kausala beroenden.
- 7–11: återbyggnad, återstart, tillförlitlig publicering, Saga och externa konsekvenser.
- 12–14: arkitekturkrav, plattform och skyddsmetod per datatyp.
- 15–18: katastrofåterställning, cyberincident, operativt genomförande och testning.
- 19–20: beslutsansvar och stegvis organisationsförändring.
- Bilagorna ger definitions- och arbetsstöd och ersätter inte huvudkapitlens argumentation.

## Automatiserade redaktionella stickprov

- Totalt antal ord (inklusive bilagor): 23747.
- Huvudtextens ungefärliga ordantal: 21504.
- Exakta längre textstycken som återkommer i två olika huvudkapitel: 0.
- Kvarvarande indikationer på platshållare eller redaktionella arbetsrubriker: 0 dokument (se kontrollens begränsningar).

## Manuell redaktionell granskning

Skillnaden mellan teknisk och verksamhetsmässig återställning återkommer som bokens röda tråd, men behöver inte definieras från början i varje kapitel. Fokus ligger på att varje kapitel ger ett eget besluts- eller teknikbidrag. Bilagorna är avsiktligt punktvisa uppslags- och granskningsverktyg och återanvänder därför vissa fackord från huvudtexten. Det är funktionell repetition, inte omtag i berättelsen.

## Kvarstående kvalitetsfrågor

- Manusets huvudkapitel är relativt korta jämfört med den tidiga omfattningsidén. Texten bör inte fyllas ut till ett sidmål utan nytt sakligt innehåll. Bedöm boklängd efter provlayout.
- Produkt- och versionsspecifika återställningsförfaranden måste verifieras för målmiljön före praktiskt bruk.
- Beskrivningen av NIST SP 800-61 ska gälla revision 3 (2025), inte äldre revision 2.
- Författare saknas ännu i `book.yaml`; av den anledningen är provexport inte ett godkännande för publicering.
- Fullständig sid-för-sid- och EPUB-läsgranskning behövs inför release.


## Riktad fördjupning, revision 13

Bedömning: det mesta av manus har lämnats orört. De tidigare identifierade luckorna har adresserats med en kausal tidslinje (kapitel 6), datamängdsklassificering (4), ett processkort (10), ett ADR-exempel (12), en regionåterstart (13), två backupfall (14), en beslutsstyrd DR-sekvens (15), ett misslyckat/omtestat scenario (18) samt dokumenterad övning (bilaga E). Kontrollera särskilt under slutläsning att begreppen ”auktoritativ källa”, ”avstämning” och ”återöppning” används konsekvent och inte blandas med backupmediets integritet.


## Slutläsning och provexport – revision 14

Genomgången omfattar inledning, 20 huvudkapitel och sex bilagor efter fördjupningarna i revision 13. Ingen ytterligare utfyllnad har lagts till i boktexten. Begreppsflödet är sammanhängande: auktoritativa data -> konsistens och återspelning -> idempotent tjänstedesign -> driftplattform/backup -> återställningsbeslut och verifiering. Kontroll av identiska textsekvenser om minst 35 ord mellan skilda kapitel gav inga träffar. Detta är ingen garanti mot semantiska upprepningar, men övergångarna är tydligt ämnesavgränsade. Ingen kvarvarande arbetsplatshållare hittades i kapiteltexterna.

### Provexport och granskningsomfattning

- EPUB och PDF byggdes separat med **tillfällig** författarmetadata i en isolerad provkopia; projektets author är fortsatt tomt och ordinarie export stoppas därför korrekt.
- Testad generering: Pandoc och XeLaTeX; EPUB har `nav.xhtml` med navigerbar kapitelstruktur, giltigt ZIP-arkiv och 30 nav-länkar.
- PDF-provexport före layoutjustering: 90 sidor. Visuell kontroll av innehållsförteckningens sida 3 visade att detaljrubriker överlastade TOC och gav besvärliga avstavningar.
- PDF-exporten är därför anpassad till TOC-djup 1 med huvudkapitel och bilagor. Detta påverkar inte manusets underrubriker.
- Stickprov av layout och EPUB:s struktur är inte samma sak som sid-för-sid-kontroll på läsplattor. Slutlig release kräver en full visuell läsgranskning samt kontroll av externa länkar och källor.

### Öppna publiceringsfrågor

1. Ange en verklig författare i `book.yaml` och fastställ omslag/identifierare vid behov.
2. Bekräfta att PDF:ens förenklade innehållsförteckning passar läsupplevelsen; kontrollera tabeller och långa länkar i alla kapitel.
3. EPUB bör öppnas och kontrolleras i minst en fysisk eller programbaserad EPUB-läsare.
4. Versionsbundna tekniska påståenden och källreferenser måste slutkontrolleras inför release.

## Provpublicering 0.1.16 (2026-10-14)
Omslagsbilden infogas av exportskriptet som första sida i PDF och som EPUB-cover. Reproducerbart bygge kräver PyMuPDF, och CI:s preview-/releasejobb installerar beroendet. EPUB/PDF har genererats lokalt. Kontrollera utskrivna sidbrytningar och EPUB-läsare före slutlig release; en byggframgång innebär inte automatiskt en godkänd publikationsleverans.

PDF-export använder en explicit LaTeX-mall för att bryta sidan efter innehållsförteckningen före inledningen.
