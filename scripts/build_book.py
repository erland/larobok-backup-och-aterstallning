#!/usr/bin/env python3
"""Validate and build EPUB/PDF with release-tag metadata and checksums."""
import subprocess,sys,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[1]; out=r/'exports'
out.mkdir(exist_ok=True)
for old in [*out.glob('*.epub'),*out.glob('*.pdf'),out/'SHA256SUMS.txt']:
    if old.exists(): old.unlink()
subprocess.run([sys.executable,str(r/'scripts/validate_project.py')],cwd=r,check=True)
subprocess.run([sys.executable,str(r/'scripts/project_integrity.py'),'verify'],cwd=r,check=True)
for fmt in ('epub','pdf'): subprocess.run([sys.executable,str(r/'scripts/export-book.py'),'--format',fmt],cwd=r,check=True)
files=sorted([*out.glob('*.epub'),*out.glob('*.pdf')]);assert len(files)==2,files
subprocess.run([sys.executable,str(r/'scripts/validate_exports.py'),*[str(p) for p in sorted(files,key=lambda p:0 if p.suffix=='.epub' else 1)]],cwd=r,check=True)
(out/'SHA256SUMS.txt').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in files),encoding='utf-8')
print('Built:',*[p.name for p in files])
