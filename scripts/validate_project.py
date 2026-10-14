#!/usr/bin/env python3
from pathlib import Path
import sys,yaml
root=Path(__file__).resolve().parent.parent
b=yaml.safe_load((root/'book.yaml').read_text(encoding='utf-8'))
errors=[]
if b.get('book_kind')!='factbook': errors.append('book_kind must be factbook')
if len(b['chapters'])!=27: errors.append('Expected introduction, 20 chapters, 6 appendices')
for f in b['chapters']:
 if not (root/f).is_file():errors.append(f'Missing {f}')
if b['chapters'][0]!='chapters/00-inledning.md':errors.append('Missing opening introduction')
for f in ('docs/kapitelplan.md','docs/kallpolicy.md','docs/faktakontroll.md','project-manifest.json'):
 if not (root/f).exists():errors.append(f'Missing {f}')
print('VALIDATION:', 'PASS' if not errors else 'FAIL')
for e in errors:print('-',e)
sys.exit(bool(errors))
