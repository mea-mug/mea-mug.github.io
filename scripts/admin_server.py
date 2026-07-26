# -*- coding: utf-8 -*-
"""Local admin dashboard: export, apply, preview and publish from one page.

Runs only on this computer (127.0.0.1) and only when a valid
my-github-details.txt is present. Started by ADMIN.bat.

The GitHub token is never read into this process, never sent to the browser,
and never written to a log. Publishing is handed to PUBLISH.bat, which reads
the credentials itself, exactly as it does when you double-click it.
"""
import os, sys, io, json, re, glob, base64, shutil, secrets, socket, subprocess
import threading, unicodedata, webbrowser, datetime
from http.server import (BaseHTTPRequestHandler, ThreadingHTTPServer,
                         SimpleHTTPRequestHandler)
from functools import partial

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from ai_import import process_image   # same trim / resize / thumbnail pipeline
except Exception:
    process_image = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, 'scripts')
PAGES = os.path.join(ROOT, 'html_files')
SITE = os.path.join(ROOT, '_site')

TOKEN = secrets.token_urlsafe(24)
PREVIEW = {'port': None}

REQUIRED = ('GITHUB_USERNAME', 'GITHUB_EMAIL', 'GITHUB_REPO', 'GITHUB_TOKEN')
PLACEHOLDERS = ('PASTE_YOUR_USERNAME_HERE', 'PASTE_YOUR_GITHUB_USERNAME_HERE',
                'PASTE_YOUR_GITHUB_EMAIL_HERE', 'PASTE_YOUR_REPOSITORY_NAME_HERE',
                'PASTE_YOUR_TOKEN_HERE')


# ------------------------------------------------------------------ credentials
def credentials_file():
    for name in ('my-github-details.txt', 'my-github-details.txt.txt'):
        p = os.path.join(ROOT, name)
        if os.path.isfile(p):
            return p
    return None


def check_credentials():
    """Return (ok, message, public_info). The token value never leaves this function."""
    path = credentials_file()
    if not path:
        return False, ('I cannot find your details file.\n\n'
                       'Make a copy of my-github-details.EXAMPLE.txt, name it\n'
                       'my-github-details.txt, and fill it in. See START-HERE.md Part 6.'), {}

    vals = {}
    for raw in io.open(path, encoding='utf-8', errors='replace'):
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, _, v = line.partition('=')
        vals[k.strip().upper()] = v.strip()

    for key in REQUIRED:
        if not vals.get(key):
            return False, ('Your details file is missing %s.\n\n'
                           'Check there is no space around the "=" and that the line\n'
                           'has a value after it. See START-HERE.md Part 6.' % key), {}
        if vals[key] in PLACEHOLDERS:
            return False, ('%s still has the example text in it.\n\n'
                           'Replace it with your own value. See START-HERE.md Part 6.'
                           % key), {}

    if '/' in vals['GITHUB_REPO']:
        return False, ('GITHUB_REPO must be the repository name only, such as\n'
                       'jane.github.io — not jane/jane.github.io.'), {}

    # Only non-secret fields are ever surfaced.
    return True, 'ok', {'repo': vals['GITHUB_REPO'], 'user': vals['GITHUB_USERNAME']}


# ------------------------------------------------------------------ helpers
def decode(b):
    for enc in ('utf-8', 'cp1252', 'cp850'):
        try:
            return b.decode(enc)
        except UnicodeDecodeError:
            continue
    return b.decode('utf-8', 'replace')


def run(args, cwd=ROOT, stdin_null=True):
    """Run a command, return (returncode, combined output)."""
    p = subprocess.run(
        args, cwd=cwd,
        stdin=subprocess.DEVNULL if stdin_null else None,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        shell=isinstance(args, str))
    return p.returncode, decode(p.stdout)


