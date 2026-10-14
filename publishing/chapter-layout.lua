-- Split chapter number and title while preserving semantic headings, TOC and anchors.
function Header(el)
  if el.level ~= 1 then return nil end
  local original=pandoc.utils.stringify(el.content)
  local number,title=original:match('^(%d+)%.%s+(.+)$')
  if not number then number,title=original:match('^(Bilaga%s+[%aÅÄÖåäö]+)%.%s+(.+)$') end
  if not number then number,title=original:match('^(Bilaga%s+[%aÅÄÖåäö]+)%s*[:%-]%s*(.+)$') end
  if number then
    if FORMAT:match('latex') then
      el.content={pandoc.Str(number),pandoc.RawInline('latex','\\texorpdfstring{\\\\}{: }'),pandoc.Str(title)}
    elseif FORMAT:match('epub') or FORMAT:match('html') then
      el.content={pandoc.Span({pandoc.Str(number)},pandoc.Attr('',{'chapter-number'})),pandoc.Space(),pandoc.Span({pandoc.Str(title)},pandoc.Attr('',{'chapter-title'}))}
    end
  end
  if FORMAT:match('latex') then return {pandoc.RawBlock('latex','\\clearpage'),el} end
  return el
end
