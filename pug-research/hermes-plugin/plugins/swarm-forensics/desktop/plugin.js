// Swarm Forensics desktop plugin. One ESM file, loaded uncompiled by Hermes Desktop.
// Allowed imports: @hermes/plugin-sdk, react, react/jsx-runtime. No build step.
//
// The operator starts a hunt here. Hermes then researches on its own until the
// operator stops it. This file only draws state and sends operator decisions to
// the backend (dashboard/plugin_api.py). All rules live in the backend.

import {
  host,
  queryClient,
  useQuery,
  ROUTES_AREA,
  SIDEBAR_NAV_AREA,
  STATUSBAR_AREAS,
  PALETTE_AREA,
  KEYBINDS_AREA
} from '@hermes/plugin-sdk'
import { useEffect, useMemo, useRef, useState } from 'react'
import { jsx, jsxs } from 'react/jsx-runtime'

const ID = 'swarm-forensics'
const PATH = '/swarm-forensics'
const HEARTBEAT_MS = 20000
const ALERT_POLL_MS = 10000
const ENTITY_TYPES = ['agent', 'swarm', 'case', 'trace', 'collection']
const LINK_KINDS = ['member_of', 'part_of', 'trace_of', 'related', 'observed_with']

let rest = null // set in register(ctx)

// ---------------------------------------------------------------- helpers

const flat = kids => kids.flat(Infinity).filter(k => k !== null && k !== undefined && k !== false)

// Build an element. Two React rules apply here:
// - A void element (input, img) MUST NOT receive `children`, even `[]`.
//   So pass no `children` key when there are none (React error #137).
// - `key` MUST be the third argument. It MUST NOT sit inside the props object.
function h(type, props, ...kids) {
  const { key, ...p } = props || {}
  const children = flat(kids)
  if (children.length === 0) return jsx(type, p, key)
  if (children.length === 1) return jsx(type, { ...p, children: children[0] }, key)
  return jsxs(type, { ...p, children }, key)
}

const V = {
  text: 'var(--ui-text-secondary)',
  dim: 'var(--ui-text-tertiary)',
  faint: 'var(--ui-text-quaternary)',
  line: 'var(--ui-stroke-secondary)',
  accent: 'var(--ui-accent)'
}

const S = {
  page: { display: 'flex', flexDirection: 'column', height: '100%', minHeight: 0, fontSize: '0.8125rem', color: V.text },
  tabs: { display: 'flex', gap: 4, padding: '8px 12px 0', borderBottom: `1px solid ${V.line}` },
  body: { flex: 1, minHeight: 0, overflow: 'auto', padding: 12 },
  row: { display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' },
  col: { display: 'flex', flexDirection: 'column', gap: 8 },
  card: { border: `1px solid ${V.line}`, borderRadius: 8, padding: 10 },
  h2: { fontSize: '0.9rem', fontWeight: 600, margin: '4px 0' },
  dim: { color: V.dim },
  mono: { fontFamily: 'ui-monospace, monospace', fontSize: '0.75rem', wordBreak: 'break-all' },
  input: {
    background: 'transparent', color: 'inherit', border: `1px solid ${V.line}`,
    borderRadius: 6, padding: '4px 8px', font: 'inherit', minWidth: 0
  },
  btn: {
    background: 'transparent', color: 'inherit', border: `1px solid ${V.line}`,
    borderRadius: 6, padding: '3px 10px', font: 'inherit', cursor: 'pointer'
  },
  chip: { border: `1px solid ${V.line}`, borderRadius: 999, padding: '0 8px', fontSize: '0.7rem' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))', gap: 8 }
}

const ago = iso => {
  if (!iso) return ''
  const s = Math.max(0, (Date.now() - Date.parse(iso)) / 1000)
  if (s < 90) return `${Math.round(s)}s ago`
  if (s < 5400) return `${Math.round(s / 60)}m ago`
  if (s < 129600) return `${Math.round(s / 3600)}h ago`
  return `${Math.round(s / 86400)}d ago`
}

const hostOf = url => {
  try { return new URL(url).hostname } catch { return url }
}

const api = (path, opts) => rest(path, opts)

const refresh = () => queryClient.invalidateQueries({ queryKey: [ID] })

async function act(path, body, method = 'POST', okMessage) {
  try {
    const out = await api(path, { method, body })
    refresh()
    if (okMessage) host.notify({ kind: 'info', message: okMessage })
    return out
  } catch (err) {
    host.notifyError(err, 'Swarm Forensics request failed')
    return null
  }
}

function useApi(key, path, poll) {
  return useQuery({
    queryKey: [ID, ...key],
    queryFn: () => api(path),
    refetchInterval: poll || false,
    retry: 1
  })
}

// ---------------------------------------------------------------- small UI

function Btn({ onClick, children, disabled, title, kind }) {
  const style = { ...S.btn, opacity: disabled ? 0.45 : 1, cursor: disabled ? 'default' : 'pointer' }
  if (kind === 'primary') style.borderColor = V.accent
  if (kind === 'primary') style.color = V.accent
  return h('button', { type: 'button', style, title, disabled, onClick: disabled ? undefined : onClick }, children)
}

function Chip({ children, strong }) {
  return h('span', { style: { ...S.chip, color: strong ? V.accent : V.dim, borderColor: strong ? V.accent : V.line } }, children)
}

