# Backup och återställning i moderna IT-system

Kanoniskt Markdown-bokprojekt för en svensk teknisk faktabok. Projektet innehåller godkänd struktur, detaljerad kapitelplan och inledning. Övriga kapitel och bilagor är ännu inte skrivna; **byggda EPUB/PDF får därför inte betraktas som färdig bok**.

## Struktur

- `book.yaml`: bokmetadata och bindande ordning för läsmaterial.
- `chapters/`: inledning, planerade kapitel och bilagor.
- `docs/`: kapitelplan, källpolicy, terminologi, faktakontroll och projektstatus.
- `scripts/`: validering och export från Markdown.
- `.github/workflows/`: validering, preview och taggstyrd release.

## Arbetsflöde

1. Skriv ett kapitel i taget och följ dispositionen i `docs/kapitelplan.md`.
2. Uppdatera faktakontroll/källpolicy och verifiera dokumentationen.
3. Kör `python3 scripts/validate_project.py`.
4. Exportera via `python3 scripts/export-book.py --format epub` eller `--format pdf` när författare har angetts och beroenden finns.

Release ska ta versionsnummer från GitHub-taggen `v*` utan att ändra `book.yaml`.
