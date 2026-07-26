# -*- coding: utf-8 -*-
"""Write AI-PROMPT.md: the whole project packed into one message for a chatbot.

Run it with EXPORT-FOR-AI.bat. Nothing here changes the website.
"""
import os, sys, io, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(ROOT, 'html_files')
OUT = os.path.join(ROOT, 'AI-PROMPT.md')

TEXT_EXT = ('.html', '.css', '.js')
IMG_EXT = ('.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp')

try:
    from PIL import Image
except ImportError:
    Image = None


def rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, '/')


def collect_text():
    out = []
    for pat in ('*.html', 'css/*.css', 'js/*.js'):
        for p in sorted(glob.glob(os.path.join(PAGES, pat))):
            out.append(p)
    return out


def collect_assets():
    out = []
    for root, dirs, files in os.walk(os.path.join(PAGES, 'images')):
        for f in sorted(files):
            if f.lower().endswith(IMG_EXT):
                out.append(os.path.join(root, f))
    return sorted(out)


FORMAT_SPEC = """\
## HOW YOU MUST REPLY

Reply with plain text using the markers below. **Do not wrap them in markdown code
fences.** Anything outside the markers is ignored, so explain yourself freely.

To create or overwrite a file — always give the **entire** file, never a fragment:

    <<<FILE html_files/contact.html>>>
    ...the complete new contents of the file...
    <<<END>>>

To delete a file:

    <<<DELETE html_files/old-page.html>>>

To add a picture from the user's own computer (it will be copied in, resized,
white borders trimmed, and a thumbnail generated automatically):

    <<<ASSET C:\\Users\\Otaku\\Pictures\\new-lathe.jpg -> html_files/images/equipment/41-cnc-lathe.jpg>>>

### Rules that matter

1. **Never abbreviate a file.** Writing `/* ...unchanged... */`, `<!-- rest of file -->`
   or similar will be rejected by the importer and nothing will be applied. If a file
   is long, write it out in full anyway.
2. **Only include files you actually changed.** Unchanged files must not appear.
3. **Bilingual text comes in threes.** Every visible string carries `data-en`,
   `data-ar` and the visible text between the tags:
   `<h3 data-en="Cranes" data-ar="رافعات">Cranes</h3>`
   If you change wording you must change all three, or the site will show one thing
   and then flip to another when the visitor switches language.
4. **The header, navigation and footer are duplicated in all six pages.** If you change
   any of them, output all six pages, not one.
5. **All paths start from the site root** — `/css/site.css`, `/images/equipment/x.jpg`.
   Never use relative paths like `../images/`.
6. **Every photo has a matching `thumbs/` copy.** Grids and galleries load
   `/images/<section>/thumbs/<name>.jpg`; the lightbox loads the full-size
   `/images/<section>/<name>.jpg` via `data-full`.
7. Keep the existing look: the design tokens at the top of `site.css` (colours,
   spacing, radius) drive everything. Prefer changing a token over hard-coding a value.
8. Both a **dark and a light** theme exist, and the page flips to **right-to-left**
   in Arabic. Any new styling has to survive all of that.
"""


