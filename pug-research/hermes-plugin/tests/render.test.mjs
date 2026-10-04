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

const HUNT = { id: 'h1', state: 'running', cycle: 2, detail: 'searching', origin: 'desktop', created_utc: NOW }
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
  unresolved: ['Nobody'], outgoing: [{ id: 1, kind: 'member_of', other: 'e2', type: 'swarm', name: 'Beta' }],
  backlinks: [{ id: 2, kind: 'mentions', other: 'e2', type: 'swarm', name: 'Beta' }],
  indicators: [{ kind: 'url', value: 'https://example.test/x' }],
  evidence: [{ id: 7, claim_level: 'L2', url: 'https://example.test/p', observed_utc: NOW, title: 'A page', excerpt: '' }]
}

function fixture(path, status) {
  const route = String(path).split('?')[0]
  const table = {
    '/status': status,
    '/overview': { settings: SETTINGS.values, capabilities: { model: true, web_search: true, web_extract: true } },
    '/hunts': { hunts: [HUNT, { ...HUNT, id: 'h0', state: 'paused' }] },
    '/events': { events: [{ id: 1, ts: NOW, kind: 'state', level: 'info', message: 'started' },
      { id: 2, ts: NOW, kind: 'finding', level: 'alert', message: 'alert' }] },
    '/evidence': { evidence: [EVIDENCE] },
    '/iocs': { iocs: [IOC], counts: { proposed: 1, active: 0, inactive: 0, rejected: 0 } },
    '/iocs/1': { log: [{ ts: NOW, from_status: null, to_status: 'proposed', actor: 'model', reason: 'seen' }], evidence: [EVIDENCE] },
    '/entities': { entities: [ENTITY, { ...ENTITY, id: 'e2', name: 'Beta', type: 'swarm' }] },
    '/entities/e1': ENTITY_DETAIL,
    '/graph': {
      nodes: [{ ...ENTITY, degree: 1 }, { id: 'e2', name: 'Beta', type: 'swarm', degree: 1 },
        { id: 'e3', name: 'Case', type: 'case', degree: 0 }, { id: 'e4', name: 'Trace', type: 'trace', degree: 0 },
        { id: 'e5', name: 'Group', type: 'collection', degree: 0 }],
      edges: [{ id: 1, src: 'e1', dst: 'e2', kind: 'member_of' }, { id: 2, src: 'e2', dst: 'e1', kind: 'mentions' }]
    },
    '/settings': SETTINGS,
    '/schedules': { schedules: [{ id: 's1', name: 'daily', kind: 'interval', spec: '6h', max_cycles: 5, enabled: 1, next_run_utc: NOW },
      { id: 's2', name: 'off', kind: 'cron', spec: '0 * * * *', max_cycles: 1, enabled: 0 }] }
  }
  if (!(route in table)) throw new Error(`No fixture for ${path}. Add one to render.test.mjs.`)
  return table[route]
}

// Load the plugin the way Hermes does, then collect what it registers.
function load() {
  const registered = new Map()
  const ctx = {
    rest: path => { globalThis.__sf.lastPath = path; return Promise.resolve({}) },
    setInterval() {},
    onEvent() {},
    storage: { get: () => null, set() {} },
    registerMany: items => items.forEach(item => registered.set(item.id, item))
  }
  globalThis.__sf = { lastPath: null, mode: 'data', stateRules: [], status: STATUS_RUNNING, fixture: null }
  plugin.register(ctx)
  return registered
}

// React reports bad usage (spread keys, children on a textarea) as console
// errors. Treat any of them as a failure.
function render({ tab = 'hunt', mode = 'data', status = STATUS_RUNNING, rules = [] } = {}) {
  const registered = load()
  Object.assign(globalThis.__sf, {
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

test('the plugin registers a page, nav entry, status chip, palette and keybind', () => {
  const registered = load()
  for (const id of ['page', 'nav', 'status', 'open', 'start', 'stop', 'open-key']) {
    assert.ok(registered.has(id), `missing registration: ${id}`)
  }
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
  ['iocs', 'zz=oaitest'], ['settings', 'Save changes']
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

test('the Knowledge tab renders a selected entity, its note links, and edit mode', () => {
  const selected = render({ tab: 'knowledge', rules: [[null, 'e1']] })
  assert.match(selected, /Works with/)
  assert.match(selected, /Unresolved links: Nobody/)
  assert.match(selected, /Backlinks/)
  const editing = render({ tab: 'knowledge', rules: [[null, 'e1'], [false, true]] })
  assert.match(editing, /<textarea/)
})

test('the Settings tab renders every field kind, including schedules', () => {
  const html = render({ tab: 'settings' })
  assert.match(html, /type="checkbox"/)
  assert.match(html, /type="number"/)
  assert.match(html, /<select/)
  assert.match(html, />Disarm</)
  assert.match(html, />Arm</)
})

test('the status chip renders in every state', () => {
  const registered = load()
  for (const [mode, status] of [['data', STATUS_RUNNING], ['data', STATUS_EMPTY], ['error', STATUS_RUNNING]]) {
    Object.assign(globalThis.__sf, { mode, fixture: path => fixture(path, status) })
    assert.match(renderToStaticMarkup(registered.get('status').render()), /sf: /)
  }
})
