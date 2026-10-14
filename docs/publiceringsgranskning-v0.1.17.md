# Publiceringsgranskning – v0.1.17

Datum: 2026-10-14. Källa: bokprojekt v0.1.16. Revisionskedja: revision 18 efter revision 17.

## Genomförda förändringar

- GitHub Actions Validate, Build Preview och Release granskas mot Lärobokskaparens kontrakt. Preview/Release installerar låst Pandoc **3.1.11.1**, XeLaTeX och nödvändiga Pythonberoenden. Preview ger ett artifact med EPUB, PDF och SHA256SUMS.txt. Release på `vX.Y.Z` använder taggen i exporterade filnamn och versionsmetadata utan att ändra `book.yaml`, och publicerar de tre artefakterna som release-assets.
- `scripts/build_book.py` rensar gamla previewartefakter före nytt bygge, validerar projektintegritet och exporter, samt skriver SHA-256-fil.
- EPUB får CSS för läsbara stycken/tabeller och efterbearbetas så `nav.xhtml` bevaras, men får `linear=no` i OPF-spine för att undvika en oavsiktlig synlig innehållsförteckning. Ett EPUB-test granskar manifest, navigationsdokument, omslag och interna länkmål.
- PDF sätts i 170 × 240 mm med marginaler 20/18/20/22 mm, och har omslag, separat titelsida och innehållsförteckning före inledningen. PDF-metadata omfattar titel, författare och version som nyckelord. Manus och kapitelordning är oförändrade.

## Faktiskt verifierat i lokal exekveringsmiljö

- `scripts/project_integrity.py verify` och `scripts/validate_project.py` passerade.
- Både previewbygge 0.1.17 och testbygge med releasetagg v1.0.0 gick igenom med Pandoc 3.1.11.1 och XeLaTeX. `book.yaml` ändrades inte av taggbygget.
- Slutlig preview-PDF: **81 sidor**, 170 × 240 mm, 27 PDF-bokmärken och 27 PDF-länkobjekt enligt PyMuPDF. PDF-text kunde extraheras och PDF-metadata hade rätt titel, författare och version.
- EPUB: ZIP-CRC kontrollerad, omslag finns, `nav.xhtml` är navigerbart och markerat `linear=no`; 79 interna länkförekomster verifierades mot befintliga mål. Samtliga exporterade EPUB-interna XHTML-dokument kontrollerades som XML.
- Sidrenderingar granskade i en kontaktkarta från 15 sidor: omslag, titelsida, innehållsförteckning, kapitelstarter, text, kod, tabeller och bilagor. Inga uppenbara avklippningar i urvalet.

## Kvarstående begränsningar

- GitHub Actions har granskats mot pluginmallen och motsvarande byggsteg har körts lokalt, men **inte körts på GitHub Actions servrar**; denna kontroll kräver att projektet publiceras i ett GitHub-repo och workflow_dispatch/PR körs där.
- Visuell läsning av **varje enskild PDF-sida** och fysisk eller programbaserad genomläsning i Apple Böcker har inte genomförts. Kontaktkartan är ett urval, inte ett fullständigt sidvis intyg.
- Externa URL:ers aktuella svar och all versionkänslig teknisk information behöver slutkontrolleras separat inför offentlig publicering. Förhandsutgåvan är inte en faktisk GitHub Release.
- Ett ISBN/identifierare och utgivare är valfria metadatafält som inte är ifyllda. Användaren behöver besluta om detta före distribution där det är relevant.

## Slutsats

Bygg- och strukturkontrollerna är godkända. Rekommendationen är ett GitHub-previewbygge följt av kort faktisk läsarkontroll i Apple Böcker innan första publika release. Inga kapitel eller bilagor har ändrats.