def main():
    parts = []
    A = parts.append

    A('# MEA website — full project context\n')
    A('This message contains the complete source of a small static website: every page, '
      'the shared stylesheet, the shared script, and a list of every image. '
      'The request from the site owner follows at the very end of this message.\n')
    A('**Read "HOW YOU MUST REPLY" at the bottom before answering.** Your reply is fed '
      'straight into a script that writes files to disk, so the format is not optional.\n')

    A('\n---\n\n## What this site is\n')
    A("""\
MEA — Mughrabi Engineering Agencies. A six-page brochure site for an industrial
engineering business run by Eng. M. Said Mughrabi, based in Germany: machinery design,
manufacture, supply and consultancy.

- Plain HTML, CSS and JavaScript. No framework, no build step, no dependencies.
- Published to GitHub Pages by double-clicking `PUBLISH.bat`.
- A script copies `html_files/` to `_site/` and gives each page a clean address, so
  `html_files/about.html` is served at both `/about.html` and `/about/`.
- Fully bilingual English / Arabic from one set of files, switched by a button.
- Dark and light themes, switched by a button, defaulting to the visitor's system setting.
""")

    A('\n### Page map\n')
    A('| File | Live address | Purpose |')
    A('|---|---|---|')
    A('| `html_files/index.html` | `/` | Home |')
    A('| `html_files/about.html` | `/about` | Company, mission, capabilities |')
    A('| `html_files/services.html` | `/services` | The five service lines |')
    A('| `html_files/equipment.html` | `/equipment` | Filterable machine catalogue |')
    A('| `html_files/projects.html` | `/projects` | Photo gallery |')
    A('| `html_files/contact.html` | `/contact` | Contact card |')

    A('\n### Shared behaviour in `js/site.js`\n')
    A("""\
1. Theme (dark / light), remembered in localStorage
2. Language (English / Arabic) with right-to-left switching
3. Mobile navigation menu
4. Current year written into the footer automatically
5. Scroll reveal, sticky-header shadow, back-to-top button
6. Equipment filtering (also reads `/equipment#food` style links)
7. Photo lightbox with keyboard arrows
""")

    # ---------------- file tree ----------------
    A('\n---\n\n## File tree\n')
    A('```')
    A('website-kit/')
    A('├── html_files/            <- the website itself; everything here is published')
    text_files = collect_text()
    for p in text_files:
        A('│   ' + rel(p).replace('html_files/', ''))
    A('│   images/                <- see the asset list below')
    A('├── scripts/build_index.py <- builds the site (do not edit)')
    A('├── PUBLISH.bat            <- publishes to GitHub')
    A('├── EXPORT-FOR-AI.bat      <- produced this message')
    A('└── IMPORT-FROM-AI.bat     <- applies your reply')
    A('```')

    # ---------------- assets ----------------
    assets = collect_assets()
    full = [a for a in assets if 'thumbs' not in rel(a)]
    thumbs = [a for a in assets if 'thumbs' in rel(a)]
    A('\n---\n\n## Images (%d full-size, each with a matching thumbnail)\n' % len(full))
    A('Reference the thumbnail in grids and the full-size one in `data-full`. '
      'Thumbnails are not listed individually — every full-size file below has one at '
      'the same name inside its folder\'s `thumbs/`.\n')

    by_dir = {}
    for a in full:
        by_dir.setdefault(os.path.dirname(rel(a)), []).append(a)
    for d in sorted(by_dir):
        A('\n**/%s/**\n' % d.replace('html_files/', ''))
        for a in by_dir[d]:
            dims = ''
            if Image:
                try:
                    with Image.open(a) as im:
                        dims = ' — %d×%d' % im.size
                except Exception:
                    pass
            kb = os.path.getsize(a) / 1024.0
            A('- `/%s` (%.0f KB%s)' % (rel(a).replace('html_files/', ''), kb, dims))
    A('\n_%d thumbnails also exist and are managed automatically._' % len(thumbs))

    # ---------------- source ----------------
    A('\n---\n\n## Source files\n')
    A('Each file is shown between markers identical to the ones you must use in your reply.\n')
    for p in text_files:
        body = io.open(p, encoding='utf-8').read()
        A('\n<<<FILE %s>>>' % rel(p))
        A(body.rstrip('\n'))
        A('<<<END>>>')

    A('\n---\n\n' + FORMAT_SPEC)
    A('\n---\n\n## The request\n')
    A('Everything above is context. What the site owner wants is written below.\n')

    text = '\n'.join(parts) + '\n'
    io.open(OUT, 'w', encoding='utf-8', newline='\n').write(text)

    chars = len(text)
    print('  Wrote AI-PROMPT.md')
    print('  %d source files, %d images described' % (len(text_files), len(full)))
    print('  %.0f KB  (roughly %s tokens)' % (chars / 1024.0, format(int(chars / 3.7), ',d')))
    return 0


if __name__ == '__main__':
    sys.exit(main())