def site_stats():
    pages = len(glob.glob(os.path.join(PAGES, '*.html')))
    imgs = 0
    for root, d, files in os.walk(os.path.join(PAGES, 'images')):
        if 'thumbs' in root:
            continue
        imgs += sum(1 for f in files if f.lower().endswith(
            ('.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp')))
    return {'pages': pages, 'images': imgs}


# ------------------------------------------------------------------ photos
SECTIONS = ('equipment', 'services', 'projects', 'about', 'home', 'contact', 'brand')
IMG_OK = ('.jpg', '.jpeg', '.png', '.gif', '.webp')


def slugify(s, maxlen=48):
    s = re.sub(r'\.[A-Za-z0-9]{2,5}$', '', s or '')
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\b\d{6,}\b', ' ', s)
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    parts = [p for p in s.split('-') if p and p not in ('img', 'image', 'dsc', 'photo')]
    # drop a camera counter at the front (DSC_04821 -> 04821) but keep numbers
    # that carry meaning further along, such as "fu251" or "type-3"
    while len(parts) > 1 and parts[0].isdigit():
        parts.pop(0)
    s = '-'.join(parts)[:maxlen].strip('-')
    return s or 'photo'


def next_index(folder):
    top = 0
    if os.path.isdir(folder):
        for f in os.listdir(folder):
            m = re.match(r'(\d+)-', f)
            if m:
                top = max(top, int(m.group(1)))
    return top + 1


def referenced_paths():
    """Every /images/... path mentioned anywhere in the pages."""
    used = set()
    rx = re.compile(r'(?:src|href|data-full|content)\s*=\s*"([^"]*?/images/[^"]+)"', re.I)
    for page in glob.glob(os.path.join(PAGES, '*.html')):
        html = io.open(page, encoding='utf-8', errors='replace').read()
        for u in rx.findall(html):
            used.add(u.split('#')[0].split('?')[0].lstrip('/'))
    return used


def list_images():
    used = referenced_paths()
    out = []
    base = os.path.join(PAGES, 'images')
    for section in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        d = os.path.join(base, section)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            p = os.path.join(d, f)
            if not os.path.isfile(p) or not f.lower().endswith(IMG_OK + ('.svg',)):
                continue
            web = 'images/%s/%s' % (section, f)
            thumb = 'images/%s/thumbs/%s' % (section, f)
            has_thumb = os.path.isfile(os.path.join(PAGES, thumb))
            out.append({
                'section': section,
                'name': f,
                'full': '/' + web,
                'thumb': '/' + (thumb if has_thumb else web),
                'kb': round(os.path.getsize(p) / 1024.0),
                'used': web in used,
            })
    return out


def save_upload(filename, section, data_b64):
    if section not in SECTIONS:
        raise ValueError('unknown section')
    ext = os.path.splitext(filename)[1].lower()
    if ext not in IMG_OK:
        raise ValueError('only JPG, PNG, GIF and WEBP pictures can be added')

    folder = os.path.join(PAGES, 'images', section)
    os.makedirs(folder, exist_ok=True)

    stem = slugify(filename)
    name = '%02d-%s.jpg' % (next_index(folder), stem)
    dest = os.path.join(folder, name)

    raw = base64.b64decode(data_b64.split(',')[-1])
    tmp = dest + '.upload'
    with open(tmp, 'wb') as f:
        f.write(raw)
    try:
        note = process_image(tmp, dest) if process_image else (shutil.copy(tmp, dest) or 'copied')
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

    return {
        'name': name, 'section': section, 'note': note,
        'full': '/images/%s/%s' % (section, name),
        'thumb': '/images/%s/thumbs/%s' % (section, name),
    }