function Tabs({ tabs, value, onChange }) {
  return h('div', { style: S.tabs },
    tabs.map(([id, label]) => h('button', {
      key: id, type: 'button', onClick: () => onChange(id),
      style: {
        ...S.btn, border: 'none', borderRadius: 0, padding: '6px 10px',
        color: value === id ? V.accent : V.dim,
        borderBottom: `2px solid ${value === id ? V.accent : 'transparent'}`
      }
    }, label)))
}

function Empty({ children }) {
  return h('div', { style: { ...S.dim, padding: 16, textAlign: 'center' } }, children)
}

function Masked({ text, on }) {
  const [shown, setShown] = useState(false)
  if (!on || shown) return h('span', { style: S.mono, onClick: () => setShown(false) }, text)
  return h('span', { style: { ...S.mono, cursor: 'pointer', color: V.dim }, title: 'Click to reveal', onClick: () => setShown(true) },
    '\u2022'.repeat(Math.min(12, Math.max(4, text.length))))
}

function useSettings() {
  const q = useApi(['settings'], '/settings')
  return q.data ? q.data.values : null
}

function Error({ q }) {
  if (!q.isError) return null
  return h('div', { style: { ...S.card, color: V.accent } }, `Backend unreachable: ${String(q.error && q.error.message || q.error)}. Is the plugin in plugins.enabled and the gateway restarted?`)
}

// ---------------------------------------------------------------- hunt page

const STATE_HELP = {
  running: 'Hermes is researching.',
  waiting: 'Between cycles.',
  paused: 'Paused. A person must resume it.',
  blocked: 'Blocked. Fix the cause, then resume.',
  stopped: 'Stopped.'
}

function HuntPage() {
  const status = useApi(['status'], '/status', 3000)
  const overview = useApi(['overview'], '/overview', 30000)
  const hunts = useApi(['hunts'], '/hunts?limit=10', 8000)
  const hunt = status.data && status.data.hunt
  const events = useApi(['events', hunt ? hunt.id : 'none'], `/events?limit=80${hunt ? `&hunt_id=${hunt.id}` : ''}`, 3000)
  const settings = overview.data && overview.data.settings
  const caps = overview.data && overview.data.capabilities
  const [goal, setGoal] = useState('')
  const [lead, setLead] = useState('')
  const running = !!(status.data && status.data.running)
  const st = status.data
  const t = st ? st.totals : {}
  const i = st ? st.iocs : {}
  const qs = st ? st.queries : {}

  return h('div', { style: S.col },
    h(Error, { q: status }),
    caps && (!caps.model || !caps.web_search) && h('div', { style: { ...S.card, color: V.accent } },
      [!caps.model && 'Hermes model unavailable in the backend process. Hunts fall back to indicator matching.',
        !caps.web_search && 'Hermes web_search tool not found. Configure a web backend in Hermes.'].filter(Boolean).join(' ')),
    h('div', { style: S.card },
      h('div', { style: S.row },
        h('span', { style: S.h2 }, hunt ? `Hunt ${hunt.id}` : 'No hunts yet'),
        hunt && h(Chip, { strong: running }, hunt.state),
        hunt && h('span', { style: S.dim }, `cycle ${hunt.cycle}`),
        hunt && h('span', { style: S.dim }, hunt.detail || STATE_HELP[hunt.state] || ''),
        st && !st.desktop_alive && h(Chip, null, 'heartbeat lost'),
        st && st.paused_all && h(Chip, { strong: true }, 'all hunting paused')),
      !running && h('div', { style: { ...S.col, marginTop: 8 } },
        h('textarea', {
          style: { ...S.input, minHeight: 56, resize: 'vertical' }, value: goal,
          placeholder: (settings && settings['hunt.default_goal']) || 'Hunt goal. Empty uses the default goal.',
          onChange: e => setGoal(e.target.value)
        }),
        h('div', { style: S.row },
          h(Btn, { kind: 'primary', onClick: () => act('/hunts/start', { goal }, 'POST', 'Hunt started') }, 'Start hunt'),
          hunt && (hunt.state === 'paused' || hunt.state === 'blocked') &&
            h(Btn, { onClick: () => act('/hunts/resume', { hunt_id: hunt.id }, 'POST', 'Hunt resumed') }, 'Resume last hunt'),
          h('span', { style: S.dim }, 'A started hunt runs until you stop it. Closing the app pauses it.'))),
      running && h('div', { style: { ...S.row, marginTop: 8 } },
        h(Btn, { onClick: () => act('/hunts/pause', { hunt_id: hunt.id }) }, 'Pause'),
        h(Btn, { onClick: () => act('/hunts/stop', { hunt_id: hunt.id }, 'POST', 'Stop requested') }, 'Stop'))),
    h('div', { style: S.grid },
      [['Evidence', t.evidence], ['Tainted', t.evidence_tainted], ['Entities', t.entities], ['Links', t.links],
        ['IOCs active', i.active], ['IOCs proposed', i.proposed], ['Open leads', t.open_leads],
        ['Queries ok', qs.ok || 0], ['Throttled', qs.throttled || 0], ['Errors', qs.error || 0]]
        .map(([k, v]) => h('div', { key: k, style: S.card },
          h('div', { style: S.dim }, k), h('div', { style: { fontSize: '1.1rem' } }, v === undefined ? '-' : String(v))))),
    h('div', { style: S.card },
      h('div', { style: S.h2 }, 'Add a lead'),
      h('div', { style: S.row },
        h('input', { style: { ...S.input, flex: 1 }, value: lead, placeholder: 'A search query for the next cycle', onChange: e => setLead(e.target.value) }),
        h(Btn, {
          disabled: !lead.trim(),
          onClick: async () => { if (await act('/leads', { kind: 'query', value: lead.trim() })) setLead('') }
        }, 'Add'))),
    h('div', { style: S.card },
      h('div', { style: S.h2 }, 'Activity'),
      events.data && events.data.events.length
        ? h('div', { style: { ...S.col, gap: 2, maxHeight: 280, overflow: 'auto' } },
          events.data.events.slice().reverse().map(e => h('div', {
            key: e.id,
            style: { ...S.mono, color: e.level === 'alert' ? V.accent : (e.level === 'info' ? 'inherit' : V.dim), fontWeight: e.level === 'alert' ? 600 : 400 }
          }, `${ago(e.ts)}  [${e.kind}] ${e.message}`)))
        : h(Empty, null, 'No activity yet.')),
    h('div', { style: S.card },
      h('div', { style: S.h2 }, 'Recent hunts'),
      hunts.data && hunts.data.hunts.length
        ? hunts.data.hunts.map(x => h('div', { key: x.id, style: { ...S.row, padding: '2px 0' } },
          h('span', { style: S.mono }, x.id), h(Chip, null, x.state), h('span', { style: S.dim }, `${x.origin}, ${x.cycle} cycles, ${ago(x.created_utc)}`),
          (x.state === 'paused' || x.state === 'blocked') && !running &&
            h(Btn, { onClick: () => act('/hunts/resume', { hunt_id: x.id }, 'POST', 'Hunt resumed') }, 'Resume')))
        : h(Empty, null, 'None.')))
}

