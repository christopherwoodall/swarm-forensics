// Render tests for desktop/plugin.js. Run with `make test` (needs `make js-deps`).
//
// The page is rendered on the server with a real React and canned data.
// React throws on invalid element trees, such as children on an <input>
// (error #137), so a bad tree fails here and not in the desktop app.

import assert from 'node:assert/strict'
import { createRequire, register } from 'node:module'
import { test } from 'node:test'
import { pathToFileURL } from 'node:url'

const deps = process.env.SF_JS_DEPS
assert.ok(deps, 'SF_JS_DEPS is not set. Run `make test` or `make js-deps`.')
register('./js/hooks.mjs', import.meta.url)

const { renderToStaticMarkup } = createRequire(`${deps}/`)('react-dom/server')
const PLUGIN = new URL('../plugins/swarm-forensics/desktop/plugin.js', import.meta.url)
const plugin = (await import(pathToFileURL(PLUGIN.pathname).href)).default

const NOW = new Date().toISOString()

const SETTINGS = {
  values: {
    'hunt.default_goal': 'Find traces', 'iocs.promotion': 'manual', 'safety.private_mode': true,
    'schedule.enabled': false, 'hunt.sources': ['web'], 'safety.exclusion_terms': ['x'],
    'hunt.max_cycles': 0, 'hunt.request_delay_seconds': 2.0, 'hunt.use_model': true
  },
  schema: {
    fields: {
      'hunt.default_goal': { group: 'Hunt', label: 'Default hunt goal', kind: 'text', help: 'Goal text' },
      'hunt.sources': { group: 'Hunt', label: 'Sources', kind: 'multi', choices: ['web', 'cdx'] },
      'hunt.use_model': { group: 'Hunt', label: 'Use the model', kind: 'bool' },
      'hunt.max_cycles': { group: 'Hunt', label: 'Cycle limit', kind: 'int', min: 0, max: 100 },
      'hunt.request_delay_seconds': { group: 'Hunt', label: 'Delay', kind: 'float', min: 0, max: 60 },
      'iocs.promotion': { group: 'IOCs', label: 'Promotion', kind: 'choice', choices: ['manual', 'automatic'] },
      'safety.exclusion_terms': { group: 'Safety', label: 'Excluded', kind: 'list' },
      'safety.private_mode': { group: 'Safety', label: 'Private mode', kind: 'bool' },
      'schedule.enabled': { group: 'Schedule', label: 'Allow scheduled hunts', kind: 'bool' }
    }
  }
}

const HUNT = { id: 'h1', state: 'running', cycle: 2, detail: 'searching', origin: 'desktop', created_utc: NOW, depth: 0, parent_hunt_id: null, session_id: 'ses-1' }
const STATUS_RUNNING = {
  hunt: HUNT, running: true, desktop_alive: true, paused_all: false,
  totals: { evidence: 3, evidence_tainted: 1, entities: 2, links: 1, open_leads: 2 },
  iocs: { active: 1, proposed: 1, inactive: 0, rejected: 0 }, queries: { ok: 2, throttled: 1 }
}
const STATUS_IDLE = { ...STATUS_RUNNING, hunt: { ...HUNT, state: 'paused' }, running: false }
const STATUS_EMPTY = { ...STATUS_RUNNING, hunt: null, running: false, desktop_alive: false, paused_all: true }