def delete_image(web_path):
    rel = web_path.strip().lstrip('/')
    if not rel.startswith('images/'):
        raise ValueError('not a picture in this site')
    full = os.path.normpath(os.path.join(PAGES, rel))
    if not full.startswith(os.path.normpath(PAGES) + os.sep) or not os.path.isfile(full):
        raise ValueError('picture not found')

    stamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    bdir = os.path.join(ROOT, '_ai-backups', stamp, os.path.dirname(rel))
    os.makedirs(bdir, exist_ok=True)
    shutil.copy2(full, os.path.join(bdir, os.path.basename(full)))
    os.remove(full)

    thumb = os.path.join(os.path.dirname(full), 'thumbs', os.path.basename(full))
    if os.path.isfile(thumb):
        os.remove(thumb)
    return stamp


# ------------------------------------------------------------------ site state
def broken_links():
    """Root-relative assets a page points at that are not on disk."""
    rx = re.compile(r'(?:src|href|data-full)\s*=\s*"(/[^"]+)"', re.I)
    bad = []
    for page in glob.glob(os.path.join(PAGES, '*.html')):
        html = io.open(page, encoding='utf-8', errors='replace').read()
        for url in rx.findall(html):
            path = url.split('#')[0].split('?')[0]
            if not re.search(r'\.[a-z0-9]{2,5}$', path, re.I):
                continue
            if not os.path.isfile(os.path.join(PAGES, path.lstrip('/'))):
                bad.append('%s → %s' % (os.path.basename(page), url))
    return bad