// ---------------------------------------------------------------- evidence

function EvidencePage() {
  const [q, setQ] = useState('')
  const [level, setLevel] = useState('')
  const [open, setOpen] = useState(null)
  const query = useApi(['evidence', q, level], `/evidence?limit=100${q ? `&q=${encodeURIComponent(q)}` : ''}${level ? `&min_level=${level}` : ''}`, 10000)
  const detail = useApi(['evidence-one', open], open ? `/evidence/${open}` : '/status')
  const rows = query.data ? query.data.evidence : []
  return h('div', { style: S.col },
    h('div', { style: S.row },
      h('input', { style: { ...S.input, flex: 1 }, value: q, placeholder: 'Search url, title, excerpt', onChange: e => setQ(e.target.value) }),
      h('select', { style: S.input, value: level, onChange: e => setLevel(e.target.value) },
        h('option', { value: '' }, 'Any claim level'),
        ['L1', 'L2', 'L3', 'L4', 'L5'].map(l => h('option', { key: l, value: l }, `${l} and up`)))),
    h(Error, { q: query }),
    rows.length === 0 && h(Empty, null, 'No evidence yet. Start a hunt.'),
    rows.map(r => h('div', { key: r.id, style: S.card },
      h('div', { style: { ...S.row, cursor: 'pointer' }, onClick: () => setOpen(open === r.id ? null : r.id) },
        h(Chip, { strong: r.claim_level >= 'L3' }, r.claim_level),
        r.tainted ? h(Chip, { strong: true }, 'tainted') : null,
        h('span', { style: S.mono }, hostOf(r.url)),
        h('span', { style: S.dim }, `${r.source} ${ago(r.observed_utc)}`)),
      h('div', { style: { marginTop: 4 } }, r.title || r.url),
      h('div', { style: { ...S.dim, marginTop: 2, whiteSpace: 'pre-wrap' } }, r.excerpt.slice(0, 280)),
      open === r.id && detail.data && detail.data.url && h('div', { style: { ...S.mono, marginTop: 6 } },
        h('div', null, detail.data.url),
        h('pre', { style: { whiteSpace: 'pre-wrap', margin: '6px 0 0' } }, JSON.stringify(detail.data.analysis, null, 2))))))
}

// ---------------------------------------------------------------- IOCs

function IocRow({ ioc, mask }) {
  const [open, setOpen] = useState(false)
  const [narrow, setNarrow] = useState('')
  const detail = useApi(['ioc', ioc.id], `/iocs/${ioc.id}`)
  const decide = (decision, extra) => act(`/iocs/${ioc.id}/decision`, { decision, ...extra })
  const actions = {
    proposed: [['accept', 'Accept'], ['reject', 'Reject']],
    active: [['deactivate', 'Deactivate']],
    inactive: [['reactivate', 'Reactivate']],
    rejected: [['reopen', 'Reopen']]
  }[ioc.status] || []
  return h('div', { style: S.card },
    h('div', { style: S.row },
      h('span', { style: { cursor: 'pointer' }, onClick: () => setOpen(!open) }, h(Masked, { text: ioc.term, on: mask })),
      h(Chip, null, ioc.category), h(Chip, null, ioc.origin),
      h('span', { style: S.dim }, `${ioc.evidence_count} evidence, conf ${ioc.confidence.toFixed(1)}`),
      h('span', { style: { flex: 1 } }),
      actions.map(([d, label]) => h(Btn, { key: d, onClick: () => decide(d, {}) }, label))),
    ioc.status === 'proposed' && h('div', { style: { ...S.row, marginTop: 6 } },
      h('input', { style: { ...S.input, flex: 1 }, value: narrow, placeholder: 'Narrow to a more specific term', onChange: e => setNarrow(e.target.value) }),
      h(Btn, { disabled: !narrow.trim(), onClick: () => decide('narrow', { narrower: narrow.trim() }) }, 'Narrow')),
    open && detail.data && detail.data.log && h('div', { style: { ...S.col, gap: 2, marginTop: 8 } },
      ioc.provenance && h('div', { style: S.dim }, `provenance: ${ioc.provenance}`),
      detail.data.log.map((l, n) => h('div', { key: n, style: { ...S.mono, color: V.dim } }, `${ago(l.ts)} ${l.from_status || 'new'} -> ${l.to_status} by ${l.actor}: ${l.reason}`)),
      detail.data.evidence.map(e => h('div', { key: e.id, style: S.mono }, `[${e.claim_level}${e.tainted ? ' tainted' : ''}] ${e.url}`))))
}