const EVIDENCE = {
  id: 7, claim_level: 'L3', tainted: 1, url: 'https://example.test/p', title: 'A page',
  excerpt: 'excerpt text', source: 'web', observed_utc: NOW
}
const IOC = {
  id: 1, term: 'zz=oaitest', category: 'nonce_grammar', origin: 'model', status: 'proposed',
  evidence_count: 2, confidence: 0.6, provenance: 'hunt h1'
}
const ENTITY = { id: 'e1', name: 'Alpha', type: 'agent', degree: 1, evidence_count: 1 }
const ENTITY_DETAIL = {
  ...ENTITY, origin: 'model', updated_utc: NOW, summary: 'An agent', notes: 'Works with [[Beta]] and [[Nobody]].',
  tags: ['recon', 'stealth'],
  unresolved: ['Nobody'], outgoing: [{ id: 1, kind: 'part_of', other: 'e2', type: 'swarm', name: 'Beta' }],
  backlinks: [{ id: 2, kind: 'mentions', other: 'e2', type: 'swarm', name: 'Beta' }],
  parents: { swarm: [{ id: 1, kind: 'part_of', other: 'e2', type: 'swarm', name: 'Beta' }] },
  children: { artifact: [{ id: 3, kind: 'part_of', other: 'e4', type: 'artifact', name: 'Artifact 1' }] },
  indicators: [{ kind: 'url', value: 'https://example.test/x' }],
  evidence: [{ id: 7, claim_level: 'L2', url: 'https://example.test/p', observed_utc: NOW, title: 'A page', excerpt: '' }]
}

function fixture(path, status) {
  const route = String(path).split('?')[0]
  const table = {
    '/status': status,
    '/overview': { settings: SETTINGS.values, capabilities: { model: true, web_search: true, web_extract: true } },
    '/hunts': { hunts: [HUNT, { ...HUNT, id: 'h0', state: 'paused' }] },
    '/hunts/h1': { ...HUNT, stats: { queries: 2 }, detail: 'running' },
    '/hunts/h1/children': { children: [{ id: 'h2', state: 'running', depth: 1, parent_hunt_id: 'h1', goal: 'child subhunt', cycle: 1 }] },
    '/events': { events: [{ id: 1, ts: NOW, kind: 'state', level: 'info', message: 'started' },
      { id: 2, ts: NOW, kind: 'finding', level: 'alert', message: 'alert' }] },
    '/evidence': { evidence: [EVIDENCE] },
    '/leads': { leads: [{ id: 1, kind: 'query', value: 'find traces', priority: 0.9, origin: 'human', created_utc: NOW }] },
    '/morphologies': { morphologies: [{
      id: 'm1', candidate_id: 'morphology-1', candidate_label: 'Shared-state handoff',
      candidate_status: 'possible_new_morphology', evidence_strength: 'e2',
      review_status: 'new', tainted: 0, created_utc: NOW
    }] },
    '/morphologies/m1': {
      id: 'm1', candidate_id: 'morphology-1', candidate_status: 'possible_new_morphology',
      evidence_strength: 'e2', review_status: 'new', review_reason: '', review_history: [], tainted: 0,
      card: { candidate_label: 'Shared-state handoff', alternative_explanations: ['A central controller may explain it.'] }
    },
    '/sources': { sources: [{ id: 1, name: 'Wayback CDX', kind: 'cdx', endpoint: 'https://web.archive.org/cdx/search/cdx', config: {}, enabled: 1, probe_candidates: 1, note: '' }] },
    '/grammar': { grammar: [{ id: 1, kind: 'pattern', value: 'https://example.test/{slot}', param: '', enabled: 1, note: '' }] },
    '/urls': {
      urls: [{
        url: 'https://example.test/item', host: 'example.test', source: 'web',
        status: 'discovered', reason: '', discovered_utc: NOW, updated_utc: NOW
      }],
      counts: { discovered: 1, examined: 0, benign: 0, suspicious: 0 }
    },
    '/prompts': {
      prompts: [{
        id: 'plan_system', name: 'Plan System', description: 'System prompt',
        template: 'You are an agent.', default_template: 'You are an agent.',
        variables: ['goal'], updated_utc: NOW
      }]
    },
    '/iocs': { iocs: [IOC], counts: { proposed: 1, active: 0, inactive: 0, rejected: 0 } },
    '/iocs/1': { log: [{ ts: NOW, from_status: null, to_status: 'proposed', actor: 'model', reason: 'seen' }], evidence: [EVIDENCE] },
    '/entities': { entities: [ENTITY, { ...ENTITY, id: 'e2', name: 'Beta', type: 'swarm' }] },
    '/entities/e1': ENTITY_DETAIL,
    '/graph': {
      nodes: [{ ...ENTITY, degree: 1, rank: 1 }, { id: 'e2', name: 'Beta', type: 'swarm', degree: 1, rank: 2 },
        { id: 'e3', name: 'Case', type: 'campaign', degree: 0, rank: 3 }, { id: 'e4', name: 'Trace', type: 'artifact', degree: 0, rank: 0 },
        { id: 'e5', name: 'Group', type: 'collection', degree: 0, rank: null }],
      edges: [{ id: 1, src: 'e1', dst: 'e2', kind: 'part_of' }, { id: 2, src: 'e2', dst: 'e1', kind: 'mentions' }]
    },
    '/settings': SETTINGS,
    '/schedules': { schedules: [{ id: 's1', name: 'daily', kind: 'interval', spec: '6h', max_cycles: 5, enabled: 1, next_run_utc: NOW },
      { id: 's2', name: 'off', kind: 'cron', spec: '0 * * * *', max_cycles: 1, enabled: 0 }] },
    '/mirrors': { mirrors: [{ id: 1, url: 'https://example.test/item', sha256: 'abc12345', byte_count: 1024, tainted: 0 }], total: 1 },
    '/sessions/ses-1/overview': { session_id: 'ses-1', hunt: HUNT, events: [{ id: 1, ts: NOW, kind: 'tool_call', message: 'search' }], corpus: [] },
    '/sessions/durable-1/overview': { session_id: 'durable-1', hunt: HUNT, events: [], corpus: [] },
    '/sessions/ses-free/overview': { session_id: 'ses-free', hunt: null, events: [], corpus: [], narration_blocked: true }
  }
  if (!(route in table)) throw new Error(`No fixture for ${path}. Add one to render.test.mjs.`)
  return table[route]
}

