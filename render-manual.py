#!/usr/bin/env python3
"""Render manual.md to manual.html (no dependencies).

Usage:  python3 render-manual.py [manual.md] [manual.html]

Supports the Markdown subset the manual uses: headings, paragraphs, bullet
and numbered lists (nested by 4 spaces), fenced code blocks, tables,
blockquotes, **bold**, *italic*, `code` and [links](url).
"""
import html
import re
import sys

SRC = sys.argv[1] if len(sys.argv) > 1 else 'manual.md'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'manual.html'


def slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def inline(text):
    """Escape, then apply inline markup. Code spans are protected first."""
    codes = []

    def keep(m):
        codes.append('<code>' + html.escape(m.group(1)) + '</code>')
        return f'\x00{len(codes) - 1}\x00'

    text = re.sub(r'`([^`]+)`', keep, text)
    text = html.escape(text, quote=False)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?!\w)', r'<em>\1</em>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', r'<a href="\2">\1</a>', text)
    return re.sub(r'\x00(\d+)\x00', lambda m: codes[int(m.group(1))], text)


LIST_RE = re.compile(r'^( *)([-*]|\d+\.) +(.*)$')


def render_list(lines, i, indent):
    """Render a (possibly nested) list starting at lines[i]; return (html, next i)."""
    ordered = LIST_RE.match(lines[i]).group(2)[0].isdigit()
    out = ['<ol>' if ordered else '<ul>']
    while i < len(lines):
        m = LIST_RE.match(lines[i])
        if not m or len(m.group(1)) < indent:
            break
        if len(m.group(1)) > indent:                     # nested list inside the previous item
            sub, i = render_list(lines, i, len(m.group(1)))
            out[-1] = out[-1].removesuffix('</li>') + sub + '</li>'
            continue
        out.append('<li>' + inline(m.group(3)) + '</li>')
        i += 1
    out.append('</ol>' if ordered else '</ul>')
    return ''.join(out), i


def render(md):
    lines = md.split('\n')
    body, toc, title = [], [], ''
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
        elif line.startswith('```'):
            lang = line[3:].strip()
            j = i + 1
            while j < len(lines) and not lines[j].startswith('```'):
                j += 1
            code = html.escape('\n'.join(lines[i + 1:j]))
            label = f'<span class="lang">{html.escape(lang)}</span>' if lang and lang != 'text' else ''
            body.append(f'<div class="code">{label}<pre><code>{code}</code></pre></div>')
            i = j + 1
        elif m := re.match(r'^(#{1,3}) +(.*)$', line):
            level, text = len(m.group(1)), m.group(2).strip()
            if level == 1:
                title = text
                body.append(f'<h1>{inline(text)}</h1>')
            else:
                anchor = slug(text)
                toc.append((level, anchor, text))
                body.append(f'<h{level} id="{anchor}"><a class="anchor" href="#{anchor}">#</a>{inline(text)}</h{level}>')
            i += 1
        elif line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            head, rest = rows[0], [r for r in rows[1:] if not all(re.fullmatch(r':?-+:?', c) for c in r)]
            body.append('<div class="table"><table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in head)
                        + '</tr></thead><tbody>'
                        + ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>' for r in rest)
                        + '</tbody></table></div>')
        elif line.startswith('>'):
            quote = []
            while i < len(lines) and lines[i].startswith('>'):
                quote.append(lines[i][1:].strip())
                i += 1
            body.append('<blockquote><p>' + inline(' '.join(quote)) + '</p></blockquote>')
        elif LIST_RE.match(line):
            out, i = render_list(lines, i, len(LIST_RE.match(line).group(1)))
            body.append(out)
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not re.match(r'^(#|```|\||>)', lines[i]) and not LIST_RE.match(lines[i]):
                para.append(lines[i].strip())
                i += 1
            text = ' '.join(para)
            body.append(f'<p class="lead">{inline(text)}</p>' if len(body) == 1 and title else f'<p>{inline(text)}</p>')
    return title, toc, '\n'.join(body)


def nav(toc):
    items = []
    for level, anchor, text in toc:
        cls = 'sub' if level == 3 else ''
        items.append(f'<li class="{cls}"><a href="#{anchor}">{inline(text)}</a></li>')
    return '<ul>' + ''.join(items) + '</ul>'


