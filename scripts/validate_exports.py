#!/usr/bin/env python3
"""Structural checks on final exported artifacts."""
import zipfile,sys,subprocess,os,posixpath
from pathlib import Path
from urllib.parse import unquote,urlsplit
from xml.etree import ElementTree as E
P='{http://www.idpf.org/2007/opf}';C='{urn:oasis:names:tc:opendocument:xmlns:container}'
epub,pdf=map(Path,sys.argv[1:]);
with zipfile.ZipFile(epub) as z:
  assert z.testzip() is None
  names=set(z.namelist());assert z.namelist()[0]=='mimetype' and z.getinfo('mimetype').compress_type==0
  rf=E.fromstring(z.read('META-INF/container.xml')).find('.//'+C+'rootfile'); assert rf is not None
  pkg=E.fromstring(z.read(rf.attrib['full-path'])); man=pkg.find(P+'manifest');spine=pkg.find(P+'spine')
  items={n.attrib['id']:n for n in man.findall(P+'item')};nav=[k for k,v in items.items() if 'nav' in v.attrib.get('properties','').split()]
  assert len(nav)==1,'Expected one nav.xhtml'
  assert all(n.attrib.get('linear')=='no' for n in spine.findall(P+'itemref') if n.attrib.get('idref') in nav),'Nav must be non-linear'
  assert any('cover' in k.lower() for k in names),'Cover missing'
  count=0
  for name in sorted(n for n in names if n.endswith('.xhtml')):
    root=E.fromstring(z.read(name))
    anchors={n.attrib['id'] for n in root.iter() if 'id' in n.attrib}
    for el in root.iter():
      href=el.attrib.get('href','')
      if not href or href.startswith(('http:','https:','mailto:')):continue
      url=urlsplit(href); target=posixpath.normpath(posixpath.join(posixpath.dirname(name),unquote(url.path))) if url.path else name
      assert target in names,(name,href)
      if url.fragment and target==name: assert unquote(url.fragment) in anchors,(name,href)
      count+=1
p=subprocess.run(['pdfinfo',str(pdf)],capture_output=True,text=True,check=True);assert 'Pages:' in p.stdout
p=subprocess.run(['pdftotext',str(pdf),'-'],capture_output=True,text=True,check=True);assert len(p.stdout)>2000
print('EXPORT VALIDATION PASS; EPUB internal links:',count)