function IocsPage() {
  const [status, setStatus] = useState('proposed')
  const [q, setQ] = useState('')
  const [term, setTerm] = useState('')
  const [activate, setActivate] = useState(false)
  const settings = useSettings()
  const query = useApi(['iocs', status, q], `/iocs?status=${status}&limit=300${q ? `&q=${encodeURIComponent(q)}` : ''}`, 8000)
  const counts = query.data ? query.data.counts : {}
  const mode = settings ? settings['iocs.promotion'] : 'manual'
  return h('div', { style: S.col },
    h('div', { style: { ...S.card, ...S.row } },
      h('span', null, 'Promotion mode:'), h(Chip, { strong: mode === 'automatic' }, mode),
      h('span', { style: S.dim }, mode === 'manual'
        ? 'Every term waits for your decision.'
        : 'Terms with enough untainted evidence promote on their own. The model never promotes.'),
      h('span', { style: { flex: 1 } }),
      h(Btn, { onClick: () => act('/settings', { updates: { 'iocs.promotion': mode === 'manual' ? 'automatic' : 'manual' } }, 'PUT') },
        `Switch to ${mode === 'manual' ? 'automatic' : 'manual'}`)),
    h('div', { style: S.row },
      ['proposed', 'active', 'inactive', 'rejected'].map(s => h(Btn, { key: s, kind: s === status ? 'primary' : undefined, onClick: () => setStatus(s) }, `${s} (${counts[s] || 0})`)),
      h('input', { style: { ...S.input, flex: 1 }, value: q, placeholder: 'Filter terms', onChange: e => setQ(e.target.value) })),
    h('div', { style: { ...S.card, ...S.row } },
      h('input', { style: { ...S.input, flex: 1 }, value: term, placeholder: 'Add a term by hand', onChange: e => setTerm(e.target.value) }),
      h('label', { style: S.row }, h('input', { type: 'checkbox', checked: activate, onChange: e => setActivate(e.target.checked) }), 'active now'),
      h(Btn, { disabled: !term.trim(), onClick: async () => { if (await act('/iocs', { term: term.trim(), activate })) setTerm('') } }, 'Add')),
    h(Error, { q: query }),
    query.data && query.data.iocs.length === 0 && h(Empty, null, `No ${status} terms.`),
    (query.data ? query.data.iocs : []).map(ioc => h(IocRow, { key: ioc.id, ioc, mask: settings ? settings['safety.private_mode'] : true })))
}

// ---------------------------------------------------------------- graph

function layout(nodes, edges, w, h0) {
  const pos = new Map()
  const n = nodes.length
  nodes.forEach((node, k) => {
    const a = (2 * Math.PI * k) / Math.max(1, n)
    pos.set(node.id, { x: w / 2 + Math.cos(a) * w * 0.3, y: h0 / 2 + Math.sin(a) * h0 * 0.3, vx: 0, vy: 0 })
  })
  const iters = n > 250 ? 120 : 260
  for (let it = 0; it < iters; it++) {
    const cool = 1 - it / iters
    for (let a = 0; a < n; a++) {
      const pa = pos.get(nodes[a].id)
      for (let b = a + 1; b < n; b++) {
        const pb = pos.get(nodes[b].id)
        let dx = pa.x - pb.x, dy = pa.y - pb.y
        const d2 = Math.max(60, dx * dx + dy * dy)
        const f = 2400 / d2
        const d = Math.sqrt(d2)
        dx = (dx / d) * f; dy = (dy / d) * f
        pa.vx += dx; pa.vy += dy; pb.vx -= dx; pb.vy -= dy
      }
    }
    edges.forEach(e => {
      const pa = pos.get(e.src), pb = pos.get(e.dst)
      if (!pa || !pb) return
      const dx = pb.x - pa.x, dy = pb.y - pa.y
      const d = Math.max(1, Math.sqrt(dx * dx + dy * dy))
      const f = (d - 90) * 0.02
      pa.vx += (dx / d) * f; pa.vy += (dy / d) * f; pb.vx -= (dx / d) * f; pb.vy -= (dy / d) * f
    })
    pos.forEach(p => {
      p.vx += (w / 2 - p.x) * 0.005; p.vy += (h0 / 2 - p.y) * 0.005
      p.x += Math.max(-12, Math.min(12, p.vx)) * cool; p.y += Math.max(-12, Math.min(12, p.vy)) * cool
      p.vx *= 0.6; p.vy *= 0.6
    })
  }
  return pos
}

const SHAPE_OPACITY = { agent: 1, swarm: 0.75, case: 0.55, trace: 0.3, collection: 0.45 }

