#!/usr/bin/env python3
"""Пересобирает индекс источника SmockingRider (Cydia/Sileo/Zebra):
Packages, Packages.gz, Packages.bz2 и список пакетов в index.html.

У каждого приложения свой репозиторий GitHub с папкой debs/ и включёнными
Pages: https://smockingrider.github.io/<приложение>/debs/… Список приложений —
apps.txt (по одному имени репозитория в строке). Локальные копии этих
репозиториев лежат в APPS_DIR (по умолчанию ../SmockingRider-apps).
Пакеты в debs/ самого источника тоже учитываются.
Только стандартная библиотека Python.
    python3 tools/update-repo.py"""
import bz2, gzip, hashlib, io, lzma, os, re, tarfile, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS_DIR = os.environ.get('APPS_DIR', os.path.join(os.path.dirname(ROOT), 'SmockingRider-apps'))
FIELD_ORDER = ['Package', 'Name', 'Version', 'Architecture', 'Maintainer', 'Author',
               'Installed-Size', 'Depends', 'Conflicts', 'Replaces', 'Section',
               'Description', 'Depiction', 'Icon']

def ar_members(data):
    if not data.startswith(b'!<arch>\n'):
        raise ValueError('не .deb')
    pos = 8
    while pos < len(data):
        name = data[pos:pos + 16].decode().strip().rstrip('/')
        size = int(data[pos + 48:pos + 58].decode().strip())
        pos += 60
        yield name, data[pos:pos + size]
        pos += size + (size & 1)

def control_of(path):
    data = open(path, 'rb').read()
    for name, body in ar_members(data):
        if name.startswith('control.tar'):
            if name.endswith('.xz') or name.endswith('.lzma'):
                body = lzma.decompress(body)
            elif name.endswith('.gz'):
                body = gzip.decompress(body)
            with tarfile.open(fileobj=io.BytesIO(body)) as t:
                for m in t.getmembers():
                    if m.name.lstrip('./') == 'control':
                        return t.extractfile(m).read().decode('utf-8'), data
    raise ValueError('нет control в ' + path)

def parse(text):
    fields, key = {}, None
    for line in text.splitlines():
        if line.startswith((' ', '\t')) and key:
            fields[key] += '\n' + line
        elif ':' in line:
            key, val = line.split(':', 1)
            fields[key.strip()] = val.strip()
    return fields

def ver_key(v):
    return [int(x) if x.isdigit() else x for x in re.split(r'[.\-~+]', v)]

def sources():
    """(папка с .deb, префикс пути от корня источника)"""
    yield os.path.join(ROOT, 'debs'), 'debs/'
    apps = os.path.join(ROOT, 'apps.txt')
    if os.path.exists(apps):
        for line in open(apps, encoding='utf-8'):
            name = line.split('#')[0].strip()
            if not name:
                continue
            d = os.path.join(APPS_DIR, name, 'debs')
            if not os.path.isdir(d):
                raise SystemExit('нет папки %s — склонируйте репозиторий %s в %s' % (d, name, APPS_DIR))
            yield d, name + '/debs/'

entries = []
for folder, prefix in sources():
    if not os.path.isdir(folder):
        continue
    for f in sorted(os.listdir(folder)):
        if not f.endswith('.deb'):
            continue
        p = os.path.join(folder, f)
        text, data = control_of(p)
        c = parse(text)
        c['Filename'] = prefix + f
        c['Size'] = str(len(data))
        c['MD5sum'] = hashlib.md5(data).hexdigest()
        c['SHA1'] = hashlib.sha1(data).hexdigest()
        c['SHA256'] = hashlib.sha256(data).hexdigest()
        entries.append(c)
entries.sort(key=lambda c: (c['Package'], ver_key(c.get('Version', '0'))))

out = []
for c in entries:
    keys = [k for k in FIELD_ORDER if k in c] + \
           [k for k in c if k not in FIELD_ORDER and k not in ('Filename', 'Size', 'MD5sum', 'SHA1', 'SHA256')] + \
           ['Filename', 'Size', 'MD5sum', 'SHA1', 'SHA256']
    out.append('\n'.join('%s: %s' % (k, c[k]) for k in keys))
packages = ('\n\n'.join(out) + '\n').encode('utf-8')
open(os.path.join(ROOT, 'Packages'), 'wb').write(packages)
with gzip.GzipFile(os.path.join(ROOT, 'Packages.gz'), 'wb', mtime=0) as g:
    g.write(packages)
open(os.path.join(ROOT, 'Packages.bz2'), 'wb').write(bz2.compress(packages))

# список в index.html между маркерами
idx = os.path.join(ROOT, 'index.html')
page = open(idx, encoding='utf-8').read()
rows = '\n'.join('<li><b>%s</b> %s — %s (%s)</li>' % (
    html.escape(c.get('Name', c['Package'])), html.escape(c['Version']),
    html.escape(c.get('Description', '').split('\n')[0]), html.escape(c['Architecture']))
    for c in entries)
page = re.sub(r'<!-- packages -->.*<!-- /packages -->',
              '<!-- packages -->\n<ul>\n' + rows + '\n</ul>\n<!-- /packages -->', page, flags=re.S)
open(idx, 'w', encoding='utf-8').write(page)
for c in entries:
    print('%-40s %-10s %s' % (c['Package'], c['Version'], c['Architecture']))
