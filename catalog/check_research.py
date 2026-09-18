#!/usr/bin/env python3
"""Check the research collection without contacting a host or network."""
from pathlib import Path
import json
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {'.md', '.json', '.py'}
PATTERNS = {
    'account-qualified path': r'/(?:Users|home)/[^\s/`]+',
    'redaction placeholder': r'(?i)(?:\[(?:redacted|removed|private)[^\]]*\]|<(?:redacted|private[-_ ][^>]+)>)',
    'network address': r'(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])',
    'hardware address': r'(?i)\b(?:[0-9a-f]{2}:){5}[0-9a-f]{2}\b',
    'installation UUID': r'(?i)\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b',
    'private URL': r'https?://[^/\s)]*(?:\.local|\.internal|\.invalid|:3000)(?:[/\s)]|$)',
    'credential-like token': r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{24,})\b',
    'email address': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
    'private key': r'-----BEGIN [A-Z ]*PRIVATE KEY-----',
}


# Mach-O build identifiers identify distributed firmware, not installations.
FIRMWARE_UUIDS = {
    'docs/method/sep-artifacts.md': '-'.join(
        ('D14EC38B', '9DE3', '32B0', '867C', '07C86AE9C97C')),
    'docs/sep/aks-create-v4-j214k.md': '-'.join(
        ('9d8aad8b', '0dbc', '1c37', '95f9', 'cd0316e38d5a')),
}


def anchors(text):
    """GitHub-style anchors for the headings used in this collection."""
    seen, result = {}, set()
    for heading in re.findall(r'^#{1,6}\s+(.+)$', text, re.M):
        slug = re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')
        n = seen.get(slug, 0)
        seen[slug] = n + 1
        result.add(slug if not n else f'{slug}-{n}')
    result.update(re.findall(r'<a id="([^"]+)"></a>', text))
    return result


def verify(root):
    errors = []
    files = sorted(p for p in root.rglob('*') if p.is_file()
                   and not any(part in {'.git', '__pycache__', '.DS_Store'}
                               for part in p.relative_to(root).parts))
    texts = {}
    for path in files:
        rel = path.relative_to(root)
        if path.suffix not in ALLOWED and path.name not in {'LICENSE', '.gitignore'}:
            errors.append(f'{rel}: unexpected publication file type')
            continue
        try:
            text = path.read_text()
        except UnicodeError:
            errors.append(f'{rel}: binary content')
            continue
        texts[path] = text
        if path.suffix == '.json' and not text.isascii():
            characters = ', '.join(f'U+{ord(c):04X}' for c in sorted(set(text)) if ord(c) > 127)
            errors.append(f'{rel}: non-ASCII JSON characters ({characters}); use ASCII notation or JSON Unicode escapes')
        for label, pattern in PATTERNS.items():
            for m in re.finditer(pattern, text):
                if label == 'installation UUID' and m.group().lower() == FIRMWARE_UUIDS.get(rel.as_posix(), '').lower():
                    continue
                line = text.count('\n', 0, m.start()) + 1
                errors.append(f'{rel}:{line}: {label}')
        if re.search(r'^\|.*(?:SHA-256|sha256)', text, re.M):
            for token in re.findall(r'`([0-9a-f]{50,70})`', text):
                if len(token) != 64:
                    errors.append(f'{rel}: malformed SHA-256')
        for line, value in enumerate(text.splitlines(), 1):
            if value.rstrip() != value:
                errors.append(f'{rel}:{line}: trailing whitespace')

    def check_link(origin, target):
        url = urlsplit(target)
        if url.scheme:
            if url.scheme != 'https':
                errors.append(f'{origin.relative_to(root)}: non-HTTPS external link')
            return
        dest = (origin.parent / unquote(url.path)).resolve() if url.path else origin
        if not dest.is_relative_to(root.resolve()) or not dest.is_file():
            errors.append(f'{origin.relative_to(root)}: missing or escaping link {target}')
        elif url.fragment and dest.suffix == '.md':
            if unquote(url.fragment) not in anchors(dest.read_text()):
                errors.append(f'{origin.relative_to(root)}: missing anchor {target}')

    for path, text in texts.items():
        if path.suffix == '.md':
            for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text):
                check_link(path, target)
    try:
        findings = json.loads((root / 'catalog/findings.json').read_text())
        ids = [f['id'] for f in findings['findings']]
        if len(set(ids)) != len(ids):
            errors.append('findings.json: duplicate finding ID')
        for item in findings['findings']:
            if any(not item.get(key) for key in ('id', 'reference', 'evidence', 'finding', 'scope')):
                errors.append('findings.json: missing required field')
            check_link(root / 'README.md', item['reference'])
        boards = json.loads((root / 'catalog/boards.json').read_text())
        records = boards['boards']
        if len(records) != 16 or len({b['ibridge'] for b in records}) != 16:
            errors.append('boards.json: expected 16 distinct production configurations')
        if boards['bridgeos_build'] != findings['scope']['bridgeos_build']:
            errors.append('board and finding build scopes disagree')
        doc = (root / 'docs/platform/board-configurations.md').read_text()
        rows = [[c.strip().replace('`', '') for c in line.strip('|').split('|')]
                for line in doc.splitlines() if line.startswith('| `iBridge')]
        for b in records:
            wanted = [b['ibridge'], b['board']+' / '+b['board_id'], b['mac_model'],
                      b['kernelcache'], str(b['min_sleep_state']), b['aop_profile'],
                      'yes' if b['spi_multitouch'] else 'no',
                      'yes' if b['codec_power_off_at_sleep'] else 'no']
            digest = b['devicetree_im4p']['sha256']
            hash_row = [b['ibridge']+' / '+b['board'],
                        format(b['devicetree_im4p']['bytes'], ','), digest]
            if wanted not in rows or hash_row not in rows:
                errors.append(f'board data/table mismatch: {b["ibridge"]}')
            if not re.fullmatch('[0-9a-f]{64}', digest):
                errors.append(f'invalid DeviceTree digest: {b["ibridge"]}')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f'index structure: {type(exc).__name__}')
    from research import validate
    errors.extend(validate(root))
    return errors, len(files)


if __name__ == '__main__':
    errors, count = verify(ROOT)
    print(json.dumps({'ok': not errors, 'files': count, 'errors': errors}, separators=(',', ':')))
    sys.exit(bool(errors))
