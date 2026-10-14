#!/usr/bin/env python3
"""Manifestintegritet: init eller verify. Ändringar kräver nytt init och revisionslogg."""
import hashlib,json,sys,datetime
from pathlib import Path
r=Path(__file__).resolve().parent.parent;f=r/'project-manifest.json'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tracks():return {str(p.relative_to(r)):digest(p) for p in sorted(r.rglob('*')) if p.is_file() and '.git' not in p.parts and p.name!='project-manifest.json' and 'exports' not in p.parts and not p.name.endswith('.zip') and '__pycache__' not in p.parts}
mode=sys.argv[1] if len(sys.argv)>1 else 'verify'
if mode=='init':
 old=json.loads(f.read_text()) if f.exists() else {};rev=int(old.get('revision',0))+1
 obj={'schema_version':1,'project_slug':r.name,'revision':rev,'parent_revision':rev-1 if rev>1 else None,'tracked_files':tracks(),'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 f.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print('Manifest revision',rev)
elif mode=='verify':
 actual=tracks();expected=json.loads(f.read_text())['tracked_files'];changed=[k for k in sorted(set(actual)|set(expected)) if actual.get(k)!=expected.get(k)]
 if changed:print('FAIL:',changed);sys.exit(1)
 print('INTEGRITY PASS:',len(actual),'files')
else:sys.exit('Usage: project_integrity.py [init|verify]')
