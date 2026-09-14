# -*- coding: utf-8 -*-
"""Apply an AI reply pasted into AI-RESPONSE.md.

Everything it touches is backed up first, and it refuses anything that looks
truncated. Run it with IMPORT-FROM-AI.bat.
"""
import os, sys, io, re, shutil, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(ROOT, 'html_files')
RESPONSE = os.path.join(ROOT, 'AI-RESPONSE.md')
BACKUPS = os.path.join(ROOT, '_ai-backups')

MAX_IMG = 1600
MAX_THUMB = 700

FILE_RE = re.compile(r'<<<FILE\s+(?P<path>[^>]+?)>>>\r?\n(?P<body>.*?)\r?\n?<<<END>>>', re.S)
DEL_RE = re.compile(r'<<<DELETE\s+([^>]+?)>>>')
ASSET_RE = re.compile(r'<<<ASSET\s+(?P<src>.+?)\s*->\s*(?P<dst>[^>]+?)>>>')

# Phrases that mean the model abbreviated instead of writing the file out.
TRUNCATION = [
    r'\.\.\.\s*(rest|remainder|unchanged|snip|etc)',
    r'(rest|remainder)\s+of\s+(the\s+)?(file|code|content)',
    r'unchanged\s*\.\.\.',
    r'<!--\s*\.\.\.',
    r'/\*\s*\.\.\.\s*\*/',
    r'\[\s*(unchanged|same as before|no changes)\s*\]',
    r'…\s*(rest|unchanged)',
]
TRUNC_RE = [re.compile(p, re.I) for p in TRUNCATION]

try:
    from PIL import Image, ImageOps
except ImportError:
    Image = None


def say(msg=''):
    print('  ' + msg if msg else '')


def safe_path(p):
    """Resolve a project-relative path, refusing anything outside the project."""
    p = p.strip().strip('"').replace('\\', '/').lstrip('/')
    full = os.path.normpath(os.path.join(ROOT, p))
    if not full.startswith(os.path.normpath(ROOT) + os.sep):
        return None
    return full


