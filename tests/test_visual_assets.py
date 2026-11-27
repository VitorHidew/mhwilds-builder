import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app import main


def test_local_catalog_covers_monsters_and_gog_with_attribution():
    catalog = main.STATIC_ASSET_DIR / 'catalog'
    manifest = json.loads((catalog / 'manifest.json').read_text('utf-8'))
    assert len([key for key in manifest if key.startswith('monster:')]) == 34
    for name in main.GOGMA_WEAPON_IMAGES:
        assert 'weapon:' + name in manifest
    for key, record in manifest.items():
        path = main.STATIC_DIR / record['path'].lstrip('/')
        assert path.resolve().parent == catalog.resolve()
        body = path.read_bytes()
        assert hashlib.sha256(body).hexdigest() == record['sha256'], key
        assert len(body) == record['bytes']
        assert record['source'].startswith('https://')
        assert record['page'].startswith('https://')
        assert 'CAPCOM' in record['rights']
        assert body.startswith(b'\x89PNG') or body.startswith(b'\xff\xd8') or (body[:4] == b'RIFF' and body[8:12] == b'WEBP')


def test_gog_photo_uses_local_asset_without_network(monkeypatch):
    monkeypatch.setattr(main, '_wiki_page_image', lambda *_: (_ for _ in ()).throw(AssertionError('network used')))
    with TestClient(main.app) as client:
        response = client.get('/api/equipment-photo/weapon', params={'name':'Ostrak Oblivion'})
        assert response.status_code == 200
        assert response.headers['content-type'] == 'image/png'
        assert len(response.content) > 1000
        assert client.get('/api/equipment-image/weapon', params={'name':'Ostrak Oblivion'}).json()['image_url'].startswith('/assets/catalog/')


def test_catalog_rejects_manifest_traversal(monkeypatch):
    monkeypatch.setattr(Path, 'read_text', lambda *_args, **_kwargs: json.dumps({'weapon:test':{'path':'/assets/catalog/../private.png'}}))
    assert main._catalog_asset('weapon','test') is None
    monkeypatch.setattr(Path, 'read_text', lambda *_args, **_kwargs: '{')
    assert main._catalog_asset('weapon','test') is None


def test_monster_photo_uses_local_catalog_without_network():
    with TestClient(main.app) as client:
        response = client.get('/api/equipment-photo/monster', params={'name': 'Ajarakan'})
        assert response.status_code == 200
        assert response.headers['content-type'] == 'image/webp'
        assert len(response.content) > 1000


def test_armor_catalog_asset_falls_back_across_greek_variants():
    # Gore Helm α or β shares set/slot visual if one variant is in manifest.json
    path = main._catalog_asset('armor', 'Gore Mail β')
    assert path is not None and path.is_file()