// Load the plugin the way Hermes does, then collect what it registers.
function load() {
  const registered = new Map()
  const ctx = {
    rest: (path, options) => {
      globalThis.__sf.lastPath = path
      if (globalThis.__sf.paths) globalThis.__sf.paths.push(path)
      globalThis.__sf.restCalls?.push({ path, options })
      return Promise.resolve(globalThis.__sf.restResults?.[path] || {})
    },
    setInterval() {},
    onEvent() {},
    storage: { get: () => null, set() {} },
    registerMany: items => items.forEach(item => registered.set(item.id, item))
  }
  globalThis.__sf = { lastPath: null, paths: [], mode: 'data', stateRules: [], status: STATUS_RUNNING, fixture: null }
  plugin.register(ctx)
  return registered
}

// React reports bad usage (spread keys, children on a textarea) as console
// errors. Treat any of them as a failure.
function render({ tab = 'hunt', mode = 'data', status = STATUS_RUNNING, rules = [] } = {}) {
  const registered = load()
  Object.assign(globalThis.__sf, {
    paths: [],
    mode, fixture: path => fixture(path, status),
    stateRules: [['hunt', tab], ...rules]
  })
  const warnings = []
  const original = console.error
  console.error = (...args) => warnings.push(args.join(' '))
  try {
    const html = renderToStaticMarkup(registered.get('page').render())
    assert.deepEqual(warnings, [], 'React reported problems while rendering')
    return html
  } finally {
    console.error = original
  }
}

test('the plugin registers a page, nav entry, status chip, palette, keybind, composer strip, and companion pane', () => {
  const registered = load()
  for (const id of ['page', 'nav', 'status', 'open', 'start', 'stop', 'export', 'open-key', 'composer-strip', 'swarm-forensics.companion']) {
    assert.ok(registered.has(id), `missing registration: ${id}`)
  }
  const pane = registered.get('swarm-forensics.companion')
  assert.equal(pane.title, 'Swarm Forensics', 'pane tab label must be a top-level title')
  assert.equal(pane.data.placement, 'right')
})

