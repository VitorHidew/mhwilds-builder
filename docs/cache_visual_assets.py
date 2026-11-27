"""Cache verified game renders from the project's existing public image sources.

Run manually: python docs/cache_visual_assets.py
No generated art or image transformations. Attribution is stored with each file.
"""
import hashlib
import ast
import argparse
import json
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'static' / 'assets' / 'catalog'
ORIGIN = 'https://www.phantombrawlers.com'


class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            self.images.append(dict(attrs))


def read(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != 'https' or parsed.hostname not in {'www.phantombrawlers.com', 'static0.fextralifeimages.com', 'unpkg.com'}:
        raise ValueError('Unexpected image source')
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'WildsForge/1.0'}), timeout=15) as response:
        body = response.read(12_000_001)
        if len(body) > 12_000_000:
            raise ValueError('Asset exceeds limit')
        return body, response.headers.get_content_type()


def cache(key, url, page, manifest):
    if key in manifest and (ROOT / 'static' / manifest[key]['path'].lstrip('/')).exists():
        return True
    try:
        body, mime = read(url)
        if not mime.startswith('image/') or not (body.startswith(b'\x89PNG') or body.startswith(b'\xff\xd8') or (body[:4] == b'RIFF' and body[8:12] == b'WEBP')):
            raise ValueError('Not a supported bitmap')
        suffix = '.webp' if body[:4] == b'RIFF' else '.png' if body.startswith(b'\x89PNG') else '.jpg'
        file = hashlib.sha256(key.encode()).hexdigest()[:24] + suffix
        (DEST / file).write_bytes(body)
        manifest[key] = {'path':f'/assets/catalog/{file}', 'source':url, 'page':page,
                         'sha256':hashlib.sha256(body).hexdigest(), 'bytes':len(body), 'rights':'Game artwork: CAPCOM; source attribution is not a redistribution license.'}
        (DEST / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), 'utf-8')
        print('OK', key, len(body), flush=True)
        return True
    except Exception as error:
        print('UNAVAILABLE', key, str(error)[:100], flush=True)
        return False


def main():
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument('--equipment', action='store_true', help='Also cache exact armor renders used by the saved recommendation catalog.')
    options = args.parse_args()
    DEST.mkdir(parents=True, exist_ok=True)
    file = DEST / 'manifest.json'
    manifest = json.loads(file.read_text('utf-8')) if file.exists() else {}
    data = json.loads((ROOT / 'app' / 'game_data.json').read_text('utf-8'))
    parser = Images()
    parser.feed(read(ORIGIN + '/mhwilds/Monsters')[0].decode())
    icons = {image.get('alt'):urllib.parse.urljoin(ORIGIN,image.get('src','')) for image in parser.images if '/Large%20Icons/' in image.get('src','')}
    for monster in data['monsters']:
        name = monster.get('name_en') or monster['name']
        key = 'monster:' + name
        # The source's Gogmazios render is 15360x8640. Use its official game
        # illustration at UI scale instead of decoding a 132 MP bitmap.
        if name == 'Gogmazios' and name in icons:
            if manifest.get(key, {}).get('source') != icons[name]:
                manifest.pop(key, None)
                cache(key, icons[name], ORIGIN + '/mhwilds/Monsters', manifest)
            continue
        if key in manifest:
            continue
        page = ORIGIN + '/MHWilds/Monsters/' + urllib.parse.quote(name)
        detail = Images()
        try:
            detail.feed(read(page)[0].decode())
            sources = [urllib.parse.urljoin(ORIGIN,img['src']) for img in detail.images if '/Large%20Renders/' in img.get('src','') and img.get('alt') == name]
            if sources and cache(key, sources[0], page, manifest):
                continue
        except Exception as error:
            print('PAGE', name, str(error)[:80], flush=True)
        if name in icons:
            cache(key, icons[name], ORIGIN + '/mhwilds/Monsters', manifest)
    # Exact Gogma appearance mappings are already maintained in the backend.
    source = (ROOT / 'app' / 'main.py').read_text('utf-8')
    mapping = {}
    for node in ast.parse(source).body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == 'GOGMA_WEAPON_IMAGES':
            mapping = ast.literal_eval(node.value)
        elif isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'GOGMA_WEAPON_IMAGES' for target in node.targets):
            mapping = ast.literal_eval(node.value)
    for name, url in mapping.items():
        cache('weapon:' + name, url, 'https://monsterhunterwilds.wiki.fextralife.com/Gogma_Artian_Weapons', manifest)
    if options.equipment:
        builds = json.loads((ROOT / 'app' / 'meta_build_cache.json').read_text('utf-8'))['builds']
        armor_ids = {build['equipment'][slot + '_id'] for build in builds for slot in ('helm','chest','arms','waist','legs')}
        sets = {piece['name']:armor_set['name'] for armor_set in data['armor_sets'] for piece in armor_set['pieces']}
        for armor in data['armors']:
            name = armor['name']
            key = 'armor:' + name
            if armor['id'] not in armor_ids or key in manifest or name not in sets:
                continue
            page = ORIGIN + '/MHWilds/Armours/' + urllib.parse.quote(sets[name]) + '/' + urllib.parse.quote(name)
            try:
                parser = Images()
                parser.feed(read(page)[0].decode())
                sources = [urllib.parse.urljoin(ORIGIN,img['src']) for img in parser.images if 'main image' in img.get('alt','').lower() and '/Armour/' in img.get('src','')]
                if sources:
                    cache(key, sources[0], page, manifest)
                else:
                    print('NO EXACT RENDER', name, flush=True)
            except Exception as error:
                print('PAGE', name, str(error)[:80], flush=True)
    file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), 'utf-8')
    print('Assets:', len(manifest), flush=True)


if __name__ == '__main__':
    main()
