#!/usr/bin/env python3
"""Offline research discovery and deterministic human-map generation."""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
GENERATED = {'docs/README.md', 'docs/platform/research-coverage.md'}
STATUSES = {
    'bounded-static-complete': 'Bounded static analysis complete',
    'missing-input': 'Missing artifact or input',
    'runtime-evidence-needed': 'Runtime evidence needed',
    'physical-qualification-needed': 'Physical qualification needed',
    'qualification-decision': 'Qualification decision needed',
}


def read_catalog(root=ROOT):
    return json.loads((root / 'catalog/research-map.json').read_text())


def read_findings(root=ROOT):
    return json.loads((root / 'catalog/findings.json').read_text())


def heading_spans(text):
    """Map Markdown heading anchors to inclusive one-based section ranges."""
    seen, headings = {}, []
    lines = text.splitlines()
    fenced = False
    for number, line in enumerate(lines, 1):
        if line.startswith('```'):
            fenced = not fenced
        match = re.match(r'^(#{1,6})\s+(.+)$', line) if not fenced else None
        if not match:
            continue
        depth, title = len(match[1]), match[2]
        slug = re.sub(r'[^\w\- ]', '', title.lower()).replace(' ', '-')
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        headings.append((slug if not count else f'{slug}-{count}', number, depth))
    return {slug: (start, next((n - 1 for _, n, d in headings[i+1:] if d <= depth), len(lines)))
            for i, (slug, start, depth) in enumerate(headings)}


def location(root, reference):
    url = urlsplit(reference)
    if url.scheme or url.netloc or url.query:
        raise ValueError(f'expected repository reference: {reference}')
    path = (root / unquote(url.path)).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError(f'missing or escaping reference: {reference}')
    text = path.read_text()
    if url.fragment:
        anchor = unquote(url.fragment)
        spans = heading_spans(text)
        if anchor not in spans:
            raise ValueError(f'missing heading: {reference}')
        start, end = spans[anchor]
    else:
        start, end = 1, len(text.splitlines())
    return {'reference': reference, 'line_start': start, 'line_end': end}


def normalize(value):
    return re.sub(r'[^a-z0-9]', '', value.casefold())


def search(catalog, query, limit=5):
    q = normalize(query)
    if not q:
        return []
    found = []
    for topic in catalog['topics']:
        named = [topic['id'], topic['title'], *topic['aliases'],
                 *topic['linux_interfaces'], *topic['firmware_components']]
        matches = [s for s in named if q == normalize(s)]
        if q == normalize(topic['id']):
            score = 150
        elif matches:
            score = 100
        else:
            # Short acronyms must not match the middle of unrelated words
            # (for example, ISP inside "display"). Longer prefixes are useful
            # for names such as multitouch and AppleKeyStore.
            matches = [s for s in [*named, topic['function']]
                       if any(q == token or (len(q) >= 4 and token.startswith(q))
                              for token in re.findall(r'[a-z0-9]+', s.casefold()))]
            score = 50 if matches else 0
        if score:
            matches = list({normalize(s): s for s in matches}.values())
            found.append((score, {'id': topic['id'], 'title': topic['title'],
                                'matched': matches, 'references': topic['references']}))
    return [r for _, r in sorted(found, key=lambda x: (-x[0], x[1]['id']))[:limit]]


def show(root, catalog, query):
    exact = [t for t in catalog['topics'] if normalize(query) == normalize(t['id'])]
    if not exact:
        exact = [t for t in catalog['topics'] if normalize(query) in
                 {normalize(s) for s in [t['title'], *t['aliases']]}]
    if len(exact) != 1:
        raise ValueError('use a unique topic ID; candidates: ' + ', '.join(r['id'] for r in search(catalog, query, 50)))
    topic = exact[0]
    findings = {f['id']: f for f in read_findings(root)['findings']}
    documents = [d for d in catalog['documents'] if topic['id'] in d['topics']]
    return {**topic, 'references': [location(root, r) for r in topic['references']],
            'findings': [findings[i] for i in topic['finding_ids']],
            'documents': documents,
            'relationships': [r for r in catalog['relationships'] if topic['id'] in (r['source'], r['target'])],
            'interfaces': [i for i in catalog['interfaces'] if topic['id'] in i['topics']],
            'coverage': [c for c in catalog['coverage'] if topic['id'] in c['topics']],
            'scope': catalog['scope']}


def link(reference, origin):
    path, sep, anchor = reference.partition('#')
    return os.path.relpath(path, str(Path(origin).parent)) + sep + anchor