# ---------------------------------------------------------------- images
def process_image(src, dst):
    """Trim white borders, cap the size, save, and build the thumbnail."""
    if Image is None:
        shutil.copy(src, dst)
        return 'copied as-is (Pillow not installed, no resize or thumbnail)'

    im = Image.open(src)
    im = ImageOps.exif_transpose(im)
    ow, oh = im.size

    # crop near-white margins
    g = im.convert('RGB')
    w, h = g.size
    px = g.load()
    WHITE, FRAC = 238, .985

    def row_white(y):
        step = max(1, w // 220)
        xs = range(0, w, step)
        n = sum(1 for x in xs if min(px[x, y]) >= WHITE)
        return n / len(list(xs)) >= FRAC

    def col_white(x):
        step = max(1, h // 220)
        ys = range(0, h, step)
        n = sum(1 for y in ys if min(px[x, y]) >= WHITE)
        return n / len(list(ys)) >= FRAC

    t = 0
    while t < h - 1 and row_white(t):
        t += 1
    b = h - 1
    while b > t and row_white(b):
        b -= 1
    l = 0
    while l < w - 1 and col_white(l):
        l += 1
    r = w - 1
    while r > l and col_white(r):
        r -= 1

    note = ''
    if (r - l) >= ow * .35 and (b - t) >= oh * .35 and (l or t or r + 1 != ow or b + 1 != oh):
        im = im.crop((l, t, r + 1, b + 1))
        note = 'white border trimmed, '

    if im.mode not in ('RGB', 'L'):
        im = im.convert('RGB')

    full = im.copy()
    full.thumbnail((MAX_IMG, MAX_IMG), Image.LANCZOS)
    full.save(dst, 'JPEG', quality=84, optimize=True, progressive=True)

    tdir = os.path.join(os.path.dirname(dst), 'thumbs')
    os.makedirs(tdir, exist_ok=True)
    th = im.copy()
    th.thumbnail((MAX_THUMB, MAX_THUMB), Image.LANCZOS)
    th.save(os.path.join(tdir, os.path.basename(dst)), 'JPEG',
            quality=80, optimize=True, progressive=True)
    return '%s%d×%d, thumbnail made' % (note, full.size[0], full.size[1])


# ---------------------------------------------------------------- main
def main():
    if not os.path.isfile(RESPONSE):
        say('I cannot find AI-RESPONSE.md next to this kit.')
        say('Create it, paste the AI reply into it, save, and run this again.')
        return 1

    text = io.open(RESPONSE, encoding='utf-8', errors='replace').read()
    if not text.strip():
        say('AI-RESPONSE.md is empty. Paste the AI reply into it, save, then run this again.')
        return 1

    files = [(m.group('path'), m.group('body')) for m in FILE_RE.finditer(text)]
    deletes = [m.group(1) for m in DEL_RE.finditer(text)]
    assets = [(m.group('src'), m.group('dst')) for m in ASSET_RE.finditer(text)]

    if not (files or deletes or assets):
        say('I could not find any <<<FILE ...>>> blocks in AI-RESPONSE.md.')
        say('Check you pasted the whole reply, and that the AI used the required format.')
        return 1

    # ---------- validate before touching anything ----------
    problems = []
    for path, body in files:
        full = safe_path(path)
        if full is None:
            problems.append('path points outside the project: %s' % path)
            continue
        for rx in TRUNC_RE:
            m = rx.search(body)
            if m:
                problems.append('"%s" looks abbreviated near: %s'
                                % (path, m.group(0)[:48].strip()))
                break
        if os.path.isfile(full):
            old = len(io.open(full, encoding='utf-8', errors='replace').read())
            if old > 400 and len(body) < old * .55:
                problems.append('"%s" shrank from %d to %d characters — likely truncated'
                                % (path, old, len(body)))
    for src, dst in assets:
        if not os.path.isfile(src.strip().strip('"')):
            problems.append('picture not found on your PC: %s' % src.strip())
        if safe_path(dst) is None:
            problems.append('asset destination outside the project: %s' % dst)
    for d in deletes:
        if safe_path(d) is None:
            problems.append('delete target outside the project: %s' % d)

    if problems:
        say('NOTHING WAS CHANGED. The reply has problems:')
        say()
        for p in problems:
            say('  - ' + p)
        say()
        say('Ask the AI to send the affected file again, complete and unabbreviated.')
        return 1

    # ---------- back up ----------
    stamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup = os.path.join(BACKUPS, stamp)
    touched = [safe_path(p) for p, _ in files] + [safe_path(d) for d in deletes] \
              + [safe_path(d) for _, d in assets]
    saved = 0
    for full in touched:
        if full and os.path.isfile(full):
            dest = os.path.join(backup, os.path.relpath(full, ROOT))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(full, dest)
            saved += 1
    if saved:
        say('Backed up %d existing file(s) to  _ai-backups\\%s' % (saved, stamp))
        say()

    # ---------- apply ----------
    for path, body in files:
        full = safe_path(path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        existed = os.path.isfile(full)
        io.open(full, 'w', encoding='utf-8', newline='\n').write(body.rstrip('\n') + '\n')
        say('%s  %s' % ('updated' if existed else 'created', path))

    for d in deletes:
        full = safe_path(d)
        if os.path.isfile(full):
            os.remove(full)
            say('deleted  %s' % d)
            thumb = os.path.join(os.path.dirname(full), 'thumbs', os.path.basename(full))
            if os.path.isfile(thumb):
                os.remove(thumb)
                say('deleted  (its thumbnail too)')
        else:
            say('already gone  %s' % d)

    for src, dst in assets:
        src = src.strip().strip('"')
        full = safe_path(dst)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        try:
            note = process_image(src, full)
            say('added    %s  (%s)' % (dst, note))
        except Exception as e:
            say('FAILED   %s  (%s)' % (dst, e))

    # ---------- rebuild + sanity check ----------
    say()
    say('Rebuilding the site...')
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    os.chdir(ROOT)
    # Called directly rather than through os.system, so no command interpreter
    # ever parses the folder path (a name containing & would break it).
    import subprocess
    rc = subprocess.call([sys.executable, os.path.join(ROOT, 'scripts', 'build_index.py'),
                          'html_files', '_site', 'unlisted'], cwd=ROOT)
    if rc != 0:
        say('The build reported a problem. Your previous files are in _ai-backups.')
        return 1

    missing = check_links()
    say()
    if missing:
        say('WARNING: %d link(s) or picture(s) now point at something missing:' % len(missing))
        for m in missing[:12]:
            say('  - ' + m)
        say('Tell the AI about these, or restore from _ai-backups.')
    else:
        say('Checked every link and picture: all present.')

    say()
    say('Done. Preview it before publishing:')
    say('  python -m http.server 8765 --directory _site')
    say('Then open  http://localhost:8765')
    return 0


def check_links():
    """Every root-relative asset referenced by a page must exist on disk."""
    import glob
    attr = re.compile(r'(?:src|href|data-full)\s*=\s*"(/[^"]+)"', re.I)
    missing = []
    for page in glob.glob(os.path.join(PAGES, '*.html')):
        html = io.open(page, encoding='utf-8', errors='replace').read()
        for url in attr.findall(html):
            path = url.split('#')[0].split('?')[0]
            if not re.search(r'\.[a-z0-9]{2,5}$', path, re.I):
                continue
            if not os.path.isfile(os.path.join(PAGES, path.lstrip('/'))):
                missing.append('%s -> %s' % (os.path.basename(page), url))
    return missing


if __name__ == '__main__':
    sys.exit(main())
