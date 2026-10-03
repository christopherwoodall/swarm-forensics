"""Validate only the chapter and its scoped evidence artifacts."""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import subprocess
import sys

sys.dont_write_bytecode = True
SUPPORT = Path(__file__).resolve().parent
BASE = SUPPORT.parents[1]
CHAPTER = BASE / '15-autonomous-swarm-mechanisms-and-detection.md'
LEDGER = SUPPORT / 'citation-ledger.json'
SCRIPT = Path('/home/resonatingloop/.hermes/skills/research/grounded-citations/scripts/sources.py')
spec = importlib.util.spec_from_file_location('citation_tools', SCRIPT)
assert spec is not None and spec.loader is not None
cite = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cite)


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def plain(text):
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'\[\d+\]', '', text)
    return re.sub(r'[*_`#>|]', ' ', text)


def words(text):
    return re.findall(r'\b[\w]+(?:[’\'-][\w]+)*\b', plain(text))


text = CHAPTER.read_text()
prose = text.split('\n## Sources\n')[0]
records = json.loads((SUPPORT / 'source-evidence-map.json').read_text())
sources = cite.load_ledger(LEDGER)['sources']
source_index = {x['id']: x for x in sources}
errors = []
checks = {}

command = [sys.executable, str(SCRIPT), '--ledger', str(LEDGER), 'verify', str(CHAPTER), '--strict', '--evidence']
run = subprocess.run(command, capture_output=True, text=True, check=False)
checks['grounded_citations'] = {'command': command, 'exit_code': run.returncode,
                               'stdout': run.stdout, 'stderr': run.stderr}
if run.returncode:
    errors.append('Grounded-citations verification failed.')

count = len(words(prose))
checks['word_count'] = {'actual': count, 'range': [3000,4500],
                        'method': 'Markdown labels retained; link targets, citations, markup, and Sources excluded. Headings and table included.'}
if not 3000 <= count <= 4500:
    errors.append('Word count outside accepted range.')

sentences = []
for number, line in enumerate(prose.splitlines(), 1):
    if not line.strip() or line.startswith('#') or line.startswith('`action'):
        continue
    cells = line.split('|') if line.startswith('|') else [line]
    for cell in cells:
        for sentence in re.split(r'(?<=[.!?])\s+', plain(cell)):
            n = len(words(sentence))
            if n:
                sentences.append({'line': number, 'words': n, 'text': sentence.strip()})
long = [x for x in sentences if x['words'] >= 20]
checks['sentence_lengths'] = {'checked_prose_units': len(sentences),
                              'maximum_words': max(x['words'] for x in sentences),
                              'units_at_or_above_20': long,
                              'method': 'One source sentence per line; punctuation splitting; table cells checked separately.'}
if long:
    errors.append('A prose sentence is not under 20 words.')

links = []
for label, target in re.findall(r'\[([^\]]+)\]\(([^)]+)\)', text):
    if re.match(r'^[a-z]+:', target) or target.startswith('#'):
        continue
    path = (CHAPTER.parent / target.split('#')[0]).resolve()
    links.append({'label': label, 'target': target, 'exists': path.exists()})
checks['local_links'] = links
if any(not x['exists'] for x in links):
    errors.append('Broken local chapter link.')

passage_checks = []
for record in records['sources']:
    source = source_index[record['local_id']]
    body = Path(record['upstream_body_path']).read_text()
    pack = (SUPPORT / record['evidence_path']).read_text()
    valid = source['url'] == record['url'] and digest(body) == record['upstream_body_sha256']
    valid = valid and digest(pack) == record['evidence_sha256']
    for mapping in record['upstream_mappings']:
        upstream = json.loads(Path(records['upstream_namespaces'][mapping['namespace']]).read_text())['sources']
        item = next(x for x in upstream if x['id'] == mapping['id'])
        valid = valid and cite.normalize_url(item['url']) == source['url']
    if not valid:
        errors.append(f'Source mapping or digest mismatch: {record["local_id"]}')
    for passage in record['passages']:
        start,end = passage['upstream_lines']
        selected = ''.join(body.splitlines(keepends=True)[start-1:end]).strip()
        exact = selected == passage['exact_text'] and selected in pack
        quoted = any(q['text'] == selected for q in source.get('quotes', []))
        passage_checks.append({'id': passage['passage_id'], 'exact_upstream_and_pack_match': exact,
                               'ledger_quote_match': quoted})
        if not exact or not quoted:
            errors.append(f'Excerpt mismatch: {passage["passage_id"]}')
    if len(source.get('quotes', [])) != len(record['passages']):
        errors.append(f'Quote inventory mismatch: {record["local_id"]}')

local_checks = []
for record in records['local_analyses']:
    body = Path(record['upstream_path']).read_text()
    pack = (SUPPORT / record['evidence_path']).read_text()
    valid = digest(body) == record['upstream_body_sha256'] and digest(pack) == record['evidence_sha256']
    for passage in record['passages']:
        start,end = passage['upstream_lines']
        selected = ''.join(body.splitlines(keepends=True)[start-1:end]).strip()
        valid = valid and selected == passage['exact_text'] and selected in pack
    local_checks.append({'name': record['name'], 'exact_match': valid,
                         'passage_count': len(record['passages'])})
    if not valid:
        errors.append(f'Local analysis excerpt mismatch: {record["name"]}')

