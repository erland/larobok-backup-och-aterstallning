#!/usr/bin/env python3
"""Make nav.xhtml non-linear without removing the EPUB navigation document."""
import sys, zipfile, tempfile
from pathlib import Path
from xml.etree import ElementTree as ET
OPF='{http://www.idpf.org/2007/opf}'
C='{urn:oasis:names:tc:opendocument:xmlns:container}'
def fix(path):
  with tempfile.TemporaryDirectory() as d:
    root=Path(d)
    with zipfile.ZipFile(path) as z: z.extractall(root)
    c=ET.parse(root/'META-INF/container.xml').getroot(); rf=c.find('.//'+C+'rootfile')
    if rf is None: raise RuntimeError('Missing rootfile')
    opf=root/rf.attrib['full-path']; tree=ET.parse(opf); manifest=tree.getroot().find(OPF+'manifest'); spine=tree.getroot().find(OPF+'spine')
    nav={i.attrib['id'] for i in manifest.findall(OPF+'item') if 'nav' in i.attrib.get('properties','').split()}
    if len(nav)!=1: raise RuntimeError('Expected one EPUB nav document')
    for ref in spine.findall(OPF+'itemref'):
      if ref.attrib.get('idref') in nav: ref.set('linear','no')
    tree.write(opf,encoding='utf-8',xml_declaration=True)
    new=path.with_suffix('.tmp')
    with zipfile.ZipFile(new,'w') as z:
      z.write(root/'mimetype','mimetype',compress_type=zipfile.ZIP_STORED)
      for p in sorted(root.rglob('*')):
        if p.is_file() and p.name!='mimetype': z.write(p,p.relative_to(root).as_posix(),compress_type=zipfile.ZIP_DEFLATED)
    new.replace(path)
if __name__=='__main__': fix(Path(sys.argv[1]))