def render(catalog, findings):
    by_id = {f['id']: f for f in findings['findings']}
    titles = {d['path']: d['title'] for d in catalog['documents']}
    topics = {t['id']: t for t in catalog['topics']}
    out = ['# Research map', '',
           'Find a topic by its Linux name, firmware component, device ID, or function.',
           'This map is generated from [research-map.json](../catalog/research-map.json).',
           'The [catalog guide](../catalog/README.md) describes machine lookups and the schema.', '',
           'Use the [coverage map](platform/research-coverage.md) for the limits of each investigation.',
           'A relationship below is qualified evidence, not a claim that a feature works.', '',
           '## Topics', '', '| Topic | Function |', '| --- | --- |']
    for t in topics.values():
        out.append(f"| [{t['title']}](#{t['id']}) | {t['function']} |")
    for t in topics.values():
        out += ['', f'<a id="{t["id"]}"></a>', '', '## '+t['title'], '', t['function']+'.', '',
                '**Look up:** '+', '.join('`'+a+'`' for a in t['aliases'])+'.', '',
                '**Linux interfaces:** '+', '.join(t['linux_interfaces'])+'.', '',
                '**Firmware/component names:** '+', '.join(t['firmware_components'])+'.', '',
                '| Read | Reference |', '| --- | --- |']
        for i, ref in enumerate(t['references']):
            out.append(f"| {'Start here' if not i else 'Related analysis'} | [{titles.get(ref.split('#')[0], ref)}]({link(ref, 'docs/README.md')}) |")
        if t['finding_ids']:
            out += ['', '**Findings:** '+', '.join(f"[{i}]({link(by_id[i]['reference'], 'docs/README.md')})" for i in t['finding_ids'])+'.']
        coverage = [c for c in catalog['coverage'] if t['id'] in c['topics']]
        if coverage:
            out += ['', '**Examined areas:** '+', '.join(f"[{c['id']}: {c['title']}](platform/research-coverage.md#{c['id'].lower()})" for c in coverage)+'.']
    out += ['', '## Interface routes', '',
            'This partial interface map records the inspected host routes. A USB parent',
            'identifies its host transport; it does not prove the embedded firmware owner.', '',
            '| Interface | Parent route | Identity | PCI function / DART stream | Scope and evidence |',
            '| --- | --- | --- | --- | --- |']
    for interface in catalog['interfaces']:
        assignment = f"{interface['function']} / {interface['dart_stream']}" if 'function' in interface else '—'
        out.append(f"| `{interface['id']}` ({interface['type']}) | {interface['parent'] or 'Host PCIe'} | `{interface['identity']}` | {assignment} | [{interface['scope']}]({link(interface['reference'], 'docs/README.md')}) ({interface['evidence']}) |")
    out += ['', '## Relationships and evidence limits', '',
            'These edges connect investigated services and functions. Inferred and unresolved',
            'edges remain visibly distinct from recovered contracts and observations.', '',
            '| From → to | Relationship | Evidence | Interpretation and source |', '| --- | --- | --- | --- |']
    for r in catalog['relationships']:
        out.append(f"| [{r['source']}](#{r['source']}) → [{r['target']}](#{r['target']}) | {r['kind']} | {r['evidence']} | [{r['description']}]({link(r['reference'], 'docs/README.md')}) |")
    out += ['', '## Complete chapter inventory', '', '| Chapter | Topics |', '| --- | --- |']
    for d in catalog['documents']:
        ts=('Cross-cutting method' if d['kind']=='method' else 'Cross-cutting reference') if len(d['topics']) > 8 else ', '.join(f"[{i}](#{i})" for i in d['topics'])
        out.append(f"| [{d['title']}]({link(d['path'], 'docs/README.md')}) | {ts} |")
    coverage = ['# Research coverage and remaining evidence', '',
                'This is a dated map of examined questions, not a hardware support matrix.',
                'Scope: bridgeOS `23P6068`, with build and board exceptions in the linked',
                'chapters. Coverage reviewed on '+catalog['scope']['coverage_date']+'.', '',
                '“Bounded static analysis complete” means the retained analysis reached its',
                'stated boundary. It does not mean the driver is implemented, safe, or runtime-qualified.',
                'Missing inputs and qualification remain explicit below. A listed next measurement',
                'does not authorize a reset, firmware write, or disruptive hardware experiment.', '',
                'Generated from [research-map.json](../../catalog/research-map.json).', '',
                '| Disposition | Examined areas |', '| --- | ---: |']
    counts=Counter(c['status'] for c in catalog['coverage'])
    for status,title in STATUSES.items(): coverage.append(f'| {title} | {counts[status]} |')
    for c in catalog['coverage']:
        coverage += ['', f'<a id="{c["id"].lower()}"></a>', '', f"## {c['id']}: {c['title']}", '',
                     STATUSES[c['status']]+'.', '', c['limit'], '',
                     'Read: '+', '.join(f'[{titles.get(r.split("#")[0],r)}]({link(r,"docs/platform/research-coverage.md")})' for r in c['references'])+'.']
    return {'docs/README.md': '\n'.join(out).rstrip()+'\n',
            'docs/platform/research-coverage.md': '\n'.join(coverage).rstrip()+'\n'}


