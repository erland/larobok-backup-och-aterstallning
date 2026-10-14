# Backup och återställning i moderna IT-system

**Författare:** Erland Lindmark  
**Undertitel:** Från monolitiska system till distribuerade, händelsedrivna arkitekturer  
**Bokprojekt:** v0.1.17 (förhandsutgåva)

Detta repository innehåller ett komplett källprojekt för en svensk teknisk faktabok om backup och återställning i moderna IT-stöd. Målgruppen är arkitekter och driftansvariga med erfarenhet av traditionella system som vill förstå vad som förändras med mikroservicetjänster, asynkrona integrationsflöden och externa beroenden.

Manuset innehåller **inledning, 20 huvudkapitel och sex bilagor**, samt ett godkänt omslag. Både EPUB och PDF har provbyggts och genomgått teknisk och redaktionell granskning. Projektet är ännu inte publicerat som en officiell GitHub-release.

## Projektstruktur

- `book.yaml` – kanonisk metadata, författare, omslag och bindande kapitelordning.
- `chapters/` – läsarfärdig inledning, 20 huvudkapitel och bilaga A–F.
- `assets/cover/omslag.png` – godkänt bokomslag.
- `docs/` – kapitelplan, källpolicy, faktakontroll, terminologi, redaktionell granskning och publiceringskontroller.
- `scripts/` – validering, revisionsintegritet samt reproducerbar EPUB/PDF-export.
- `publishing/` – inställningar för EPUB- och PDF-formatering.
- `.github/workflows/` – validering, manuell förhandsbyggnad och taggstyrd release.

## Validering och export

Projektet kräver Python 3 och de beroenden som framgår av GitHub Actions. För export används **Pandoc 3.1.11.1**; PDF genereras med **XeLaTeX**.

```bash
python3 scripts/validate_project.py
python3 scripts/project_integrity.py verify
python3 scripts/build_book.py
```

Byggskriptet producerar EPUB, PDF och `SHA256SUMS.txt` under `exports/`. För direkt export av ett format går det även att använda `scripts/export-book.py`.

## GitHub Actions

1. **Validate** (`01-validate.yml`) kör projekt- och integritetskontroller vid pull request och push.
2. **Build Preview** (`02-build-preview.yml`) körs manuellt och publicerar EPUB, PDF och kontrollsummor som en tillfällig Actions-artifact.
3. **Release** (`03-release.yml`) körs vid taggar som `v1.0.0` och publicerar EPUB/PDF som GitHub Release-assets.

Vid release hämtas den exporterade bokens versionsnummer från **releasetaggen**, utan att `book.yaml` skrivs om. Vid förhandsbyggen används projektversionen i `book.yaml`.

## Inför första release

GitHubs Validate-workflow har passerat på projektets första pull request. Kör även **Build Preview** på `main` och granska dess PDF/EPUB innan en officiell release skapas. En kort läsarkontroll av EPUB i exempelvis Apple Böcker rekommenderas som sista steg.

Se `docs/publiceringsgranskning-v0.1.17.md` för tidigare kontrollresultat och kända begränsningar.
