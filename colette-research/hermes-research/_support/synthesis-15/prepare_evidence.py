"""Preserve selected published passages without reading trace reservoirs."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys

sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parents[2]
SUPPORT = Path(__file__).resolve().parent
ORIGINAL = Path('/home/resonatingloop/.resonance/stigmergy/help-peer/hermes-research')
STAGE = BASE / 'stage-3-event-discovery'
ROOTS = {'top': ORIGINAL, 'stage3': STAGE}
SCRIPT = Path('/home/resonatingloop/.hermes/skills/research/grounded-citations/scripts/sources.py')
spec = importlib.util.spec_from_file_location('citation_tools', SCRIPT)
assert spec is not None and spec.loader is not None
cite = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cite)
LEDGER = SUPPORT / 'citation-ledger.json'
SELECTIONS = [
    ('top', 70, [(351,351),(435,459),(543,566),(582,608),(630,636),(710,718),(854,876),(887,895),(905,921),(933,933),(1040,1040)]),
    ('top', 76, [(835,841)]),
    ('top', 78, [(449,453),(470,472),(490,494),(511,513),(758,768)]),
    ('top', 67, [(106,138),(175,175),(402,407)]),
    ('top', 64, [(129,129),(359,359),(415,420),(454,454)]),
    ('top', 87, [(19,27),(31,41),(51,58),(76,84),(90,92),(108,124)]),
    ('top', 68, [(220,228),(290,290),(296,304)]),
    ('top', 65, [(13,21),(29,38),(52,60),(145,159)]),
    ('top', 66, [(57,61),(93,109),(153,155),(173,175),(195,195),(41,41)]),
    ('top', 97, [(53,63),(71,84),(88,96),(108,120)]),
    ('stage3', 15, [(17,39),(69,79)]),
    ('stage3', 21, [(75,75),(133,135)]),
    ('stage3', 23, [(235,237),(459,465)]),
    ('stage3', 26, [(51,57),(107,113),(162,162)]),
    ('stage3', 22, [(48,48),(60,76),(124,124),(188,188)]),
    ('stage3', 32, [(372,384),(480,480)]),
    ('stage3', 33, [(137,137),(830,862),(1113,1127),(913,918)]),
    ('top', 80, [(47,57)]),
]

def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()

def save_new_or_identical(path, text):
    if path.exists():
        current = path.read_text()
        if current.rstrip() != text.rstrip():
            raise RuntimeError(f'Unexpected changed output: {path}')
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    os.chmod(path, 0o600)

metadata = {}
ledgers = {}
for namespace, root in ROOTS.items():
    data = json.loads((root / '_support/source-records.json').read_text())
    rows = data if isinstance(data, list) else data['sources']
    metadata[namespace] = {row['id']: row for row in rows}
    ledgers[namespace] = json.loads((root / '_support/citation-ledger.json').read_text())['sources']

records = []
for namespace, upstream_id, ranges in SELECTIONS:
    record = metadata[namespace][upstream_id]
    path = ROOTS[namespace] / record['evidence_path']
    body = path.read_text()
    lines = body.splitlines(keepends=True)
    source = cite.add_sources(LEDGER, [record['url']], title=record['title'], accessed='2026-10-01')[0]
    local_id = source['id']
    chunks = []
    passages = []
    for index, (start, end) in enumerate(ranges, 1):
        text = ''.join(lines[start-1:end]).strip()
        if len(text.split()) < 3:
            raise RuntimeError(f'Empty evidence: {namespace}:{upstream_id}:{start}')
        passage_id = f'S15-{local_id:02d}-P{index:02d}'
        chunks.append(f'## {passage_id}; upstream lines {start}-{end}\n\n{text}\n')
        passages.append({'passage_id': passage_id, 'upstream_lines': [start, end], 'exact_text': text})
    pack = (f'# Private working excerpts: source {local_id}\n\nPublished URL: {record["url"]}\n'
            f'Upstream namespace: {namespace}; source {upstream_id}\nVersion/date: {record.get("date")}\n\n'
            + '\n'.join(chunks))
    relative = f'evidence/source-{local_id:02d}-excerpts.txt'
    save_new_or_identical(SUPPORT / relative, pack)
    for passage in passages:
        cite.attach_quote(LEDGER, local_id, passage['exact_text'], pack)
    mappings = [{'namespace': label, 'id': item['id']} for label, items in ledgers.items()
                for item in items if cite.normalize_url(item['url']) == source['url']]
    records.append({'local_id': local_id, 'url': source['url'], 'title': record['title'],
                    'publication_or_version': record.get('date'), 'evidence_type': record.get('type'),
                    'limits': record.get('limits'), 'upstream_mappings': mappings,
                    'upstream_body_path': str(path), 'upstream_body_sha256': digest(body),
                    'evidence_path': relative, 'evidence_sha256': digest((SUPPORT / relative).read_text()),
                    'passages': passages})
    print(f'[{local_id}] {namespace}:{upstream_id}; {len(passages)} exact passage selections')

analyses = []
for name, ranges in [('organizational-forensics', [(3,22),(100,114)]),
                     ('external-model-forensics', [(3,7),(31,43)])]:
    path = BASE.parent / 'notes' / f'{name}.md'
    body = path.read_text()
    lines = body.splitlines(keepends=True)
    chunks = [{'upstream_lines': [start,end], 'exact_text': ''.join(lines[start-1:end]).strip()}
              for start,end in ranges]
    relative = f'evidence/local-{name}-excerpts.txt'
    pack = '# LOCAL FORENSIC ANALYSIS; private working excerpts\n\n' + '\n\n'.join(x['exact_text'] for x in chunks) + '\n'
    save_new_or_identical(SUPPORT / relative, pack)
    analyses.append({'name': name, 'classification': 'LOCAL FORENSIC ANALYSIS, not independent incident replication',
                     'upstream_path': str(path), 'upstream_body_sha256': digest(body),
                     'evidence_path': relative, 'evidence_sha256': digest(pack), 'passages': chunks})

result = {'chapter_namespace': 'synthesis-15', 'research_cutoff': '2026-10-01',
          'evidence_scope': 'Selected preserved published passages only. Private evidence; publication unauthorized.',
          'upstream_namespaces': {k: str(v / '_support/citation-ledger.json') for k,v in ROOTS.items()},
          'sources': records, 'local_analyses': analyses,
          'stage4_handoff': 'PROTOCOL.md read as contract only. No findings file existed at inspection. No reservoir finding incorporated.'}
save_new_or_identical(SUPPORT / 'source-evidence-map.json', json.dumps(result, indent=2, ensure_ascii=False) + '\n')
print(f'Preserved {len(records)} published-source records and {len(analyses)} local analyses.')