def validate(root=ROOT):
    errors=[]
    try:
        c=read_catalog(root); f=read_findings(root)
        if c['schema_version'] != 1: errors.append('unsupported research catalog schema')
        groups=('topics','documents','coverage','interfaces')
        for group in groups:
            ids=[x['id'] for x in c[group]]
            if len(ids)!=len(set(ids)): errors.append(f'duplicate {group} ID')
        tids={t['id'] for t in c['topics']}; fids={x['id'] for x in f['findings']}
        assigned=set(); refs=[]
        for t in c['topics']:
            if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',t['id']): errors.append(f'invalid topic ID: {t["id"]}')
            for key in ('title','aliases','linux_interfaces','firmware_components','function','references'):
                if not t.get(key):errors.append(f'{t["id"]}: missing {key}')
            assigned.update(t['finding_ids']);refs.extend(t['references'])
        if fids-assigned:errors.append('unmapped findings: '+','.join(sorted(fids-assigned)))
        if assigned-fids:errors.append('unknown findings: '+','.join(sorted(assigned-fids)))
        paths=[d['path'] for d in c['documents']]
        if len(paths)!=len(set(paths)):errors.append('duplicate document path')
        for d in c['documents']:
            refs.append(d['path'])
            if not d['topics'] or set(d['topics'])-tids:errors.append(f'{d["id"]}: invalid document topics')
            path = root / d['path']
            if path.is_file() and path.read_text().splitlines()[0] != '# ' + d['title']:
                errors.append(f'{d["id"]}: catalog title disagrees with chapter')
        for r in c['relationships']:
            if r['source'] not in tids or r['target'] not in tids:errors.append('unknown relationship topic')
            if r['evidence'] not in {'observed','recovered','inferred','unresolved'}:errors.append('invalid relationship evidence')
            if not r['kind'] or not r['description']:errors.append('unqualified relationship')
            refs.append(r['reference'])
        interfaces={i['id']: i for i in c['interfaces']}
        for item in interfaces.values():
            if not item['topics'] or set(item['topics'])-tids:
                errors.append(f'{item["id"]}: invalid interface topics')
            seen={item['id']}
            parent=item['parent']
            while parent is not None:
                if parent not in interfaces or parent in seen:
                    errors.append(f'{item["id"]}: invalid or cyclic interface parent')
                    break
                seen.add(parent)
                parent=interfaces[parent]['parent']
            if not all(item.get(k) for k in ('identity','type','evidence','scope')):
                errors.append(f'{item["id"]}: incomplete interface evidence')
            refs.append(item['reference'])
            if 'observation_reference' in item:
                refs.append(item['observation_reference'])
        for item in c['coverage']:
            if item['status'] not in STATUSES or not item['limit']:errors.append(f'{item["id"]}: invalid disposition')
            if not item['topics'] or set(item['topics'])-tids:errors.append(f'{item["id"]}: invalid coverage topics')
            refs.extend(item['references'])
        actual={p.relative_to(root).as_posix() for p in (root/'docs').rglob('*.md')}
        if actual != set(paths)|GENERATED:
            errors.append('document inventory mismatch: '+','.join(sorted(actual ^ (set(paths)|GENERATED))))
        for ref in sorted(set(refs)):
            try:location(root,ref)
            except ValueError as exc:errors.append(str(exc))
        for path, text in render(c,f).items():
            if not (root/path).is_file() or (root/path).read_text()!=text:errors.append(f'{path}: generated map stale; run catalog/research.py build')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append('catalog structure: '+str(exc))
    return errors


def main():
    p=argparse.ArgumentParser(description=__doc__)
    commands=p.add_subparsers(dest='command',required=True)
    s=commands.add_parser('search',help='find topic IDs using Linux/firmware names or device IDs')
    s.add_argument('query');s.add_argument('--limit',type=int,default=5)
    s=commands.add_parser('show',help='resolve one topic to exact sections, findings, scope, and limits')
    s.add_argument('topic')
    commands.add_parser('build',help='regenerate the human maps from the catalog')
    commands.add_parser('check',help='check catalog contracts and generated maps')
    args=p.parse_args()
    try:
        c=read_catalog()
        if args.command=='search':
            if not 1<=args.limit<=50:p.error('--limit must be between 1 and 50')
            result={'query':args.query,'results':search(c,args.query,args.limit)}
        elif args.command=='show':result=show(ROOT,c,args.topic)
        elif args.command=='build':
            built=render(c,read_findings())
            for path,text in built.items():(ROOT/path).write_text(text)
            result={'generated':list(built)}
        else:
            errors=validate();result={'ok':not errors,'errors':errors}
            print(json.dumps(result,separators=(',',':'),ensure_ascii=False));return bool(errors)
        print(json.dumps(result,separators=(',',':'),ensure_ascii=False));return 0
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print(json.dumps({'error':str(exc)},separators=(',',':')),file=sys.stderr);return 1


if __name__=='__main__':
    sys.exit(main())
