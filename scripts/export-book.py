#!/usr/bin/env python3
import argparse,subprocess,shutil,sys,os
from pathlib import Path
import yaml
p=argparse.ArgumentParser();p.add_argument('--format',choices=['epub','pdf'],required=True);a=p.parse_args()
r=Path(__file__).resolve().parent.parent;b=yaml.safe_load((r/'book.yaml').read_text(encoding='utf-8'))
if not b.get('author'):sys.exit('Set book.yaml author before export')
if not shutil.which('pandoc'):sys.exit('Pandoc is not installed')
if a.format=='pdf' and not shutil.which('xelatex'):sys.exit('XeLaTeX is not installed')
out=r/'exports';out.mkdir(exist_ok=True)
version=os.getenv('BOOK_RELEASE_TAG', '').removeprefix('v') or b['version'];output=out/f"{b['project_slug']}-{version}.{a.format}"
cmd=['pandoc',*list(map(str,[r/x for x in b['chapters']])), '--standalone','--metadata',f"title={b['title']}",'--metadata',f"subtitle={b['subtitle']}",'--metadata',f"author={b['author']}",'--metadata',f"lang={b['language']}",'--metadata',f"version={version}",'--metadata',f"keywords=Version {version}",'--lua-filter',str(r/'publishing/chapter-layout.lua'),'-o',str(output)]
if a.format=='epub':
 cover=r/b.get('cover_image','') if b.get('cover_image') else None
 if cover and cover.is_file():cmd.extend(['--epub-cover-image',str(cover)])
 cmd.extend(['--toc','--toc-depth=1','--css',str(r/'publishing/epub.css')])
else:cmd.extend(['--toc','--toc-depth=1','--pdf-engine=xelatex','--template',str(r/'publishing/pdf-pandoc-template.tex'),'--variable','geometry:paperwidth=170mm','--variable','geometry:paperheight=240mm','--variable','geometry:inner=20mm','--variable','geometry:outer=18mm','--variable','geometry:top=20mm','--variable','geometry:bottom=22mm'])
subprocess.run(cmd,check=True)
if a.format=='epub': subprocess.run([sys.executable,str(r/'publishing/fix-epub-after-pandoc.py'),str(output)],check=True)
if a.format=='pdf' and b.get('cover_image'):
 cover=r/b['cover_image']
 if not cover.is_file():sys.exit(f'Cover image missing: {cover}')
 try:import fitz
 except ImportError:sys.exit('PyMuPDF required to embed PDF cover; install pymupdf')
 doc=fitz.open(str(output));front=doc.new_page(pno=0,width=doc[0].rect.width,height=doc[0].rect.height)
 front.insert_image(front.rect,filename=str(cover),keep_proportion=True)
 temp=out/(output.stem+'-with-cover.pdf');doc.save(str(temp),garbage=4,deflate=True);doc.close();temp.replace(output)
print(output)
