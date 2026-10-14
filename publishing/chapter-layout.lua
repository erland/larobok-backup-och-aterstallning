-- PDF needs explicit starts; EPUB already splits at h1, so do not add page breaks.
local function latex_escape(s)
  return s:gsub('\\','\\textbackslash{}'):gsub('([%%$#&_{}])','\\%1')
end
function Header(h)
  if h.level ~= 1 then return nil end
  local full=pandoc.utils.stringify(h.content)
  local number,title=full:match('^(%d+)%.%s+(.+)$')
  if not number then number,title=full:match('^(Bilaga%s+%S+)[%s%.:%-]+(.+)$') end
  if FORMAT:match('latex') then
    local heading
    if number then
      heading='\\phantomsection\\addcontentsline{toc}{section}{'..latex_escape(full)..'}\n'..
        '\\begin{center}\\large '..latex_escape(number)..'\\par\\vspace{0.7em}'..
        '{\\Large\\bfseries '..latex_escape(title)..'\\par}\\end{center}\\vspace{1.0em}'
    else
      heading='\\phantomsection\\addcontentsline{toc}{section}{'..latex_escape(full)..'}\n'..
        '\\begin{center}{\\Large\\bfseries '..latex_escape(full)..'\\par}\\end{center}\\vspace{1.0em}'
    end
    return {pandoc.RawBlock('latex','\\clearpage'), pandoc.RawBlock('latex',heading)}
  end
  if (FORMAT:match('epub') or FORMAT:match('html')) and number then
    h.content={pandoc.Span({pandoc.Str(number)},pandoc.Attr('',{'chapter-number'})),pandoc.Space(),pandoc.Span({pandoc.Str(title)},pandoc.Attr('',{'chapter-title'}))}
  end
  return h
end