test('the composer strip and companion pane render against the focused session', () => {
  const registered = load()
  Object.assign(globalThis.__sf, {
    paths: [],
    mode: 'data',
    fixture: path => fixture(path, STATUS_RUNNING),
    stateRules: [],
    sessionId: 'ses-1',
    storedSessionId: 'ses-1'
  })
  // The desktop Slot mounts contributions with no props, so renders take no
  // argument and the session id comes from host.state (stubbed above).
  const stripHtml = renderToStaticMarkup(registered.get('composer-strip').render())
  assert.match(stripHtml, /Swarm Forensics/)
  const paneHtml = renderToStaticMarkup(registered.get('swarm-forensics.companion').render())
  assert.match(paneHtml, /Hunt Companion/)
  assert.ok(globalThis.__sf.paths.includes('/sessions/ses-1/overview'),
    'companion pane must query the focused session overview')
})

test('the strip and pane look up the durable session key first', () => {
  const registered = load()
  Object.assign(globalThis.__sf, {
    paths: [], mode: 'data',
    fixture: path => fixture(path, STATUS_RUNNING),
    stateRules: [],
    sessionId: 'runtime-1', storedSessionId: 'durable-1'
  })
  renderToStaticMarkup(registered.get('composer-strip').render())
  renderToStaticMarkup(registered.get('swarm-forensics.companion').render())
  assert.ok(globalThis.__sf.paths.includes('/sessions/durable-1/overview'),
    'session lookup must prefer the durable key')
  assert.ok(!globalThis.__sf.paths.includes('/sessions/runtime-1/overview'),
    'the runtime id must not be queried when a durable key exists')
})

test('the strip and pane surface multi-hunt state and blocked chat updates', () => {
  const status = {
    ...STATUS_RUNNING,
    active_hunts: [HUNT, { ...HUNT, id: 'h9' }],
    narration_blocked: true
  }
  const registered = load()
  Object.assign(globalThis.__sf, {
    paths: [], mode: 'data',
    fixture: path => fixture(path, status),
    stateRules: [],
    sessionId: 'ses-free', storedSessionId: ''
  })
  const stripHtml = renderToStaticMarkup(registered.get('composer-strip').render())
  assert.match(stripHtml, /\+1/, 'strip must count the other active hunts')
  assert.match(stripHtml, /chat updates off/)
  const paneHtml = renderToStaticMarkup(registered.get('swarm-forensics.companion').render())
  assert.match(paneHtml, /2 hunts are running/)
  assert.match(paneHtml, /Chat updates are off/)
})

test('the Hunt page renders with an input and keeps its button labels', () => {
  const html = render()
  assert.match(html, /<input[^>]*placeholder="A search query for the next cycle"[^>]*\/?>/)
  assert.match(html, />Add</)
  assert.match(html, />Pause</)
  assert.match(html, />Stop</)
})

test('the Hunt page renders when idle, paused, and empty', () => {
  assert.match(render({ status: STATUS_IDLE }), />Start hunt</)
  assert.match(render({ status: STATUS_IDLE }), />Resume last hunt</)
  assert.match(render({ status: STATUS_EMPTY }), /No hunts yet/)
})

for (const [tab, marker] of [
  ['hunt', 'Add a lead'], ['knowledge', 'Pick an entity'], ['evidence', 'excerpt text'],
  ['iocs', 'zz=oaitest'], ['urls', 'https://example.test/item'], ['prompts', 'Plan System'],
  ['sources', 'Index sources'], ['settings', 'Save changes']
]) {
  test(`the ${tab} tab renders with data`, () => {
    // Private mode masks IOC terms until clicked, so reveal them in that tab.
    const html = render({ tab, rules: tab === 'iocs' ? [[false, true]] : [] })
    assert.ok(html.includes(marker), `expected "${marker}" in the ${tab} tab`)
  })

  test(`the ${tab} tab renders while loading and when the backend is offline`, () => {
    assert.doesNotThrow(() => render({ tab, mode: 'loading' }))
    assert.doesNotThrow(() => render({ tab, mode: 'error' }))
  })
}

test('the Sources tab renders index sources, URL grammar, and wordlist import', () => {
  const html = render({ tab: 'sources' })
  assert.match(html, /Index sources/)
  assert.match(html, /Wayback CDX/)
  assert.match(html, /URL grammar/)
  assert.match(html, />Regenerate candidates</)
  assert.match(html, /Wordlist import/)
  assert.match(html, />Import</)
})