function GraphView({ center, selected, onSelect, height }) {
  const q = useApi(['graph', center || 'all'], `/graph?depth=2${center ? `&center=${center}` : ''}`, 15000)
  const [view, setView] = useState({ x: 0, y: 0, k: 1 })
  const drag = useRef(null)
  const W = 800, H = 500
  const g = q.data
  const pos = useMemo(() => (g ? layout(g.nodes, g.edges, W, H) : new Map()), [g])
  if (!g) return h('div', { style: { height } }, h(Error, { q }))
  if (g.nodes.length === 0) return h(Empty, null, 'The graph is empty. Hunts add agents, swarms, and cases as they find them.')
  const vb = `${view.x} ${view.y} ${W / view.k} ${H / view.k}`
  const onWheel = e => {
    const k = Math.max(0.3, Math.min(5, view.k * (e.deltaY < 0 ? 1.15 : 0.87)))
    setView({ ...view, k })
  }
  return h('svg', {
    viewBox: vb, style: { width: '100%', height, border: `1px solid ${V.line}`, borderRadius: 8, cursor: 'grab', touchAction: 'none' },
    onWheel,
    onPointerDown: e => { drag.current = { x: e.clientX, y: e.clientY, vx: view.x, vy: view.y } },
    onPointerMove: e => {
      if (!drag.current) return
      const el = e.currentTarget.getBoundingClientRect()
      const sx = (W / view.k) / el.width, sy = (H / view.k) / el.height
      setView({ ...view, x: drag.current.vx - (e.clientX - drag.current.x) * sx, y: drag.current.vy - (e.clientY - drag.current.y) * sy })
    },
    onPointerUp: () => { drag.current = null },
    onPointerLeave: () => { drag.current = null }
  },
    g.edges.map(e => {
      const a = pos.get(e.src), b = pos.get(e.dst)
      if (!a || !b) return null
      return h('line', { key: e.id, x1: a.x, y1: a.y, x2: b.x, y2: b.y, stroke: 'currentColor', strokeOpacity: e.kind === 'mentions' ? 0.2 : 0.4, strokeDasharray: e.kind === 'mentions' ? '3 3' : undefined })
    }),
    g.nodes.map(n => {
      const p = pos.get(n.id)
      const r = 6 + Math.min(8, n.degree)
      const sel = n.id === selected || n.id === center
      const common = { fill: V.accent, fillOpacity: SHAPE_OPACITY[n.type] || 0.5, stroke: sel ? 'currentColor' : V.accent, strokeWidth: sel ? 2 : 1 }
      const shape = n.type === 'swarm' ? h('rect', { x: p.x - r, y: p.y - r, width: 2 * r, height: 2 * r, ...common })
        : n.type === 'case' ? h('polygon', { points: `${p.x},${p.y - r - 2} ${p.x + r + 2},${p.y} ${p.x},${p.y + r + 2} ${p.x - r - 2},${p.y}`, ...common })
          : n.type === 'collection' ? h('polygon', { points: `${p.x},${p.y - r} ${p.x + r},${p.y + r} ${p.x - r},${p.y + r}`, ...common })
            : h('circle', { cx: p.x, cy: p.y, r: n.type === 'trace' ? Math.max(4, r - 2) : r, ...common })
      return h('g', { key: n.id, style: { cursor: 'pointer' }, onPointerDown: e => e.stopPropagation(), onClick: () => onSelect && onSelect(n.id) },
        h('title', null, `${n.type}: ${n.name}`), shape,
        h('text', { x: p.x + r + 3, y: p.y + 3, fontSize: 10, fill: 'currentColor', opacity: 0.8 }, n.name.slice(0, 28)))
    }))
}

// ---------------------------------------------------------------- knowledge (notes + graph)