CSS = '''
:root { --pink:#F6E2E9; --cream:#FEFAF3; --sagel:#B8CFB3; --sage:#84A282; --ink:#2B3A2A; --soft:#5B6F59;
        --card:rgba(254,250,243,.92); --code:#F3EFE6; --line:#DCE6D8; }
* { box-sizing: border-box; }
html { scroll-behavior: smooth; scroll-padding-top: 16px; }
body { margin: 0; background: var(--cream); color: var(--ink); font: 16px/1.6 "Avenir Next","Segoe UI",system-ui,sans-serif; overflow-x: hidden; }
.blob { position: fixed; border-radius: 50%; pointer-events: none; z-index: 0; }
.a { width: 46vmax; height: 46vmax; background: var(--pink); top: -18vmax; right: -14vmax; opacity: .7; }
.b { width: 38vmax; height: 38vmax; background: var(--sagel); bottom: -20vmax; left: -12vmax; opacity: .45; }
.layout { position: relative; z-index: 1; display: grid; grid-template-columns: 250px minmax(0, 1fr); gap: 32px;
          max-width: 1180px; margin: 0 auto; padding: 32px 24px 64px; }
nav { position: sticky; top: 24px; align-self: start; max-height: calc(100vh - 48px); overflow-y: auto;
      background: var(--card); border: 2px solid var(--sagel); border-radius: 20px; padding: 18px 14px; font-size: .88rem; }
nav .home { display: inline-block; margin: 0 6px 10px; color: var(--sage); font-weight: 700; text-decoration: none; }
nav .home:hover { color: var(--ink); }
nav ul { list-style: none; margin: 0; padding: 0; }
nav summary { display: none; }
td code { white-space: nowrap; }
nav li a { display: block; padding: 4px 8px; border-radius: 10px; color: var(--ink); text-decoration: none; }
nav li.sub a { padding-left: 22px; color: var(--soft); font-size: .84rem; }
nav li a:hover, nav li a.on { background: var(--pink); color: var(--ink); }
main { background: var(--card); border: 2px solid var(--sagel); border-radius: 28px; padding: 40px 48px;
       box-shadow: 0 8px 24px rgba(70,95,68,.1); min-width: 0; }
h1 { font-size: clamp(2rem, 5vw, 2.8rem); letter-spacing: -.03em; line-height: 1.1; margin: 0 0 10px;
     display: flex; align-items: center; gap: 12px; }
h1::before { content: ""; flex: none; width: 16px; height: 16px; border-radius: 50%; background: var(--sage); }
.lead { color: var(--soft); font-size: 1.12rem; margin: 0 0 8px; }
h2 { font-size: 1.55rem; letter-spacing: -.02em; margin: 48px 0 12px; padding-top: 20px; border-top: 2px dashed var(--line); }
h3 { font-size: 1.15rem; margin: 30px 0 8px; }
h2, h3 { position: relative; }
.anchor { position: absolute; left: -22px; color: var(--sagel); text-decoration: none; opacity: 0; transition: opacity .15s; }
h2:hover .anchor, h3:hover .anchor { opacity: 1; }
p, li { color: #34452F; }
ul, ol { padding-left: 1.4em; }
li { margin: 4px 0; }
li > ul, li > ol { margin: 4px 0; }
strong { color: var(--ink); }
a { color: #5E7F5C; }
code { font: .86em/1.4 "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace; background: var(--code);
       border: 1px solid var(--line); border-radius: 6px; padding: 1px 5px; }
.code { position: relative; margin: 14px 0; }
.code .lang { position: absolute; top: 8px; right: 12px; font: 700 .68rem/1 system-ui, sans-serif;
              letter-spacing: .08em; text-transform: uppercase; color: var(--sage); }
pre { margin: 0; background: #2B3A2A; color: #EAF1E6; border-radius: 16px; padding: 18px 20px; overflow-x: auto; }
pre code { background: none; border: 0; padding: 0; color: inherit; font-size: .84rem; line-height: 1.55; }
.table { overflow-x: auto; margin: 14px 0; border: 2px solid var(--line); border-radius: 16px; }
table { border-collapse: collapse; width: 100%; font-size: .93rem; }
th { background: var(--sagel); text-align: left; font-weight: 700; }
th, td { padding: 9px 14px; vertical-align: top; }
tbody tr:nth-child(even) { background: rgba(184,207,179,.16); }
tbody tr + tr td { border-top: 1px solid var(--line); }
blockquote { margin: 18px 0; padding: 14px 18px; background: var(--pink); border-radius: 16px; border-left: 6px solid #D9A9BA; }
blockquote p { margin: 0; }
footer { margin-top: 48px; padding-top: 16px; border-top: 2px dashed var(--line); font-size: .85rem; color: var(--soft); }
footer a { color: var(--soft); }
@media (max-width: 860px) {
  .layout { grid-template-columns: 1fr; padding: 16px; gap: 16px; }
  nav { position: static; max-height: none; display: flex; flex-direction: column; }
  nav summary { display: block; cursor: pointer; font-weight: 700; padding: 4px 8px; margin-bottom: 4px; }
  nav .home { margin-bottom: 4px; }
  main { padding: 26px 18px; border-radius: 22px; }
  .anchor { display: none; }
  th, td { min-width: 9.5rem; padding: 8px 10px; }
}
@media print {
  .blob, nav { display: none; }
  .layout { display: block; padding: 0; }
  main { border: 0; box-shadow: none; padding: 0; }
  pre { white-space: pre-wrap; }
}
'''

JS = '''
const links = [...document.querySelectorAll('nav a[href^="#"]')];
const heads = links.map(a => document.getElementById(a.getAttribute('href').slice(1)));
const mark = () => {
  let cur = 0;
  heads.forEach((h, i) => { if (h.getBoundingClientRect().top < 120) cur = i; });
  links.forEach((a, i) => a.classList.toggle('on', i === cur));
};
addEventListener('scroll', mark, { passive: true }); mark();
// phones: the contents list starts collapsed so the manual is visible first
if (matchMedia('(max-width: 860px)').matches) document.querySelector('details.toc').removeAttribute('open');
'''


def page(title, toc, body):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<!-- Generated from manual.md by render-manual.py — edit the Markdown, then re-run the script. -->
<style>{CSS}</style>
</head>
<body>
<div class="blob a"></div><div class="blob b"></div>
<div class="layout">
<nav><a class="home" href="index.html">← ExamTools</a><details class="toc" open><summary>Contents</summary>{nav(toc)}</details></nav>
<main>
{body}
<footer>Generated from <a href="manual.md">manual.md</a> · <a href="index.html">ExamTools</a> · <a href="https://github.com/diogo-aos/examtools">Source on GitHub</a></footer>
</main>
</div>
<script>{JS}</script>
</body>
</html>
'''


if __name__ == '__main__':
    with open(SRC, encoding='utf-8') as f:
        title, toc, body = render(f.read())
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(page(title or 'Manual', toc, body))
    print(f'{SRC} → {OUT} ({len(toc)} sections)')