test('HuntDetail renders with events, evidence, stats, sub-hunts, and close button', () => {
  const html = render({ tab: 'hunt', rules: [[null, 'h1']] })
  assert.match(html, /Hunt h1/)
  assert.match(html, />Close</)
  assert.match(html, /depth 0/)
  assert.match(html, />\+ Sub-hunt</)
  assert.match(html, />Attach Command</)
  assert.match(html, /Child Sub-hunts \(1\)/)
  assert.match(html, /Events \(/)
  assert.match(html, /Evidence \(/)
})

test('Hunt tab renders Leads card and Live discovered URLs card with + Artifact', () => {
  const html = render({ tab: 'hunt' })
  assert.match(html, /Leads \(/)
  assert.match(html, /find traces/)
  assert.match(html, />Dismiss</)
  assert.match(html, /Live discovered URLs \(/)
  assert.match(html, />\+ Artifact</)
})

test('the Knowledge tab renders a selected entity, its note links, hierarchy, and edit mode', () => {
  const selected = render({ tab: 'knowledge', rules: [[null, 'e1']] })
  assert.match(selected, /Works with/)
  assert.match(selected, /Unresolved links: Nobody/)
  assert.match(selected, /Backlinks/)
  assert.match(selected, /Hierarchy/)
  assert.match(selected, /Belongs to/)
  assert.match(selected, /Beta/)
  assert.match(selected, /Contains/)
  assert.match(selected, /Artifact 1/)
  const editing = render({ tab: 'knowledge', rules: [[null, 'e1'], [false, true]] })
  assert.match(editing, /<textarea/)
})

test('the IOCs tab does not request /iocs/1 while rows are closed', () => {
  render({ tab: 'iocs' })
  assert.ok(!globalThis.__sf.paths.includes('/iocs/1'), 'detail should not be requested while rows are closed')
})

test('the Settings tab renders every field kind, including schedules, export, and reset', () => {
  const html = render({ tab: 'settings' })
  assert.match(html, /type="checkbox"/)
  assert.match(html, /type="number"/)
  assert.match(html, /<select/)
  assert.match(html, />Disarm</)
  assert.match(html, />Arm</)
  assert.match(html, /Export data/)
  assert.match(html, />Export</)
  assert.match(html, /Danger zone: Reset all data/)
  assert.match(html, />Reset all data &amp; start from scratch</)
})

test('Morphologies tab imports and lists candidate cards as hypotheses', () => {
  const html = render({ tab: 'morphologies' })
  assert.ok(html.includes('Morphology candidates'))
  assert.ok(html.includes('Paste candidate card JSON'))
  assert.ok(html.includes('Shared-state handoff'))
  assert.ok(html.includes('possible_new_morphology'))
  assert.ok(html.includes('Candidates remain hypotheses until investigators verify them.'))
})

test('Morphologies tab can discover from raw data rather than requiring imported cards', () => {
  const html = render({ tab: 'morphologies' })
  assert.ok(html.includes('Discover from raw data'))
  assert.ok(html.includes('Dataset path'))
  assert.ok(html.includes('Allow redacted excerpts'))
  assert.ok(html.includes('Run morphology hunter'))
})

test('Morphology discovery shows fenced model prose as transient escaped text', () => {
  const report = {
    candidates: [], rounds: 4, scope: { record_count: 2 }, limitations: [],
    observations: [], probe_failures: [], rejected_hypotheses: [],
    transient_proposals: [{ candidate_id: 'hunter-fixture',
      interpretation_untrusted: '<<<UNTRUSTED transient discovery interpretation>>>\n' +
        'violet glacier <script>not executable</script>\n<<<END UNTRUSTED>>>' }]
  }
  const html = render({ tab: 'morphologies', rules: [[undefined, report]] })
  assert.ok(html.includes('Transient model interpretations (not saved)'))
  assert.ok(html.includes('violet glacier'))
  assert.ok(html.includes('&lt;script&gt;not executable&lt;/script&gt;'))
  assert.ok(!html.includes('<script>not executable</script>'))
})

test('Morphology discovery handler posts consent and waits for its bounded model budget', async () => {
  const registered = load()
  Object.assign(globalThis.__sf, {
    stateRules: [['hunt', 'morphologies'], ['', '/operator/authorized.jsonl', 4], [false, true, 0]],
    stateCounts: new Map(), elements: [], restCalls: [],
    fixture: path => fixture(path, STATUS_RUNNING),
    restResults: { '/morphologies/discover': { candidates: [], imported_records: [] } }
  })
  renderToStaticMarkup(registered.get('page').render())
  const button = globalThis.__sf.elements.find(element =>
    element.type === 'button' &&
    [element.props.children].flat(Infinity).includes('Run morphology hunter'))
  assert.ok(button)
  assert.equal(button.props.disabled, false)
  await button.props.onClick()
  const requests = globalThis.__sf.restCalls.filter(call => call.path === '/morphologies/discover')
  assert.equal(requests.length, 1)
  assert.deepEqual(requests[0].options.body, {
    path: '/operator/authorized.jsonl', allow_excerpts: true, max_records: 10000, max_rounds: 4
  })
  assert.ok(requests[0].options.timeoutMs >= 4 * 120 * 1000)
})

test('Morphologies tab renders while loading and when the backend is offline', () => {
  assert.doesNotThrow(() => render({ tab: 'morphologies', mode: 'loading' }))
  assert.doesNotThrow(() => render({ tab: 'morphologies', mode: 'error' }))
})

test('Morphology details preserve alternatives and offer an investigator session command', () => {
  const html = render({ tab: 'morphologies', rules: [[null, 'm1']] })
  assert.ok(html.includes('A central controller may explain it.'))
  assert.ok(html.includes('/swarm-forensics session Investigate morphology record m1'))
  assert.ok(html.includes('sf_get_morphology_candidates'))
  assert.ok(html.includes('Mark investigating'))
  assert.ok(html.includes('Mark review complete'))
  assert.ok(html.includes('Dismiss candidate'))
})

test('the status chip renders in every state', () => {
  const registered = load()
  for (const [mode, status] of [['data', STATUS_RUNNING], ['data', STATUS_EMPTY], ['error', STATUS_RUNNING]]) {
    Object.assign(globalThis.__sf, { mode, fixture: path => fixture(path, status) })
    assert.match(renderToStaticMarkup(registered.get('status').render()), /sf: /)
  }
})

test('Hunt tab renders Interactive hunt session card with command', () => {
  const html = render({ tab: 'hunt' })
  assert.match(html, /Interactive hunt session &amp; attach/)
  assert.match(html, /\/swarm-forensics session \[goal\]/)
  assert.match(html, /\/swarm-forensics attach \[hunt_id\]/)
  assert.match(html, /sf_get_context/)
  assert.match(html, /sf_spawn_subhunt/)
  assert.match(html, /sf_attach_hunt/)
})

test('URLs tab renders URL table, triage buttons, and + Artifact button', () => {
  const html = render({ tab: 'urls' })
  assert.match(html, /Discovered &amp; candidate URLs/)
  assert.match(html, /https:\/\/example\.test\/item/)
  assert.match(html, />Mark Benign</)
  assert.match(html, />Mark Suspicious</)
  assert.match(html, />\+ Artifact</)
})

test('Prompts tab renders template editor and token chips', () => {
  const html = render({ tab: 'prompts' })
  assert.match(html, /Prompt templates &amp; system persona/)
  assert.match(html, /Plan System/)
  assert.match(html, /\{\{goal\}\}/)
  assert.match(html, />Export Prompts \(JSON\)</)
})

test('the Knowledge tab renders group creation button and tags', () => {
  const html = render({ tab: 'knowledge' })
  assert.match(html, />\+ Group</)
  const selected = render({ tab: 'knowledge', rules: [[null, 'e1']] })
  assert.match(selected, /#recon/)
  assert.match(selected, /#stealth/)
})