function NoteText({ text, names, onOpen }) {
  const parts = text.split(/(\[\[[^\]\n]+\]\])/g)
  return h('div', { style: { whiteSpace: 'pre-wrap', lineHeight: 1.5 } },
    parts.map((part, n) => {
      const m = /^\[\[([^\]|#\n]+)(?:\|[^\]\n]*)?\]\]$/.exec(part)
      if (!m) return h('span', { key: n }, part)
      const target = names.get(m[1].trim().toLowerCase())
      return h('a', {
        key: n, href: '#', title: target ? 'Open' : 'No such entity',
        style: { color: target ? V.accent : V.dim, textDecoration: target ? 'underline' : 'dotted underline' },
        onClick: e => { e.preventDefault(); if (target) onOpen(target) }
      }, m[1])
    }))
}

function EntityPane({ id, names, onOpen, onGone }) {
  const q = useApi(['entity', id], `/entities/${id}`, 15000)
  const e = q.data
  const [edit, setEdit] = useState(false)
  const [notes, setNotes] = useState('')
  const [summary, setSummary] = useState('')
  const [linkTo, setLinkTo] = useState('')
  const [linkKind, setLinkKind] = useState('related')
  useEffect(() => { if (e) { setNotes(e.notes); setSummary(e.summary); setEdit(false) } }, [e && e.id, e && e.updated_utc])
  if (!e) return h(Error, { q })
  const others = Array.from(names.entries()).filter(([, v]) => v !== id)
  const edgeRow = (l, dir) => h('div', { key: `${dir}${l.id}`, style: S.row },
    h(Chip, null, l.kind), h('a', { href: '#', style: { color: V.accent }, onClick: ev => { ev.preventDefault(); onOpen(l.other) } }, `${l.type}: ${l.name}`),
    l.kind !== 'mentions' && h(Btn, { onClick: () => act(`/links/${l.id}`, undefined, 'DELETE') }, 'Unlink'))
  return h('div', { style: S.col },
    h('div', { style: S.row },
      h('span', { style: { fontSize: '1.05rem', fontWeight: 600 } }, e.name), h(Chip, null, e.type), h(Chip, null, e.origin),
      h('span', { style: S.dim }, `updated ${ago(e.updated_utc)}`), h('span', { style: { flex: 1 } }),
      h(Btn, { onClick: () => setEdit(!edit) }, edit ? 'Cancel' : 'Edit'),
      h(Btn, { onClick: async () => { if (window.confirm(`Delete ${e.name} and its links?`)) { await act(`/entities/${id}`, undefined, 'DELETE'); onGone() } } }, 'Delete')),
    edit
      ? h('div', { style: S.col },
        h('input', { style: S.input, value: summary, placeholder: 'One-line summary', onChange: ev => setSummary(ev.target.value) }),
        h('textarea', { style: { ...S.input, minHeight: 180, fontFamily: 'ui-monospace, monospace' }, value: notes, placeholder: 'Markdown notes. Link with [[Name]].', onChange: ev => setNotes(ev.target.value) }),
        h('div', null, h(Btn, { kind: 'primary', onClick: async () => { if (await act(`/entities/${id}`, { summary, notes }, 'PUT', 'Saved')) setEdit(false) } }, 'Save')))
      : h('div', { style: S.col },
        e.summary && h('div', { style: S.dim }, e.summary),
        e.notes ? h(NoteText, { text: e.notes, names, onOpen }) : h('div', { style: S.dim }, 'No notes yet.'),
        e.unresolved.length > 0 && h('div', { style: S.dim }, `Unresolved links: ${e.unresolved.join(', ')}`)),
    h('div', { style: S.card },
      h('div', { style: S.h2 }, `Links (${e.outgoing.length + e.backlinks.length})`),
      e.outgoing.map(l => edgeRow(l, 'o')),
      e.backlinks.length > 0 && h('div', { style: { ...S.dim, marginTop: 6 } }, 'Backlinks'),
      e.backlinks.map(l => edgeRow(l, 'b')),
      h('div', { style: { ...S.row, marginTop: 8 } },
        h('select', { style: S.input, value: linkKind, onChange: ev => setLinkKind(ev.target.value) }, LINK_KINDS.map(k => h('option', { key: k, value: k }, k))),
        h('select', { style: S.input, value: linkTo, onChange: ev => setLinkTo(ev.target.value) },
          h('option', { value: '' }, 'link to...'), others.map(([name, v]) => h('option', { key: v, value: v }, name))),
        h(Btn, { disabled: !linkTo, onClick: async () => { if (await act('/links', { src: id, dst: linkTo, kind: linkKind })) setLinkTo('') } }, 'Link'))),
    e.indicators.length > 0 && h('div', { style: S.card },
      h('div', { style: S.h2 }, `Indicators (${e.indicators.length})`),
      h('div', { style: { ...S.col, gap: 2, maxHeight: 180, overflow: 'auto' } },
        e.indicators.map((i, n) => h('div', { key: n, style: S.mono }, `${i.kind}  ${i.value}`)))),
    e.evidence.length > 0 && h('div', { style: S.card },
      h('div', { style: S.h2 }, `Evidence (${e.evidence.length})`),
      e.evidence.slice(0, 20).map(ev => h('div', { key: ev.id, style: { ...S.col, gap: 0, marginBottom: 6 } },
        h('div', { style: S.row }, h(Chip, null, ev.claim_level), h('span', { style: S.mono }, hostOf(ev.url)), h('span', { style: S.dim }, ago(ev.observed_utc))),
        h('div', { style: S.dim }, (ev.title || ev.excerpt || '').slice(0, 160))))))
}

function KnowledgePage() {
  const [type, setType] = useState('')
  const [q, setQ] = useState('')
  const [sel, setSel] = useState(null)
  const [nt, setNt] = useState('agent')
  const [nn, setNn] = useState('')
  const list = useApi(['entities', type, q], `/entities?limit=300${type ? `&type=${type}` : ''}${q ? `&q=${encodeURIComponent(q)}` : ''}`, 10000)
  const all = useApi(['entities-all'], '/entities?limit=1000', 20000)
  const names = useMemo(() => {
    const m = new Map()
    ;(all.data ? all.data.entities : []).forEach(e => m.set(e.name.toLowerCase(), e.id))
    return m
  }, [all.data])
  const items = list.data ? list.data.entities : []
  return h('div', { style: { display: 'flex', gap: 12, height: '100%', minHeight: 0 } },
    h('div', { style: { ...S.col, width: 260, flexShrink: 0, minHeight: 0 } },
      h('div', { style: { ...S.row, gap: 4 } },
        ['', ...ENTITY_TYPES].map(t => h(Btn, { key: t || 'all', kind: t === type ? 'primary' : undefined, onClick: () => setType(t) }, t || 'all'))),
      h('input', { style: S.input, value: q, placeholder: 'Search agents, swarms, cases', onChange: e => setQ(e.target.value) }),
      h('div', { style: { ...S.row, flexWrap: 'nowrap' } },
        h('select', { style: S.input, value: nt, onChange: e => setNt(e.target.value) }, ENTITY_TYPES.map(t => h('option', { key: t, value: t }, t))),
        h('input', { style: { ...S.input, flex: 1 }, value: nn, placeholder: 'New name', onChange: e => setNn(e.target.value) }),
        h(Btn, { disabled: !nn.trim(), onClick: async () => { const out = await act('/entities', { type: nt, name: nn.trim() }); if (out) { setNn(''); setSel(out.id) } } }, '+')),
      h('div', { style: { ...S.col, gap: 2, overflow: 'auto', flex: 1 } },
        items.length === 0 && h(Empty, null, 'No entities yet.'),
        items.map(e => h('div', {
          key: e.id, onClick: () => setSel(e.id),
          style: { padding: '4px 6px', borderRadius: 6, cursor: 'pointer', border: `1px solid ${e.id === sel ? V.accent : 'transparent'}` }
        }, h('div', null, e.name), h('div', { style: S.dim }, `${e.type}, ${e.degree} links, ${e.evidence_count} evidence`))))),
    h('div', { style: { ...S.col, flex: 1, minWidth: 0, overflow: 'auto' } },
      h(GraphView, { center: sel, selected: sel, onSelect: setSel, height: 300 }),
      sel ? h(EntityPane, { id: sel, names, onOpen: setSel, onGone: () => setSel(null) }) : h(Empty, null, 'Pick an entity, or click a node, to open its note.')))
}

// ---------------------------------------------------------------- settings and schedules

function FieldEditor({ name, field, value, onChange }) {
  const kind = field.kind
  if (kind === 'bool') return h('input', { type: 'checkbox', checked: !!value, onChange: e => onChange(e.target.checked) })
  if (kind === 'choice') return h('select', { style: S.input, value, onChange: e => onChange(e.target.value) }, field.choices.map(c => h('option', { key: c, value: c }, c)))
  if (kind === 'multi') {
    return h('div', { style: S.row }, field.choices.map(c => h('label', { key: c, style: S.row },
      h('input', { type: 'checkbox', checked: value.includes(c), onChange: e => onChange(e.target.checked ? [...value, c] : value.filter(v => v !== c)) }), c)))
  }
  if (kind === 'list') return h('textarea', { style: { ...S.input, minHeight: 48, width: '100%' }, value: value.join('\n'), placeholder: 'One per line', onChange: e => onChange(e.target.value.split('\n').map(s => s.trim()).filter(Boolean)) })
  if (kind === 'int' || kind === 'float') {
    return h('input', {
      type: 'number', style: { ...S.input, width: 110 }, value, min: field.min, max: field.max, step: kind === 'int' ? 1 : 0.5,
      onChange: e => { const n = Number(e.target.value); if (!Number.isNaN(n)) onChange(n) }
    })
  }
  return h('textarea', { style: { ...S.input, minHeight: 40, width: '100%' }, value, onChange: e => onChange(e.target.value) })
}

function ScheduleSection({ enabled }) {
  const q = useApi(['schedules'], '/schedules', 10000)
  const [f, setF] = useState({ name: '', kind: 'interval', spec: '6h', goal: '', max_cycles: 5 })
  const set = (k, v) => setF({ ...f, [k]: v })
  return h('div', { style: S.card },
    h('div', { style: S.h2 }, 'Scheduled hunts'),
    h('div', { style: S.dim }, enabled
      ? 'Armed schedules start a bounded hunt, only while this app is open and no hunt is running.'
      : 'Off. Turn on "Allow scheduled hunts" below, then arm a schedule. Nothing runs by itself until you do both.'),
    (q.data ? q.data.schedules : []).map(s => h('div', { key: s.id, style: { ...S.row, padding: '4px 0' } },
      h('span', null, s.name), h(Chip, null, `${s.kind} ${s.spec}`), h('span', { style: S.dim }, `${s.max_cycles} cycles`),
      h(Chip, { strong: !!s.enabled }, s.enabled ? `armed, next ${s.next_run_utc || '?'}` : 'not armed'),
      h(Btn, { onClick: () => act(`/schedules/${s.id}/arm`, { armed: !s.enabled }) }, s.enabled ? 'Disarm' : 'Arm'),
      h(Btn, { onClick: () => act(`/schedules/${s.id}`, undefined, 'DELETE') }, 'Delete'))),
    h('div', { style: { ...S.row, marginTop: 8 } },
      h('input', { style: S.input, value: f.name, placeholder: 'Name', onChange: e => set('name', e.target.value) }),
      h('select', { style: S.input, value: f.kind, onChange: e => set('kind', e.target.value) }, h('option', { value: 'interval' }, 'interval'), h('option', { value: 'cron' }, 'cron (UTC)')),
      h('input', { style: { ...S.input, width: 120 }, value: f.spec, placeholder: f.kind === 'cron' ? '0 */6 * * *' : '6h', onChange: e => set('spec', e.target.value) }),
      h('input', { type: 'number', style: { ...S.input, width: 70 }, value: f.max_cycles, min: 1, onChange: e => set('max_cycles', Number(e.target.value) || 1) }),
      h('input', { style: { ...S.input, flex: 1 }, value: f.goal, placeholder: 'Goal (optional)', onChange: e => set('goal', e.target.value) }),
      h(Btn, { disabled: !f.name.trim(), onClick: async () => { if (await act('/schedules', f)) set('name', '') } }, 'Add')))
}

function SettingsPage() {
  const q = useApi(['settings'], '/settings')
  const [draft, setDraft] = useState({})
  if (!q.data) return h(Error, { q })
  const { values, schema } = q.data
  const fields = schema.fields
  const groups = {}
  Object.keys(fields).forEach(k => { (groups[fields[k].group] = groups[fields[k].group] || []).push(k) })
  const dirty = Object.keys(draft).length > 0
  const save = async () => {
    const out = await act('/settings', { updates: draft }, 'PUT', 'Settings saved')
    if (out) setDraft({})
  }
  return h('div', { style: S.col },
    h('div', { style: S.row },
      h(Btn, { kind: 'primary', disabled: !dirty, onClick: save }, 'Save changes'),
      h(Btn, { disabled: !dirty, onClick: () => setDraft({}) }, 'Discard'),
      h('span', { style: S.dim }, 'Invalid values are refused as a whole.')),
    Object.keys(groups).map(group => h('div', { key: group, style: S.card },
      h('div', { style: S.h2 }, group),
      groups[group].map(k => {
        const value = k in draft ? draft[k] : values[k]
        return h('div', { key: k, style: { ...S.col, gap: 2, padding: '6px 0', borderTop: `1px solid ${V.line}` } },
          h('div', { style: S.row }, h('span', null, fields[k].label), h('span', { style: { ...S.mono, color: V.faint } }, k)),
          fields[k].help && h('div', { style: S.dim }, fields[k].help),
          h(FieldEditor, { name: k, field: fields[k], value, onChange: v => setDraft({ ...draft, [k]: v }) }))
      }))),
    h(ScheduleSection, { enabled: values['schedule.enabled'] }))
}

// ---------------------------------------------------------------- shell

const TABS = [['hunt', 'Hunt'], ['knowledge', 'Agents, swarms, cases'], ['evidence', 'Evidence'], ['iocs', 'IOCs'], ['settings', 'Settings']]

function Page() {
  const [tab, setTab] = useState('hunt')
  const pages = { hunt: HuntPage, knowledge: KnowledgePage, evidence: EvidencePage, iocs: IocsPage, settings: SettingsPage }
  return h('div', { style: S.page },
    h(Tabs, { tabs: TABS, value: tab, onChange: setTab }),
    h('div', { style: { ...S.body, ...(tab === 'knowledge' ? { overflow: 'hidden' } : null) } }, h(pages[tab], null)))
}

function StatusChip() {
  const q = useApi(['status'], '/status', 5000)
  const hunt = q.data && q.data.hunt
  const label = q.isError ? 'sf: offline' : hunt ? `sf: ${hunt.state}${q.data.running ? ` #${hunt.cycle}` : ''}` : 'sf: idle'
  return h('button', {
    type: 'button', onClick: () => host.navigate(PATH), title: 'Open Swarm Forensics',
    style: { background: 'transparent', border: 'none', color: q.data && q.data.running ? V.accent : V.dim, fontSize: '0.6875rem', padding: '0 6px', cursor: 'pointer' }
  }, label)
}

async function heartbeat() {
  try { await api('/heartbeat', { method: 'POST', body: {} }) } catch { /* backend off: the chip shows it */ }
}

async function pollAlerts(ctx) {
  try {
    const last = ctx.storage.get('lastEventId', null)
    const out = await api(`/events?after=${last || 0}&limit=${last === null ? 1 : 50}`)
    const events = out.events || []
    if (!events.length) return
    ctx.storage.set('lastEventId', events[events.length - 1].id)
    if (last === null) return // First run: start from now, no backlog toasts.
    events.filter(e => e.level === 'alert').forEach(e => host.notify({ kind: 'info', title: 'Swarm Forensics', message: e.message }))
    events.filter(e => e.kind === 'state' && e.level === 'warn').forEach(e => host.notify({ kind: 'info', title: 'Swarm Forensics', message: e.message }))
  } catch { /* ignore until the backend is up */ }
}

export default {
  id: ID,
  name: 'Swarm Forensics',
  defaultEnabled: false,
  register(ctx) {
    rest = ctx.rest
    heartbeat()
    ctx.setInterval(heartbeat, HEARTBEAT_MS)
    ctx.setInterval(() => pollAlerts(ctx), ALERT_POLL_MS)
    ctx.onEvent(`plugin.${ID}.hunt.state`, () => refresh())
    ctx.onEvent(`plugin.${ID}.hunt.cycle.done`, () => refresh())
    ctx.registerMany([
      { id: 'page', area: ROUTES_AREA, data: { path: PATH }, render: () => h(Page, null) },
      { id: 'nav', area: SIDEBAR_NAV_AREA, data: { path: PATH, label: 'Swarm Forensics', codicon: 'search' } },
      { id: 'status', area: STATUSBAR_AREAS.right, order: 130, render: () => h(StatusChip, null) },
      {
        id: 'open', area: PALETTE_AREA,
        data: { id: `${ID}.open`, label: 'Open Swarm Forensics', keywords: ['swarm', 'forensics', 'hunt'], run: () => host.navigate(PATH) }
      },
      {
        id: 'start', area: PALETTE_AREA,
        data: {
          id: `${ID}.start`, label: 'Swarm Forensics: start hunt', keywords: ['swarm', 'hunt', 'start'],
          run: () => { host.navigate(PATH); void act('/hunts/start', {}, 'POST', 'Hunt started') }
        }
      },
      {
        id: 'stop', area: PALETTE_AREA,
        data: { id: `${ID}.stop`, label: 'Swarm Forensics: stop hunt', keywords: ['swarm', 'hunt', 'stop'], run: () => void act('/hunts/stop', {}, 'POST', 'Stop requested') }
      },
      {
        id: 'open-key', area: KEYBINDS_AREA,
        data: { id: `${ID}.open-key`, label: 'Open Swarm Forensics', category: 'Swarm Forensics', defaults: ['mod+alt+f'], run: () => host.navigate(PATH) }
      }
    ])
  }
}