def git(*args):
    try:
        p = subprocess.run(('git', '-C', ROOT) + args, stdin=subprocess.DEVNULL,
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        # rstrip only: porcelain output starts with a two-column status field,
        # and stripping the leading space would eat the first letter of a path.
        return p.returncode, decode(p.stdout).rstrip('\r\n')
    except Exception:
        return 1, ''


def publish_state():
    """How far the working folder has drifted from what is live."""
    if not os.path.isdir(os.path.join(ROOT, '.git')):
        return {'repo': False, 'changed': 0, 'last': None, 'everPublished': False}
    rc, out = git('status', '--porcelain')
    changed = [l for l in out.split('\n') if l.strip()] if rc == 0 else []
    rc2, last = git('log', '-1', '--format=%cI')
    return {
        'repo': True,
        'changed': len(changed),
        'files': [l[3:] for l in changed[:12]],
        'last': last if rc2 == 0 and last else None,
        'everPublished': rc2 == 0 and bool(last),
    }


def activity():
    """Edits and publishes, newest first — a plain chronological history."""
    events = []
    bdir = os.path.join(ROOT, '_ai-backups')
    if os.path.isdir(bdir):
        for name in os.listdir(bdir):
            m = re.match(r'(\d{4}-\d{2}-\d{2})_(\d{2})-(\d{2})-(\d{2})$', name)
            if m:
                n = sum(len(f) for _, _, f in os.walk(os.path.join(bdir, name)))
                events.append({
                    'when': '%sT%s:%s:%s' % (m.group(1), m.group(2), m.group(3), m.group(4)),
                    'kind': 'edit',
                    'text': '%d file%s changed' % (n, '' if n == 1 else 's'),
                })
    rc, out = git('log', '-8', '--format=%cI\x1f%s')
    if rc == 0 and out:
        for line in out.split('\n'):
            if '\x1f' in line:
                when, subject = line.split('\x1f', 1)
                events.append({'when': when[:19], 'kind': 'publish', 'text': subject[:60]})
    events.sort(key=lambda e: e['when'], reverse=True)
    return events[:8]


def next_action(stats, pub, unused, bad):
    """The one thing most worth doing right now."""
    if bad:
        return {'tone': 'bad', 'title': '%d broken link%s' % (len(bad), '' if len(bad) == 1 else 's'),
                'body': 'A page points at a picture or file that is not there. Fix this before publishing.',
                'cta': None}
    if not pub['repo']:
        return {'tone': 'info', 'title': 'Not connected to GitHub yet',
                'body': 'Follow START-HERE.md to set up publishing, then come back.', 'cta': None}
    if not pub['everPublished']:
        return {'tone': 'go', 'title': 'Ready for its first publish',
                'body': 'Your site has never been put online. Preview it, then publish.',
                'cta': 'publish'}
    if pub['changed']:
        return {'tone': 'go', 'title': '%d change%s not published yet'
                % (pub['changed'], '' if pub['changed'] == 1 else 's'),
                'body': 'Preview to check them, then publish when you are happy.',
                'cta': 'publish'}
    if unused:
        return {'tone': 'warn', 'title': '%d photo%s not used on any page'
                % (unused, '' if unused == 1 else 's'),
                'body': 'Ask the AI to place them, or delete them from the Photos tab.',
                'cta': 'photos'}
    return {'tone': 'ok', 'title': 'Everything is live and up to date',
            'body': 'Nothing needs doing. Make an edit whenever you like.', 'cta': None}


def full_state():
    s = site_stats()
    imgs = list_images()
    unused = sum(1 for i in imgs if not i['used'])
    bad = broken_links()
    pub = publish_state()
    ok, msg, info = check_credentials()
    return {
        'pages': s['pages'], 'images': s['images'], 'unused': unused,
        'broken': bad, 'publish': pub, 'activity': activity(),
        'repo': info.get('repo', ''), 'user': info.get('user', ''),
        'next': next_action(s, pub, unused, bad),
    }


def free_port(start=8770):
    for p in range(start, start + 40):
        with socket.socket() as s:
            try:
                s.bind(('127.0.0.1', p))
                return p
            except OSError:
                continue
    raise RuntimeError('no free port')


def start_preview():
    if PREVIEW['port']:
        return PREVIEW['port']
    if not os.path.isdir(SITE):
        run([sys.executable, os.path.join(SCRIPTS, 'build_index.py'),
             'html_files', '_site', 'unlisted'])
    port = free_port(8790)
    handler = partial(SimpleHTTPRequestHandler, directory=SITE)
    srv = ThreadingHTTPServer(('127.0.0.1', port), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    PREVIEW['port'] = port
    return port


# ------------------------------------------------------------------ http
class Admin(BaseHTTPRequestHandler):
    server_version = 'MEAAdmin'

    def log_message(self, *a):
        pass  # keep the console clean for the user

    # ---- guards
    def _authorised(self):
        if self.headers.get('X-Admin-Token') == TOKEN:
            return True
        self._json({'ok': False, 'error': 'Not authorised.'}, 403)
        return False

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get('Content-Length') or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n).decode('utf-8'))
        except Exception:
            return {}

    # ---- routes
    def do_GET(self):
        if self.path in ('/', '/index.html'):
            html = io.open(os.path.join(SCRIPTS, 'admin.html'), encoding='utf-8').read()
            html = html.replace('<body>', '<body data-token="%s">' % TOKEN, 1)
            body = html.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path in ('/api/status', '/api/state'):
            if not self._authorised():
                return
            self._json(full_state())
            return

        if self.path == '/api/images':
            if not self._authorised():
                return
            self._json({'ok': True, 'images': list_images(), 'sections': list(SECTIONS)})
            return

        # thumbnails for the gallery, read-only, confined to the images folder
        if self.path.startswith('/img/'):
            rel = self.path[len('/img/'):].split('?')[0]
            full = os.path.normpath(os.path.join(PAGES, rel))
            if not full.startswith(os.path.normpath(os.path.join(PAGES, 'images'))) \
               or not os.path.isfile(full):
                self.send_error(404)
                return
            ctype = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
                     '.gif': 'image/gif', '.svg': 'image/svg+xml',
                     '.webp': 'image/webp'}.get(os.path.splitext(full)[1].lower(),
                                                'application/octet-stream')
            data = open(full, 'rb').read()
            self.send_response(200)
            self.send_header('Content-Type', ctype)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(data)
            return

        self.send_error(404)

    def do_POST(self):
        if not self._authorised():
            return
        route = self.path.split('?')[0]

        if route == '/api/export':
            rc, out = run([sys.executable, os.path.join(SCRIPTS, 'ai_export.py')])
            path = os.path.join(ROOT, 'AI-PROMPT.md')
            if rc != 0 or not os.path.isfile(path):
                self._json({'ok': False, 'error': out or 'The export script failed.'})
                return
            prompt = io.open(path, encoding='utf-8').read()
            self._json({'ok': True, 'prompt': prompt, 'summary': out.strip()})
            return

        if route == '/api/import':
            reply = (self._body().get('reply') or '').strip()
            if not reply:
                self._json({'ok': False, 'output': 'Nothing was pasted.'})
                return
            io.open(os.path.join(ROOT, 'AI-RESPONSE.md'), 'w',
                    encoding='utf-8', newline='\n').write(reply + '\n')
            rc, out = run([sys.executable, os.path.join(SCRIPTS, 'ai_import.py')])
            self._json({'ok': rc == 0, 'output': out.strip() or '(no output)'})
            return

        if route == '/api/upload':
            body = self._body()
            try:
                info = save_upload(body.get('name', ''), body.get('section', ''),
                                   body.get('data', ''))
                self._json({'ok': True, 'image': info})
            except Exception as e:
                self._json({'ok': False, 'error': str(e)})
            return

        if route == '/api/imagedelete':
            try:
                stamp = delete_image(self._body().get('path', ''))
                self._json({'ok': True, 'backup': stamp})
            except Exception as e:
                self._json({'ok': False, 'error': str(e)})
            return

        if route == '/api/preview':
            try:
                rc, out = run([sys.executable, os.path.join(SCRIPTS, 'build_index.py'),
                               'html_files', '_site', 'unlisted'])
                port = start_preview()
                self._json({'ok': True, 'url': 'http://127.0.0.1:%d/' % port})
            except Exception as e:
                self._json({'ok': False, 'error': 'Could not start the preview: %s' % e})
            return

        if route == '/api/publish':
            ok, msg, info = check_credentials()
            if not ok:
                self._json({'ok': False, 'output': msg})
                return
            bat = os.path.join(ROOT, 'PUBLISH.bat')
            if not os.path.isfile(bat):
                self._json({'ok': False, 'output': 'PUBLISH.bat is missing from this folder.'})
                return
            # PUBLISH.bat ends with "pause"; feeding it no stdin lets it finish on its own.
            rc, out = run(['cmd', '/c', bat])
            out = re.sub(r'Press any key to close this window\.?', '', out).strip()
            self._json({'ok': rc == 0, 'output': out or '(no output)'})
            return

        self.send_error(404)