checks['source_evidence'] = {'source_records': len(sources), 'mapped_source_records': len(records['sources']),
                             'unique_urls': len({x['url'] for x in sources}),
                             'published_passage_checks': passage_checks,
                             'local_analysis_checks': local_checks,
                             'scope': 'Exact text and identity checks, not independent incident verification.'}
if len(sources) != len(records['sources']) or len({x['url'] for x in sources}) != len(sources):
    errors.append('Source totals or URL uniqueness disagree.')

required = ['Formation and coupling', 'Allocation, topology, and changing roles', 'Memory and transmission',
            'Governance and principal conflicts', 'Amplification, adaptation, and repair',
            'Observability and discriminating tests', 'Topics for further perusal at the hackathon']
checks['coverage'] = {heading: f'## {heading}' in prose for heading in required}
checks['coverage'].update({term: term in prose for term in ['Control organization', 'Information lineage',
                          'process persistence', 'role persistence', 'information persistence',
                          'ORIGINAL SYNTHESIS', 'Immediately inspectable material',
                          'Experiments requiring further authorization', 'proposed discriminating-question checklist']})
if not all(checks['coverage'].values()):
    errors.append('Required mechanism or boundary absent.')
checks['perusal_topics'] = re.findall(r'^\*\*([^*]+)\.\*\*$', prose.split('## Topics for further perusal at the hackathon')[1], re.M)
checks['placeholders'] = re.findall(r'\b(?:TODO|TBD|FIXME|PLACEHOLDER)\b|\[unverified\]|\[SKILL_PRUNED\]', text, re.I)
if checks['placeholders']:
    errors.append('Unresolved placeholder found.')
checks['normative_keywords'] = re.findall(r'\b(?:MUST|SHOULD|MUST NOT|SHOULD NOT)\b', prose)

numeric = [
    ('30 agents over 20 minutes', 'S15-07-P01', 'Participants and duration in specialization experiment'),
    ('All sixteen compiler agents', 'S15-10-P03', 'Operator-disclosed parallel team, not sessions'),
    ('four discussants', 'S15-06-P04', 'Autonomous hidden-profile participants'),
    ('four scripted information sources', 'S15-06-P04', 'Scripted scouts, not autonomous peers'),
    ('266 vulnerabilities using 27 million tokens', 'S15-06-P01', 'Coordinated search condition'),
    ('21 using 6.5 million tokens', 'S15-06-P01', 'Independent restricted search condition'),
    ('Only 12 findings overlapped', 'S15-06-P01', 'Overlapping findings, not independent incidents'),
    ('2.4 million requests and only 117 accepted jobs', 'S15-06-P03', 'One finite-queue run; units differ'),
    ('510 reconstructed cohorts', 'S15-05-P02', 'Cohorts with trace outcomes, not authenticated agents'),
    ('37 normalized encoded mechanism implementations', 'local-organizational-forensics', 'LOCAL FORENSIC ANALYSIS counting unit'),
    ('20 encoded inference-request operations', 'local-external-model-forensics', 'Encoded operations without captured model returns'),
]
checks['declared_units_review'] = [{'literal': literal, 'passage': passage, 'unit_boundary': boundary,
                                   'literal_present': literal in prose} for literal,passage,boundary in numeric]
if not all(x['literal_present'] for x in checks['declared_units_review']):
    errors.append('Declared numeric claim inventory no longer matches draft.')
checks['entailment_review'] = {'path': 'entailment-review.md', 'present': (SUPPORT / 'entailment-review.md').exists(),
                              'status': 'Separate claim-family review; structural verification does not prove semantic entailment.'}

result = {'artifact': str(CHAPTER), 'chapter_sha256': digest(text), 'status': 'pass' if not errors else 'fail',
          'checks': checks, 'errors': errors,
          'deferred': ['Repository make test and make lint invoke setup; deferred to parent.',
                       'Final integration and any late reservoir handoff remain parent-owned.',
                       'Source 5 metadata/body version drift remains explicitly qualified.'],
          'changed_files': [str(CHAPTER)] + sorted(str(p) for p in SUPPORT.rglob('*') if p.is_file()
                                                  and '__pycache__' not in p.parts)}
if str(SUPPORT / 'verification.json') not in result['changed_files']:
    result['changed_files'].append(str(SUPPORT / 'verification.json'))
(SUPPORT / 'verification.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({'status': result['status'], 'word_count': count,
                  'max_sentence_words': checks['sentence_lengths']['maximum_words'],
                  'local_links': len(links), 'published_sources': len(sources),
                  'published_exact_passages': len(passage_checks),
                  'local_analysis_passages': sum(x['passage_count'] for x in local_checks),
                  'perusal_topics': len(checks['perusal_topics']), 'errors': errors,
                  'citation_output': run.stdout}, indent=2))
sys.exit(bool(errors))