def main():
    ok, msg, info = check_credentials()
    if not ok:
        print()
        print('  -----------------------------------------------------')
        print('    THE ADMIN PAGE CANNOT START')
        print('  -----------------------------------------------------')
        print()
        for line in msg.split('\n'):
            print('   ' + line)
        print()
        return 1

    # Normally we hunt for a free port. MEA_ADMIN_PORT pins it, which keeps
    # automated checks pointing at the right place.
    fixed = os.environ.get('MEA_ADMIN_PORT')
    port = int(fixed) if fixed else free_port(8770)
    url = 'http://127.0.0.1:%d/' % port
    try:
        srv = ThreadingHTTPServer(('127.0.0.1', port), Admin)
    except OSError as e:
        print()
        print('   Port %d is already in use (%s).' % (port, e))
        print('   Close any other admin window and try again.')
        return 1

    print()
    print('   Signed in as   %s' % info['user'])
    print('   Repository     %s' % info['repo'])
    print()
    print('   Your admin page is open at:')
    print('     %s' % url)
    print()
    print('   It is reachable only from this computer.')
    print('   Keep this black window open while you work.')
    print('   Close it when you are finished.')
    print()

    if not os.environ.get('MEA_ADMIN_NO_BROWSER'):
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print('   Shutting down.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
