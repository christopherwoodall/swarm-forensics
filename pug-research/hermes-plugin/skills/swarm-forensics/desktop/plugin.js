/**
 * Swarm Forensics desktop plugin — the hunting-dog control plane.
 *
 * Single hot-reloaded ESM file. UI is written with jsx() calls,
 * not JSX syntax. Imports resolve only from @hermes/plugin-sdk,
 * react, and react/jsx-runtime.
 *
 * Model: the human hunts, the dog fetches. There is NO autonomous
 * scanning, NO cron, NO background schedule in this lane. The human
 * opens the app, starts hunts, watches progress, cancels, triages
 * the review queue, manages IOCs, and edits settings. Every GUI
 * control calls the same plugin_api.py endpoints as the
 * /swarm-forensics CLI path: one config.ini, one state/ dir.
 *
 * Simplified Technical English in comments. HERMES_DESKTOP.md §1
 * row citations mark each contribution area used. Shapes marked
 * [INF] are inferred from the doc text, not quoted from it.
 */
import { jsx, jsxs, Fragment } from 'react/jsx-runtime';
import React, { useState, useEffect, useMemo, useRef } from 'react';
import * as sdk from '@hermes/plugin-sdk';

// UI kit. Names marked * in the doc use a fallback wrapper, because
// the exact subcomponent names are not quoted in the sections read.
const {
  Button, Input, Switch, Checkbox, SegmentedControl,
  Badge, StatusDot, SearchField, ScrollArea, EmptyState,
  CopyButton, Codicon, ConfirmDialog, LogView, cn,
  useQuery,
} = sdk;
const Tabs = sdk.Tabs || (({ children }) => jsx('div', { children }));
const TabList = sdk.TabList || (({ children }) => jsx('div', { children }));
const Tab = sdk.Tab || (({ children }) => jsx('button', { children }));
const TabPanel = sdk.TabPanel || (({ children }) => jsx('div', { children }));
const Dialog = sdk.Dialog || (({ children, open }) => open ? jsx('div', { children }) : null);
const DialogTitle = sdk.DialogTitle || (({ children }) => jsx('h3', null, children));
const Select = sdk.Select || 'select';

// ---------------------------------------------------------------------------
// Minimal shared store. The doc names atom/computed for local state, but
// the exact atom API shape is not quoted in the sections read, so this
// file uses plain React state plus a module-scope store. See report.
// ---------------------------------------------------------------------------
const _listeners = new Set();
const store = {
  state: {
    uiEnabled: true,      // Appearance extra: compact enable switch
    selectedReviewId: null,
    pendingNarrowId: null,
    lastSeenHitUtc: null,
    casesNewOpen: false,  // palette "New case entity…" opens the dialog
  },
  set(patch) {
    Object.assign(this.state, patch);
    _listeners.forEach((fn) => fn(this.state));
  },
  subscribe(fn) {
    _listeners.add(fn);
    return () => _listeners.delete(fn);
  },
};
function useStore() {
  const [s, setS] = useState(store.state);
  useEffect(() => store.subscribe(setS), []);
  return [s, (p) => store.set(p)];
}

// ---------------------------------------------------------------------------
// Backend access. ctx.rest hits the plugin namespace /api/plugins/
// swarm-forensics (HERMES_DESKTOP.md §1: ctx.rest / ctx.socket). The options
// shape below is [INF]: the doc names the method but does not quote
// the parameter shape. Live hit streaming is not used; polling via
// useQuery refetchInterval is the documented pattern (Gap 4).
// ---------------------------------------------------------------------------
async function rest(ctx, method, path, body) {
  const opts = { method };
  if (body !== undefined) {
    opts.headers = { 'Content-Type': 'application/json' };
    opts.body = JSON.stringify(body);
  }
  const res = await ctx.rest(path, opts); // [INF] options shape
  if (res && typeof res.json === 'function') return res.json();
  return res;
}
const apiGet = (ctx, path) => rest(ctx, 'GET', path);
const apiPost = (ctx, path, body) => rest(ctx, 'POST', path, body || {});
const apiPut = (ctx, path, body) => rest(ctx, 'PUT', path, body || {});
const apiDelete = (ctx, path) => rest(ctx, 'DELETE', path);

function useApi(ctx, key, path, intervalMs) {
  return useQuery({
    queryKey: ['swarm-forensics', key],
    queryFn: () => apiGet(ctx, path),
    refetchInterval: intervalMs || 15000,
    retry: 1,
  });
}

// host.* surface (HERMES_DESKTOP.md §1 capabilities). The doc lists the
// capability names; exposure as ctx.host is [INF]. The closest
// alternative is sdk-exported hooks, which the sections read do not
// name, so this file reads ctx.host and degrades when absent.
function getHost(ctx) {
  return (ctx && ctx.host) || {};
}
function notify(ctx, kind, message) {
  const host = getHost(ctx);
  if (typeof host.notify === 'function') host.notify({ kind, message });
}
function navigate(ctx, path) {
  const host = getHost(ctx);
  if (typeof host.navigate === 'function') host.navigate(path);
}

// ---------------------------------------------------------------------------
// Shared bits
// ---------------------------------------------------------------------------
const SOURCES = [
  { id: 'urlquery', label: 'urlquery' },
  { id: 'cdx', label: 'Wayback CDX' },
  { id: 'arquivo', label: 'arquivo.pt' },
];
const CLAIM_LEVELS = ['L1', 'L2', 'L3', 'L4', 'L5'];

function claimRank(level) {
  return CLAIM_LEVELS.indexOf(level);
}
function meetsThreshold(level, threshold) {
  return claimRank(level) >= claimRank(threshold || 'L3');
}

// Private mode (ADVERSARIAL.md #1): watch-term strings render masked.
// Reveal is per-term and explicit. Never render raw terms in this
// component when privateMode is on.
function MaskedTerm({ term, privateMode }) {
  const [revealed, setRevealed] = useState(false);
  if (!privateMode || revealed) return jsx('code', null, term);
  return jsx(
    'button',
    {
      onClick: () => setRevealed(true),
      title: 'Reveal term (private mode)',
      style: { cursor: 'pointer' },
    },
    '\u2022\u2022\u2022\u2022'
  );
}

function Page({ title, children, actions }) {
  return jsxs('div', {
    style: { padding: 16, maxWidth: 1100, margin: '0 auto' },
    children: [
      jsxs('div', {
        key: 'head',
        style: { display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 },
        children: [
          jsx('h1', { key: 't', style: { margin: 0, fontSize: 20 } }, title),
          jsx('div', { key: 'a', style: { marginLeft: 'auto', display: 'flex', gap: 8 } }, actions || null),
        ],
      }),
      jsx('div', { key: 'body' }, children),
    ],
  });
}

function Card({ title, children, wide }) {
  return jsxs('div', {
    style: {
      border: '1px solid var(--swarm-forensics-border, transparent)',
      borderRadius: 8, padding: 12, marginBottom: 12,
      flex: wide ? '1 1 100%' : '1 1 280px',
    },
    children: [
      title ? jsx('h3', { key: 't', style: { margin: '0 0 8px', fontSize: 14 } }, title) : null,
      jsx('div', { key: 'c' }, children),
    ],
  });
}

// Backend status indicator. The Python backend loads via a separate
// toggle (Gap 5), so the UI must show connected / degraded /
// disconnected explicitly instead of failing silently.
function BackendBadge({ ctx }) {
  const { data, isError } = useApi(ctx, 'diag', '/diagnostics', 30000);
  if (isError || !data) {
    return jsx(Badge, { variant: 'destructive' }, 'backend: disconnected');
  }
  return jsx(Badge, { variant: 'outline' }, 'backend: connected');
}

// Review queue depth badge, shared by nav-adjacent surfaces.
function QueueBadge({ ctx }) {
  const { data } = useApi(ctx, 'review', '/review', 30000);
  const n = data && data.entries ? data.entries.length : 0;
  const sla = data && data.entries
    ? data.entries.filter((e) => e.sla_breach).length : 0;
  if (n === 0) return null;
  return jsx(Badge, { variant: sla ? 'destructive' : 'secondary' },
    sla ? `${n} (${sla} overdue)` : `${n}`);
}

// ---------------------------------------------------------------------------
// Dashboard — /swarm-forensics (HERMES_DESKTOP.md §1 row: ROUTES_AREA)
// ---------------------------------------------------------------------------
function stateColor(state) {
  // green idle / amber running / red throttled / grey paused
  if (state === 'paused') return 'grey';
  if (state === 'running') return 'amber';
  if (state === 'throttled') return 'red';
  return 'green';
}

function Sparkline({ values }) {
  // Novelty-rate health (LEARNING.md): fraction of hits from outside
  // the current list. Flatline over two cycles raises the alert.
  const w = 140, h = 36;
  const bars = values.map((v, i) => {
    const bh = Math.max(2, v * h);
    return jsx('rect', {
      key: i, x: i * (w / values.length), y: h - bh,
      width: Math.max(2, w / values.length - 2), height: bh,
      fill: 'currentColor', opacity: 0.7,
    });
  });
  return jsx('svg', { width: w, height: h, role: 'img' }, bars);
}

function DashboardPage({ ctx }) {
  const [storeState, setStore] = useStore();
  const diag = useApi(ctx, 'diag', '/diagnostics', 15000);
  const hitsQ = useApi(ctx, 'hits', '/hits', 30000);
  const iocsQ = useApi(ctx, 'iocs', '/iocs', 30000);
  const reviewQ = useApi(ctx, 'review', '/review', 30000);
  const jobsQ = useApi(ctx, 'jobs', '/jobs', 5000);
  const settingsQ = useApi(ctx, 'settings', '/settings', 60000);
  const [confirmPause, setConfirmPause] = useState(false);

  const paused = diag.data && diag.data.paused;
  const jobs = (jobsQ.data && jobsQ.data.jobs) || [];
  const running = jobs.find((j) => j.status === 'running' || j.status === 'queued');
  const scannerState = paused ? 'paused' : running ? 'running' : 'idle';

  const hits = (hitsQ.data && hitsQ.data.hits) || [];
  const today = new Date().toISOString().slice(0, 10);
  const todays = hits.filter((h) => (h.observed_utc || '').startsWith(today));
  const byLevel = {};
  CLAIM_LEVELS.forEach((l) => { byLevel[l] = 0; });
  todays.forEach((h) => { byLevel[h.claim_level || 'L1'] += 1; });

  const iocs = (iocsQ.data && iocsQ.data.iocs) || [];
  const counts = { active: 0, proposed: 0, inactive: 0, quarantined: 0 };
  iocs.forEach((r) => {
    if (counts[r.status] === undefined) counts[r.status] = 0;
    counts[r.status] += 1;
  });

  // Novelty rate per day over the last 14 days.
  const activeSet = useMemo(() => new Set(
    iocs.filter((r) => r.status === 'active').map((r) => r.term)), [iocs]);
  const novelty = useMemo(() => {
    const days = [];
    for (let d = 13; d >= 0; d--) {
      const day = new Date(Date.now() - d * 86400000).toISOString().slice(0, 10);
      const dayHits = hits.filter((h) => (h.observed_utc || '').startsWith(day));
      if (dayHits.length === 0) { days.push(0); continue; }
      const novel = dayHits.filter((h) => !activeSet.has(h.term)).length;
      days.push(novel / dayHits.length);
    }
    return days;
  }, [hits, activeSet]);
  const flatlined = novelty.length >= 2 &&
    novelty[novelty.length - 1] === 0 && novelty[novelty.length - 2] === 0;

  // Toast only high-claim hits, gated by alert_on_claim_level
  // (default L3+). There is no notification center in the app
  // chrome; the dashboard is the inbox (Gap 6).
  useEffect(() => {
    if (!hitsQ.data || !settingsQ.data) return;
    const threshold = (settingsQ.data.safety || {}).alert_on_claim_level || 'L3';
    const fresh = hits.filter((h) =>
      meetsThreshold(h.claim_level || 'L1', threshold) &&
      (!storeState.lastSeenHitUtc || h.observed_utc > storeState.lastSeenHitUtc));
    if (fresh.length > 0) {
      const top = fresh[0];
      notify(ctx, 'warning',
        `Swarm Forensics: ${fresh.length} new ${threshold}+ hit(s). Latest: ${top.term} on ${top.source}.`);
      const maxUtc = fresh.reduce((m, h) =>
        h.observed_utc > m ? h.observed_utc : m, storeState.lastSeenHitUtc || '');
      setStore({ lastSeenHitUtc: maxUtc });
    }
  }, [hitsQ.dataUpdatedAt]);

  const doPause = async (pause) => {
    await apiPost(ctx, '/settings/pause', { paused: pause });
    diag.refetch();
    notify(ctx, 'info', pause ? 'All hunting paused.' : 'Hunting resumed.');
  };

  const lastJobBySource = {};
  jobs.forEach((j) => {
    (j.sources || []).forEach((s) => {
      if (!lastJobBySource[s] || j.created_utc > lastJobBySource[s].created_utc) {
        lastJobBySource[s] = j;
      }
    });
  });

  return jsx(Page, {
    title: 'Swarm Forensics dashboard',
    actions: jsx(BackendBadge, { ctx }),
    children: jsxs(Fragment, {
      children: [
        // Kill switch: prominent, destructive, confirmed. Paused
        // state must be unmissable.
        jsxs('div', {
          key: 'kill',
          style: {
            border: '2px solid', borderRadius: 8, padding: 12,
            marginBottom: 16, display: 'flex', alignItems: 'center', gap: 12,
          },
          children: [
            jsx(StatusDot, { key: 'd', color: stateColor(scannerState) }),
            jsxs('div', {
              key: 't', style: { flex: 1 },
              children: [
                jsx('strong', { key: 's' },
                  paused ? 'HUNTING PAUSED — kill switch is ON' : `Scanner: ${scannerState}`),
                jsx('div', { key: 'u' },
                  paused
                    ? 'No hunt can start. Resume is a deliberate click.'
                    : running
                      ? `Job ${running.job_id}: ${running.done}/${running.total} queries.`
                      : 'Idle. Hunts start only when you start them.'),
              ],
            }),
            paused
              ? jsx(Button, { key: 'b', onClick: () => doPause(false) }, 'Resume hunting')
              : jsx(Button, {
                  key: 'b', variant: 'destructive',
                  onClick: () => setConfirmPause(true),
                }, 'Pause all hunting'),
          ],
        }),
        jsx(ConfirmDialog, {
          key: 'cd',
          open: confirmPause,
          title: 'Pause all hunting?',
          description: 'This stops every hunt now and blocks new ones until you resume.',
          onConfirm: () => { setConfirmPause(false); doPause(true); },
          onCancel: () => setConfirmPause(false),
        }),
        jsxs('div', {
          key: 'cards',
          style: { display: 'flex', flexWrap: 'wrap', gap: 12 },
          children: [
            jsx(Card, {
              key: 'hits', title: 'Hits today',
              children: CLAIM_LEVELS.map((l) =>
                jsxs('span', { key: l, style: { marginRight: 8 } },
                  [jsx(Badge, { key: 'b' }, l), ` ${byLevel[l]} `])),
            }),
            jsx(Card, {
              key: 'iocs', title: 'IOC list',
              children: Object.entries(counts).map(([k, v]) =>
                jsxs('div', { key: k }, [`${k}: `, jsx('strong', { key: 'v' }, v)])),
            }),
            jsx(Card, {
              key: 'nov', title: 'Novelty-rate health (14d)',
              children: jsxs(Fragment, {
                children: [
                  jsx(Sparkline, { key: 's', values: novelty }),
                  flatlined
                    ? jsx('div', { key: 'w', style: { fontWeight: 'bold' } },
                        'Discovery flatlined — the loop may be describing itself.')
                    : jsx('div', { key: 'w' }, 'Novelty is flowing.'),
                ],
              }),
            }),
            jsx(Card, {
              key: 'rev', title: 'Review queue',
              children: jsxs(Fragment, {
                children: [
                  jsx(QueueBadge, { key: 'q', ctx }),
                  jsx('div', { key: 'g' },
                    jsx(Button, {
                      variant: 'link',
                      onClick: () => navigate(ctx, '/swarm-forensics/review'),
                    }, 'Open review queue')),
                ],
              }),
            }),
          ],
        }),
        jsx(Card, {
          key: 'src', title: 'Sources — last hunt', wide: true,
          children: SOURCES.map((s) => {
            const j = lastJobBySource[s.id];
            const ps = j && j.per_source && j.per_source[s.id];
            return jsxs('div', {
              key: s.id,
              style: { display: 'flex', gap: 12, padding: '4px 0' },
              children: [
                jsx('strong', { key: 'n', style: { width: 110 } }, s.label),
                jsx('span', { key: 't' },
                  j ? `last hunt ${String(j.created_utc).slice(0, 16)}Z — ${j.status}, ${j.new_hits || 0} new hits`
                    : 'no hunt this session'),
                jsx('span', { key: 'h' },
                  ps ? `throttled: ${ps.throttled || 0}, errors: ${ps.errors || 0}` : 'throttle: —'),
              ],
            });
          }),
        }),
        jsx(Card, {
          key: 'recent', title: 'Recent hits', wide: true,
          children: todays.length === 0
            ? jsx(EmptyState, {
                title: paused ? 'Scanner paused' : 'No hits today',
                description: paused
                  ? 'Hits stop when the kill switch is on.'
                  : 'Start a hunt from the Hunt page.',
              })
            : jsx(ScrollArea, {
                style: { maxHeight: 260 },
                children: todays.slice(0, 20).map((h, i) =>
                  jsxs('div', {
                    key: i, style: { display: 'flex', gap: 8, padding: '2px 0' },
                    children: [
                      jsx(Badge, { key: 'l' }, h.claim_level || 'L1'),
                      jsx('span', { key: 's' }, h.source),
                      jsx(MaskedTerm, {
                        key: 't',
                        term: h.term,
                        privateMode: (settingsQ.data && settingsQ.data.safety || {}).private_mode !== 'false',
                      }),
                      jsx(CopyButton, { key: 'c', value: h.url || '' }),
                    ],
                  })),
              }),
        }),
      ],
    }),
  });
}

// ---------------------------------------------------------------------------
// Hunt — /swarm-forensics/hunt
// ---------------------------------------------------------------------------
function HuntPage({ ctx }) {
  const [target, setTarget] = useState('');
  const [sources, setSources] = useState({ urlquery: true, cdx: true, arquivo: true });
  const [cap, setCap] = useState(200);
  const [jobId, setJobId] = useState(null);
  const settingsQ = useApi(ctx, 'settings', '/settings', 60000);
  const iocsQ = useApi(ctx, 'iocs', '/iocs', 60000);
  const jobsQ = useApi(ctx, 'jobs', '/jobs', 5000);
  const jobQ = useApi(ctx, jobId ? `job-${jobId}` : 'job-none',
    jobId ? `/jobs/${jobId}` : '/jobs', jobId ? 2000 : 30000);

  const activeTerms = ((iocsQ.data && iocsQ.data.iocs) || [])
    .filter((r) => r.status === 'active').length;
  const enabledSources = SOURCES.filter((s) => sources[s.id]);
  const maxCap = parseInt(
    (settingsQ.data && settingsQ.data.sources || {}).max_terms_per_sweep || '200', 10);
  const estimate = Math.min(target ? 1 : activeTerms, Math.min(cap, maxCap)) *
    enabledSources.length;

  const startHunt = async () => {
    const res = await apiPost(ctx, '/hunt/start', {
      target: target.trim(),
      sources: enabledSources.map((s) => s.id),
      cap: Math.min(cap, maxCap),
    });
    if (res.error) {
      notify(ctx, 'error', `Hunt refused: ${res.error}`);
      return;
    }
    setJobId(res.job_id);
    jobsQ.refetch();
    notify(ctx, 'info', `Hunt ${res.job_id} started.`);
  };
  const stopHunt = async () => {
    if (!jobId) return;
    await apiPost(ctx, '/hunt/stop', { job_id: jobId });
    jobQ.refetch();
  };

  const job = jobId && jobQ.data && jobQ.data.job_id ? jobQ.data : null;
  const jobs = (jobsQ.data && jobsQ.data.jobs) || [];

  return jsx(Page, {
    title: 'Hunt',
    actions: jsx(BackendBadge, { ctx }),
    children: jsxs(Fragment, {
      children: [
        jsx(Card, {
          key: 'form', title: 'Start a hunt', wide: true,
          children: jsxs('div', {
            style: { display: 'flex', flexDirection: 'column', gap: 12 },
            children: [
              jsxs('label', {
                key: 't', children: [
                  'Target term (blank = sweep the active list)',
                  jsx(Input, {
                    key: 'i', value: target,
                    onChange: (e) => setTarget(e.target.value),
                    placeholder: 'zz=oai',
                  }),
                ],
              }),
              jsxs('div', {
                key: 's', style: { display: 'flex', gap: 12 },
                children: SOURCES.map((s) =>
                  jsxs('label', {
                    key: s.id, style: { display: 'flex', gap: 6, alignItems: 'center' },
                    children: [
                      jsx(Checkbox, {
                        key: 'c', checked: !!sources[s.id],
                        onChange: (v) => setSources({ ...sources, [s.id]: !!v }),
                      }),
                      s.label,
                    ],
                  })),
              }),
              jsxs('label', {
                key: 'c', children: [
                  `Sweep cap (max ${maxCap}) — about ${estimate} queries`,
                  jsx(Input, {
                    key: 'i', type: 'number', value: cap, min: 1, max: maxCap,
                    onChange: (e) => setCap(parseInt(e.target.value || '1', 10)),
                  }),
                ],
              }),
              jsxs('div', {
                key: 'b', style: { display: 'flex', gap: 8 },
                children: [
                  jsx(Button, { key: 'go', onClick: startHunt }, 'Start hunt'),
                  job && (job.status === 'running' || job.status === 'queued')
                    ? jsx(Button, { key: 'stop', variant: 'destructive', onClick: stopHunt }, 'Cancel hunt')
                    : null,
                ],
              }),
            ],
          }),
        }),
        job ? jsx(Card, {
          key: 'prog', title: `Job ${job.job_id} — ${job.status}`, wide: true,
          children: jsxs(Fragment, {
            children: [
              jsx('div', { key: 'o' },
                `Overall: ${job.done || 0}/${job.total || 0} queries, ${job.new_hits || 0} new hits.`),
              Object.entries(job.per_source || {}).map(([s, p]) =>
                jsxs('div', {
                  key: s, style: { display: 'flex', gap: 8, alignItems: 'center' },
                  children: [
                    jsx('span', { key: 'n', style: { width: 90 } }, s),
                    jsx('progress', {
                      key: 'p', value: p.done, max: Math.max(1, p.total),
                      style: { flex: 1 },
                    }),
                    jsx('span', { key: 'v' }, `${p.done}/${p.total}`),
                  ],
                })),
              job.error ? jsx('div', { key: 'e' }, `Error: ${job.error}`) : null,
            ],
          }),
        }) : null,
        jsx(Card, {
          key: 'hist', title: 'Hunt history', wide: true,
          children: jobs.length === 0
            ? jsx(EmptyState, { title: 'No hunts yet', description: 'Start one above.' })
            : jobs.slice(0, 15).map((j) =>
              jsxs('div', {
                key: j.job_id, style: { display: 'flex', gap: 12, padding: '4px 0' },
                children: [
                  jsx(Badge, { key: 's' }, j.status),
                  jsx('code', { key: 'i' }, j.job_id),
                  jsx('span', { key: 't' }, j.target || '(active list)'),
                  jsx('span', { key: 'u' }, (j.sources || []).join(',')),
                  jsx('span', { key: 'h' }, `${j.new_hits || 0} hits`),
                ],
              })),
        }),
      ],
    }),
  });
}

// ---------------------------------------------------------------------------
// Inline candidate card — the fast path (HERMES_DESKTOP.md §2.7 inline
// accept). Renders wherever a candidate surfaces: chat replies and
// hunt results. Every button calls POST /review/decision. The full
// Review page stays the complete triage view.
// ---------------------------------------------------------------------------
function CandidateCard({ ctx, entryId, term, provenance, ageDays, slaBreach, onDecided }) {
  const [narrowOpen, setNarrowOpen] = useState(false);
  const [narrower, setNarrower] = useState('');
  const [rationale, setRationale] = useState('');
  const [done, setDone] = useState(null);

  const decide = async (verdict, narrowerChunk) => {
    // The backend records an explicit default rationale when the
    // fast path leaves it blank; Worker-2 requires a rationale.
    const res = await apiPost(ctx, '/review/decision', {
      id: entryId || term, verdict, rationale,
      narrower_chunk: narrowerChunk || '',
    });
    if (res.error) {
      notify(ctx, 'error', `Decision failed: ${res.error}`);
      return;
    }
    setDone(verdict);
    notify(ctx, 'info', `${term}: ${verdict}.`);
    if (onDecided) onDecided(entryId || term, verdict);
  };

  if (done) {
    return jsxs('div', {
      style: { border: '1px solid', borderRadius: 8, padding: 8, marginBottom: 8 },
      children: [
        jsx('code', { key: 't' }, term),
        jsx(Badge, { key: 'b' }, done),
      ],
    });
  }
  return jsxs('div', {
    style: { border: '1px solid', borderRadius: 8, padding: 8, marginBottom: 8 },
    children: [
      jsxs('div', {
        key: 'h', style: { display: 'flex', gap: 8, alignItems: 'center' },
        children: [
          jsx('code', { key: 't' }, term),
          slaBreach ? jsx(Badge, { key: 's', variant: 'destructive' }, 'SLA overdue') : null,
          ageDays !== undefined ? jsx('span', { key: 'a' }, `${ageDays}d old`) : null,
        ],
      }),
      provenance ? jsx('div', { key: 'p', style: { fontSize: 12 } }, `From: ${provenance}`) : null,
      jsxs('div', {
        key: 'b', style: { display: 'flex', gap: 8, marginTop: 8, flexWrap: 'wrap' },
        children: [
          jsx(Button, { key: 'a', size: 'sm', onClick: () => decide('accept') }, 'Accept'),
          jsx(Button, { key: 'r', size: 'sm', variant: 'outline', onClick: () => decide('reject') }, 'Reject'),
          jsx(Button, {
            key: 'n', size: 'sm', variant: 'outline',
            onClick: () => setNarrowOpen(!narrowOpen),
          }, 'Narrow'),
        ],
      }),
      jsx(Input, {
        key: 'rat', value: rationale, style: { marginTop: 8 },
        placeholder: 'Rationale (recorded with the decision)',
        onChange: (e) => setRationale(e.target.value),
      }),
      narrowOpen ? jsxs('div', {
        key: 'n', style: { display: 'flex', flexDirection: 'column', gap: 8, marginTop: 8 },
        children: [
          jsx(Input, {
            key: 'i', value: narrower, placeholder: 'Narrower chunk (observed co-occurrence)',
            onChange: (e) => setNarrower(e.target.value),
          }),
          jsx(Button, {
            key: 'g', size: 'sm',
            disabled: !narrower.trim(),
            onClick: () => decide('narrow', narrower.trim()),
          }, 'Propose narrower chunk'),
        ],
      }) : null,
    ],
  });
}

// ---------------------------------------------------------------------------
// Chat — /swarm-forensics/chat. The human talks to the hunting-dog.
// Messages go to POST /chat. The responder is rule-based first
// (zero model dependency); an optional model path exists behind
// config [chat]. The UI always shows which path is active.
// ---------------------------------------------------------------------------
function ChatPage({ ctx }) {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [sending, setSending] = useState(false);
  const [mode, setMode] = useState({ mode: 'rule', detail: '' });
  const scrollRef = useRef(null);

  useEffect(() => {
    apiGet(ctx, '/chat').then((d) => {
      if (d && d.history) setMessages(d.history);
      if (d && d.chat_mode) setMode(d.chat_mode);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages]);

  const send = async () => {
    const text = input.trim();
    if (!text || sending) return;
    setInput('');
    setSending(true);
    const userMsg = { role: 'user', text, utc: new Date().toISOString() };
    setMessages((m) => [...m, userMsg]);
    try {
      const reply = await apiPost(ctx, '/chat', { message: text });
      if (reply.mode) setMode({ mode: reply.mode, detail: '' });
      setMessages((m) => [...m, reply]);
      if (reply.action && reply.action.type === 'hunt_started') {
        notify(ctx, 'info', `Hunt started: ${reply.action.job_id}`);
      }
    } catch (e) {
      setMessages((m) => [...m, {
        role: 'assistant', text: `Chat backend error: ${e.message || e}`,
        cards: [], utc: new Date().toISOString(),
      }]);
    }
    setSending(false);
  };

  return jsx(Page, {
    title: 'Chat with the hunting-dog',
    actions: jsxs(Fragment, {
      children: [
        jsx(BackendBadge, { key: 'b', ctx }),
        jsx(Badge, { key: 'm', variant: 'outline', title: mode.detail || '' },
          mode.mode === 'model' ? 'brain: model path' : 'brain: rule-based'),
      ],
    }),
    children: jsxs('div', {
      style: { display: 'flex', flexDirection: 'column', height: '60vh' },
      children: [
        jsx('div', {
          key: 'mode', style: { fontSize: 12, marginBottom: 8 },
          children: mode.mode === 'model'
            ? 'Model path active: replies are rephrased by your configured endpoint. Actions stay rule-based.'
            : 'Rule-based responder: no model calls. The dog understands: hunt <term>, what did you find?, why was \'<term>\' flagged?, show queue, pause, resume.',
        }),
        jsx(ScrollArea, {
          key: 'log',
          children: jsx('div', {
            ref: scrollRef,
            style: { display: 'flex', flexDirection: 'column', gap: 8, paddingRight: 8 },
            children: messages.length === 0
              ? jsx(EmptyState, {
                  title: 'Say hello to the dog',
                  description: 'Try: hunt zz=oai on urlquery',
                })
              : messages.map((m, i) =>
                jsxs('div', {
                  key: i,
                  style: {
                    alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
                    maxWidth: '85%', border: '1px solid', borderRadius: 8, padding: 8,
                  },
                  children: [
                    jsx('div', {
                      key: 't', style: { whiteSpace: 'pre-wrap' },
                      children: m.text,
                    }),
                    (m.cards || []).map((c, j) =>
                      jsx(CandidateCard, {
                        key: `c${j}`, ctx, entryId: c.entry_id, term: c.term,
                        provenance: c.provenance, ageDays: c.age_days,
                        slaBreach: c.sla_breach,
                      })),
                  ],
                })),
          }),
        }),
        jsxs('div', {
          key: 'in', style: { display: 'flex', gap: 8, marginTop: 8 },
          children: [
            jsx(Input, {
              key: 'i', value: input, placeholder: 'hunt zz=oai on urlquery',
              onChange: (e) => setInput(e.target.value),
              onKeyDown: (e) => { if (e.key === 'Enter') send(); },
              disabled: sending,
            }),
            jsx(Button, { key: 's', onClick: send, disabled: sending },
              sending ? '...' : 'Send'),
          ],
        }),
      ],
    }),
  });
}

// ---------------------------------------------------------------------------
// Review — /swarm-forensics/review. The human queue made real.
// ---------------------------------------------------------------------------
function ReviewPage({ ctx }) {
  const [storeState, setStore] = useStore();
  const reviewQ = useApi(ctx, 'review', '/review', 10000);
  const [filter, setFilter] = useState('');
  const [sort, setSort] = useState('oldest');

  const entries = (reviewQ.data && reviewQ.data.entries) || [];
  const slaDays = (reviewQ.data && reviewQ.data.sla_days) || 7;
  const shown = entries
    .filter((e) => !filter || e.term.toLowerCase().includes(filter.toLowerCase()))
    .sort((a, b) => sort === 'oldest' ? b.age_days - a.age_days : a.age_days - b.age_days);

  const onDecided = (decidedId) => {
    reviewQ.refetch();
    if (storeState.selectedReviewId === decidedId) setStore({ selectedReviewId: null });
  };

  return jsx(Page, {
    title: 'Review queue',
    actions: jsxs(Fragment, {
      children: [
        jsx(QueueBadge, { key: 'q', ctx }),
        jsx(BackendBadge, { key: 'b', ctx }),
      ],
    }),
    children: jsxs(Fragment, {
      children: [
        jsx('div', {
          key: 'bar', style: { fontSize: 12, marginBottom: 8 },
          children: `SLA: ${slaDays} days. Every decision writes reviewer, timestamp, and rationale to the term's provenance.`,
        }),
        jsxs('div', {
          key: 'ctl', style: { display: 'flex', gap: 8, marginBottom: 12 },
          children: [
            jsx(SearchField, {
              key: 'f', value: filter,
              onChange: (e) => setFilter(e.target.value),
              placeholder: 'Filter terms...',
            }),
            jsx(Select, {
              key: 's', value: sort,
              onChange: (e) => setSort(e.target.value),
              children: [
                jsx('option', { key: 'o', value: 'oldest' }, 'Oldest first'),
                jsx('option', { key: 'n', value: 'newest' }, 'Newest first'),
              ],
            }),
          ],
        }),
        shown.length === 0
          ? jsx(EmptyState, {
              key: 'e', title: 'Queue empty',
              description: 'Nothing waits for review. Good hunting.',
            })
          : shown.map((e) =>
            jsxs('div', {
              key: e.id,
              onClick: () => setStore({ selectedReviewId: e.id }),
              style: {
                border: '1px solid', borderRadius: 8, padding: 12, marginBottom: 12,
                outline: storeState.selectedReviewId === e.id ? '2px solid' : 'none',
              },
              children: [
                jsxs('div', {
                  key: 'h', style: { display: 'flex', gap: 8, alignItems: 'center', marginBottom: 8 },
                  children: [
                    jsx('code', { key: 't', style: { fontSize: 15 } }, e.term),
                    jsx(Badge, { key: 'c' }, e.category),
                    e.sla_breach
                      ? jsx(Badge, { key: 's', variant: 'destructive' },
                          `SLA overdue (${e.age_days}d)`)
                      : jsx(Badge, { key: 's', variant: 'outline' }, `${e.age_days}d old`),
                    e.decision
                      ? jsx(Badge, { key: 'd', variant: 'secondary' },
                          `decided: ${e.decision.verdict}`)
                      : null,
                  ],
                }),
                jsx('div', {
                  key: 'prov', style: { fontSize: 12, marginBottom: 8 },
                  children: `Provenance: ${e.provenance || 'unknown'} — added ${e.added_utc.slice(0, 16)}Z`,
                }),
                (e.evidence_excerpts || []).map((x, i) =>
                  jsxs('div', {
                    key: i, style: { fontSize: 12, marginBottom: 4 },
                    children: [
                      jsx(Badge, { key: 'b' }, x.source),
                      jsx('span', { key: 'x' }, ` ${x.evidence}`),
                    ],
                  })),
                e.venues && e.venues.length > 0
                  ? jsx('div', {
                      key: 'v', style: { fontSize: 12 },
                      children: `Venues: ${e.venues.join(', ')} (${e.venue_count})`,
                    })
                  : null,
                jsx('div', {
                  key: 'fw', style: { fontSize: 12, fontStyle: 'italic' },
                  children: `Firewall: ${e.firewall_recommendation}`,
                }),
                jsx('div', { key: 'cc', style: { marginTop: 8 } },
                  jsx(CandidateCard, {
                    ctx, entryId: e.id, term: e.term, provenance: e.provenance,
                    ageDays: e.age_days, slaBreach: e.sla_breach,
                    onDecided,
                  })),
              ],
            })),
      ],
    }),
  });
}

// ---------------------------------------------------------------------------
// IOCs — /swarm-forensics/iocs. The working list, fully editable in-GUI.
// Manual adds and bulk imports enter as proposed: they go to the
// review queue, never straight to active.
// ---------------------------------------------------------------------------
function IocsPage({ ctx }) {
  const iocsQ = useApi(ctx, 'iocs', '/iocs', 15000);
  const settingsQ = useApi(ctx, 'settings', '/settings', 60000);
  const [filter, setFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [newTerm, setNewTerm] = useState('');
  const [bulk, setBulk] = useState('');
  const [bulkOpen, setBulkOpen] = useState(false);
  const [demoteFor, setDemoteFor] = useState(null);
  const [demoteReason, setDemoteReason] = useState('');
  const [provFor, setProvFor] = useState(null);

  const privateMode = (settingsQ.data && settingsQ.data.safety || {}).private_mode !== 'false';
  const iocs = (iocsQ.data && iocsQ.data.iocs) || [];
  const shown = iocs.filter((r) =>
    (statusFilter === 'all' || r.status === statusFilter) &&
    (!filter || r.term.toLowerCase().includes(filter.toLowerCase())));

  const addTerm = async () => {
    const term = newTerm.trim();
    if (!term) return;
    const res = await apiPost(ctx, '/iocs', { term });
    if (res.error) notify(ctx, 'error', res.error);
    else notify(ctx, 'info', `'${term}' proposed. It waits in the review queue.`);
    setNewTerm('');
    iocsQ.refetch();
  };
  const bulkImport = async () => {
    const terms = bulk.split('\n').map((t) => t.trim()).filter(Boolean);
    const res = await apiPost(ctx, '/iocs/bulk-import', { terms });
    notify(ctx, 'info', `Bulk import: ${res.added} proposed, ${res.skipped} already known.`);
    setBulk('');
    setBulkOpen(false);
    iocsQ.refetch();
  };
  const demote = async () => {
    if (!demoteFor) return;
    const res = await apiPost(ctx, `/iocs/${encodeURIComponent(demoteFor)}/demote`,
      { reason: demoteReason });
    if (res.error || !res.demoted) notify(ctx, 'error', 'Demote failed.');
    else notify(ctx, 'info', `'${demoteFor}' demoted to inactive. Terms are never deleted.`);
    setDemoteFor(null);
    setDemoteReason('');
    iocsQ.refetch();
  };
  const exportIocs = () => {
    // The backend serves the JSON as a download. Fetch it through
    // ctx.rest so the plugin namespace is honored, then save it.
    apiGet(ctx, '/iocs/export').then(() => {
      notify(ctx, 'info', 'Export requested from the backend.');
    });
  };

  return jsx(Page, {
    title: 'IOC list',
    actions: jsxs(Fragment, {
      children: [
        jsx(BackendBadge, { key: 'b', ctx }),
        jsx(Button, { key: 'e', variant: 'outline', onClick: exportIocs }, 'Export JSON'),
      ],
    }),
    children: jsxs(Fragment, {
      children: [
        jsxs('div', {
          key: 'ctl', style: { display: 'flex', gap: 8, marginBottom: 12, flexWrap: 'wrap' },
          children: [
            jsx(SearchField, {
              key: 'f', value: filter,
              onChange: (e) => setFilter(e.target.value),
              placeholder: 'Search terms...',
            }),
            jsx(Select, {
              key: 's', value: statusFilter,
              onChange: (e) => setStatusFilter(e.target.value),
              children: ['all', 'active', 'proposed', 'inactive', 'quarantined'].map((s) =>
                jsx('option', { key: s, value: s }, s)),
            }),
            jsx(Input, {
              key: 'n', value: newTerm, placeholder: 'Add term (goes to review)',
              onChange: (e) => setNewTerm(e.target.value),
              onKeyDown: (e) => { if (e.key === 'Enter') addTerm(); },
              style: { maxWidth: 260 },
            }),
            jsx(Button, { key: 'a', onClick: addTerm }, 'Propose term'),
            jsx(Button, {
              key: 'bi', variant: 'outline',
              onClick: () => setBulkOpen(!bulkOpen),
            }, 'Bulk import'),
          ],
        }),
        bulkOpen ? jsxs('div', {
          key: 'bulk', style: { marginBottom: 12 },
          children: [
            jsx('textarea', {
              key: 't', value: bulk, rows: 6, style: { width: '100%' },
              placeholder: 'One term per line. All enter as proposed.',
              onChange: (e) => setBulk(e.target.value),
            }),
            jsx(Button, { key: 'g', onClick: bulkImport }, 'Import as proposed'),
          ],
        }) : null,
        jsx(ScrollArea, {
          key: 'list', style: { maxHeight: 480 },
          children: shown.map((r) =>
            jsxs('div', {
              key: r.term,
              style: { display: 'flex', gap: 8, alignItems: 'center', padding: '4px 0' },
              children: [
                jsx(MaskedTerm, { key: 't', term: r.term, privateMode }),
                jsx(Badge, { key: 's' }, r.status),
                jsx('span', { key: 'c', style: { fontSize: 12 } }, r.category),
                jsxs('span', {
                  key: 'a', style: { marginLeft: 'auto', display: 'flex', gap: 4 },
                  children: [
                    jsx(Button, {
                      key: 'p', size: 'sm', variant: 'ghost',
                      onClick: () => setProvFor(provFor === r.term ? null : r.term),
                    }, 'Provenance'),
                    r.status === 'active'
                      ? jsx(Button, {
                          key: 'd', size: 'sm', variant: 'outline',
                          onClick: () => setDemoteFor(r.term),
                        }, 'Demote')
                      : null,
                  ],
                }),
              ],
            })),
        }),
        provFor ? jsx(Card, {
          key: 'prov', title: `Provenance: ${provFor}`, wide: true,
          children: (() => {
            const r = iocs.find((x) => x.term === provFor);
            if (!r) return null;
            return jsxs('div', {
              style: { fontSize: 12 },
              children: [
                jsx('div', { key: 's' }, `Source: ${r.provenance || 'unknown'}`),
                jsx('div', { key: 'a' }, `Added: ${r.added_utc || 'unknown'}`),
                jsx('div', { key: 'n' }, `Note: ${r.note || '—'}`),
              ],
            });
          })(),
        }) : null,
        jsx(Dialog, {
          key: 'dem', open: !!demoteFor,
          children: jsxs('div', {
            children: [
              jsx(DialogTitle, { key: 't' }, `Demote '${demoteFor}'?`),
              jsx('p', { key: 'p' }, 'The term becomes inactive. Terms are never deleted.'),
              jsx(Input, {
                key: 'i', value: demoteReason, placeholder: 'Reason (recorded)',
                onChange: (e) => setDemoteReason(e.target.value),
              }),
              jsxs('div', {
                key: 'b', style: { display: 'flex', gap: 8, marginTop: 8 },
                children: [
                  jsx(Button, { key: 'y', variant: 'destructive', onClick: demote }, 'Demote'),
                  jsx(Button, { key: 'n', variant: 'outline', onClick: () => setDemoteFor(null) }, 'Cancel'),
                ],
              }),
            ],
          }),
        }),
      ],
    }),
  });
}

// ---------------------------------------------------------------------------
// Research — /swarm-forensics/research. Watchlist + check-now + proposals.
// ---------------------------------------------------------------------------
function ResearchPage({ ctx }) {
  const settingsQ = useApi(ctx, 'settings', '/settings', 60000);
  const reviewQ = useApi(ctx, 'review', '/review', 15000);
  const [checking, setChecking] = useState(false);
  const [lastCheck, setLastCheck] = useState(null);

  const watch = ((settingsQ.data && settingsQ.data.research || {}).watch_urls || '')
    .split('\n').map((u) => u.trim()).filter(Boolean);
  const researchProps = ((reviewQ.data && reviewQ.data.entries) || [])
    .filter((e) => e.category === 'research');

  const checkNow = async () => {
    setChecking(true);
    const res = await apiPost(ctx, '/research/check', {});
    setChecking(false);
    if (res.error) {
      notify(ctx, 'error', `Research check refused: ${res.error}`);
      return;
    }
    setLastCheck(res);
    reviewQ.refetch();
    notify(ctx, 'info', `Research check: ${res.proposed} new proposals.`);
  };

  return jsx(Page, {
    title: 'Research',
    actions: jsxs(Fragment, {
      children: [
        jsx(BackendBadge, { key: 'b', ctx }),
        jsx(Button, { key: 'c', onClick: checkNow, disabled: checking },
          checking ? 'Checking...' : 'Check now'),
      ],
    }),
    children: jsxs(Fragment, {
      children: [
        jsx(Card, {
          key: 'w', title: 'Watchlist', wide: true,
          children: watch.length === 0
            ? jsx(EmptyState, {
                title: 'Watchlist empty',
                description: 'Add URLs in Settings → Research.',
              })
            : watch.map((u) =>
              jsxs('div', {
                key: u, style: { display: 'flex', gap: 8, padding: '4px 0' },
                children: [
                  jsx('span', { key: 'u', style: { fontSize: 12 } }, u),
                  lastCheck && lastCheck.changed_urls && lastCheck.changed_urls.includes(u)
                    ? jsx(Badge, { key: 'c' }, 'changed')
                    : jsx(Badge, { key: 'c', variant: 'outline' }, 'unchanged'),
                ],
              })),
        }),
        jsx(Card, {
          key: 'p', title: 'New findings — proposals', wide: true,
          children: researchProps.length === 0
            ? jsx(EmptyState, {
                title: 'No research proposals',
                description: 'Run "Check now". Findings arrive here first; nothing auto-promotes.',
              })
            : researchProps.map((e) =>
              jsxs('div', {
                key: e.id, style: { border: '1px solid', borderRadius: 8, padding: 8, marginBottom: 8 },
                children: [
                  jsxs('div', {
                    key: 'h', style: { display: 'flex', gap: 8, alignItems: 'center' },
                    children: [
                      jsx('code', { key: 't' }, e.term),
                      jsx('span', { key: 'p', style: { fontSize: 12 } }, `from ${e.provenance}`),
                    ],
                  }),
                  jsx('div', { key: 'b', style: { marginTop: 8 } },
                    jsx(CandidateCard, {
                      ctx, entryId: e.id, term: e.term, provenance: e.provenance,
                      ageDays: e.age_days, slaBreach: e.sla_breach,
                      onDecided: () => reviewQ.refetch(),
                    })),
                ],
              })),
        }),
      ],
    }),
  });
}

// ---------------------------------------------------------------------------
// Settings — /swarm-forensics/settings. Every tunable, prompt editors,
// firewall lock, danger zone. Writes go through PUT /settings and
// PUT /prompts/<name>. UI-only prefs mirror to ctx.storage
// (HERMES_DESKTOP.md §1 row: ctx.storage).
// ---------------------------------------------------------------------------
function NumField({ ctx, section, name, label, min, value, onSaved }) {
  const [v, setV] = useState(value);
  useEffect(() => setV(value), [value]);
  const save = async () => {
    const res = await apiPut(ctx, '/settings', { [section]: { [name]: v } });
    if (res.error) notify(ctx, 'error', res.error);
    else { notify(ctx, 'info', `${section}.${name} saved.`); if (onSaved) onSaved(); }
  };
  return jsxs('label', {
    style: { display: 'flex', flexDirection: 'column', gap: 4, minWidth: 200 },
    children: [
      label,
      jsxs('div', {
        key: 'r', style: { display: 'flex', gap: 8 },
        children: [
          jsx(Input, {
            key: 'i', type: 'number', value: v, min,
            onChange: (e) => setV(e.target.value),
          }),
          jsx(Button, { key: 's', size: 'sm', onClick: save }, 'Save'),
        ],
      }),
    ],
  });
}

function BoolField({ ctx, section, name, label, value, onSaved, locked, lockText }) {
  const [v, setV] = useState(value === 'true' || value === true);
  useEffect(() => setV(value === 'true' || value === true), [value]);
  const save = async (nv) => {
    setV(nv);
    const res = await apiPut(ctx, '/settings', { [section]: { [name]: nv ? 'true' : 'false' } });
    if (res.error) { notify(ctx, 'error', res.error); setV(!nv); }
    else { notify(ctx, 'info', `${section}.${name} saved.`); if (onSaved) onSaved(); }
  };
  return jsxs('label', {
    style: { display: 'flex', gap: 8, alignItems: 'center', opacity: locked ? 0.6 : 1 },
    children: [
      jsx(Switch, { key: 's', checked: v, disabled: !!locked, onChange: save }),
      jsx('span', { key: 'l' }, label),
      locked ? jsx('span', { key: 'x', style: { fontSize: 12 } }, lockText) : null,
    ],
  });
}

function PromptEditor({ ctx, name, title, description }) {
  const [text, setText] = useState('');
  const [source, setSource] = useState('default');
  const [loaded, setLoaded] = useState(false);
  const load = async () => {
    const d = await apiGet(ctx, `/prompts/${name}`);
    if (d && d.text !== undefined) {
      setText(d.text);
      setSource(d.source);
      setLoaded(true);
    }
  };
  useEffect(() => { load(); }, []);
  const save = async () => {
    const res = await apiPut(ctx, `/prompts/${name}`, { text });
    if (res.error) notify(ctx, 'error', res.error);
    else { notify(ctx, 'info', `${title} override saved.`); load(); }
  };
  const reset = async () => {
    const res = await apiPost(ctx, `/prompts/${name}/reset`, {});
    if (res.error) notify(ctx, 'error', res.error);
    else { notify(ctx, 'info', `${title} reset to default.`); load(); }
  };
  if (!loaded) return null;
  return jsx(Card, {
    title: `${title} (${source})`, wide: true,
    children: jsxs('div', {
      style: { display: 'flex', flexDirection: 'column', gap: 8 },
      children: [
        jsx('div', { key: 'd', style: { fontSize: 12 } }, description),
        jsx('textarea', {
          key: 't', value: text, rows: 14,
          style: { width: '100%', fontFamily: 'monospace', fontSize: 12 },
          onChange: (e) => setText(e.target.value),
        }),
        jsxs('div', {
          key: 'b', style: { display: 'flex', gap: 8 },
          children: [
            jsx(Button, { key: 's', onClick: save }, 'Save override'),
            jsx(Button, { key: 'r', variant: 'outline', onClick: reset }, 'Reset to default'),
          ],
        }),
      ],
    }),
  });
}

// Install link [DOC]: website/docs/developer-guide/desktop-plugin-sdk.md,
// section "Distributing with an install link". Deep links never
// auto-install: the app shows a confirmation dialog (repo id, source
// links, a probe of what the repo ships) and the user picks
// components first. Repo id below follows the task brief; the hunt
// repo moved to christopherwoodall/silent-locus on 2026-09-28, so
// confirm the repo id before publishing this link. See report.
const INSTALL_LINK =
  'hermes://plugin/install?repo=christopherwoodall/swarm-forensics/pug-research/hermes-plugin/skills/swarm-forensics&enable=1';

function AboutCard({ ctx }) {
  return jsx(Card, {
    title: 'About — install and permissions', wide: true,
    children: jsxs('div', {
      style: { display: 'flex', flexDirection: 'column', gap: 8, fontSize: 13 },
      children: [
        jsxs('div', {
          key: 'l', style: { display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' },
          children: [
            jsx('strong', { key: 'h' }, 'Install in Hermes:'),
            jsx('a', { key: 'a', href: INSTALL_LINK }, 'hermes://plugin/install?...'),
            jsx(CopyButton, { key: 'c', value: INSTALL_LINK }),
          ],
        }),
        jsx('div', { key: 'e' },
          'enable=1 follows the doc example, but the link never auto-installs. ' +
          'The app shows a confirm-first dialog (repo identity, source links, ' +
          'ship-probe) and you pick components. This plugin ships ' +
          'defaultEnabled: false: it inventories in Capabilities → Plugins ' +
          'and stays off until you toggle it. The Python backend loads only ' +
          'when the plugin is also in plugins.enabled in config.yaml — ' +
          'two separate toggles, both documented in the SDK doc.'),
        jsx('div', { key: 'p' },
          'What this plugin requests: read-only network egress to the ' +
          'allowlisted public sources (urlquery.net, web.archive.org, ' +
          'arquivo.pt, transluce.org); local working state under state/ ' +
          '(hits, IOC list, review log, chat log); plugin-namespaced UI ' +
          'prefs (hermes.plugin.swarm-forensics.*). No credentials, no ' +
          'authenticated APIs, no posting.'),
        jsx('div', { key: 's' },
          'No silent installs, ever. No autonomous scanning, ever: every ' +
          'hunt starts from an explicit human action in this UI or chat.'),
      ],
    }),
  });
}

function SettingsPage({ ctx }) {
  const settingsQ = useApi(ctx, 'settings', '/settings', 30000);
  const [confirmReset, setConfirmReset] = useState(false);
  const s = settingsQ.data || {};
  const reload = () => settingsQ.refetch();

  const watchUrls = (s.research || {}).watch_urls || '';
  const exclusion = (s.ioc || {}).exclusion_list || '';
  const saveWatch = async (v) => {
    const res = await apiPut(ctx, '/settings', { research: { watch_urls: v } });
    if (res.error) notify(ctx, 'error', res.error);
    else { notify(ctx, 'info', 'Watchlist saved.'); reload(); }
  };
  const saveExclusion = async (v) => {
    const res = await apiPut(ctx, '/settings', { ioc: { exclusion_list: v } });
    if (res.error) notify(ctx, 'error', res.error);
    else { notify(ctx, 'info', 'Exclusion list saved.'); reload(); }
  };
  const resetDefaults = async () => {
    const res = await apiPost(ctx, '/settings/reset', {});
    if (res.error) notify(ctx, 'error', res.error);
    else { notify(ctx, 'info', 'Settings reset to defaults.'); reload(); }
  };
  const exportDiag = async () => {
    await apiGet(ctx, '/diagnostics');
    notify(ctx, 'info', 'Diagnostics bundle requested from the backend.');
  };

  const fwMode = (s.safety || {}).firewall_mode
    || (s.firewall || {}).firewall_mode || 'advisory';
  const chatMode = (s._chat_mode || {}).mode || 'rule';

  return jsx(Page, {
    title: 'Settings',
    actions: jsx(BackendBadge, { ctx }),
    children: jsxs(Fragment, {
      children: [
        jsx(Card, {
          key: 'hunt', title: 'Hunt defaults', wide: true,
          children: jsxs(Fragment, {
            children: [
              jsx('div', {
                key: 'note',
                style: { color: 'var(--ui-text-tertiary)', fontSize: '0.8rem', marginBottom: 8 },
                children: 'Used when a hunt names no sources or cap (CLI and API). The Hunt form always sets them explicitly.',
              }),
              jsxs('div', {
                key: 'f', style: { display: 'flex', gap: 16, flexWrap: 'wrap' },
                children: [
                  jsx(TextField, {
                    key: 'a', ctx, section: 'hunt', name: 'default_sources',
                    label: 'Default sources (comma list)',
                    value: (s.hunt || {}).default_sources, onSaved: reload,
                  }),
                  jsx(NumField, {
                    key: 'b', ctx, section: 'hunt', name: 'default_cap',
                    label: 'Default cap (0 = max_terms_per_sweep)', min: 0,
                    value: (s.hunt || {}).default_cap, onSaved: reload,
                  }),
                ],
              }),
            ],
          }),
        }),
        jsx(Card, {
          key: 'src', title: 'Sources', wide: true,
          children: jsxs('div', {
            style: { display: 'flex', flexDirection: 'column', gap: 12 },
            children: [
              jsxs('div', {
                key: 't', style: { display: 'flex', gap: 16, flexWrap: 'wrap' },
                children: ['urlquery', 'cdx', 'arquivo'].map((src) =>
                  jsx(BoolField, {
                    key: src, ctx, section: 'sources', name: `${src}_enabled`,
                    label: src, value: (s.sources || {})[`${src}_enabled`],
                    onSaved: reload,
                  })),
              }),
              jsxs('div', {
                key: 'n', style: { display: 'flex', gap: 16, flexWrap: 'wrap' },
                children: [
                  jsx(NumField, {
                    key: 'd', ctx, section: 'sources', name: 'request_delay_seconds',
                    label: 'Request delay (seconds, min 1)', min: 1,
                    value: (s.sources || {}).request_delay_seconds, onSaved: reload,
                  }),
                  jsx(NumField, {
                    key: 'r', ctx, section: 'sources', name: 'max_results_per_query',
                    label: 'Max results per query', min: 1,
                    value: (s.sources || {}).max_results_per_query, onSaved: reload,
                  }),
                  jsx(NumField, {
                    key: 'c', ctx, section: 'sources', name: 'max_terms_per_sweep',
                    label: 'Sweep cap (terms per hunt)', min: 1,
                    value: (s.sources || {}).max_terms_per_sweep, onSaved: reload,
                  }),
                ],
              }),
              jsxs('label', {
                key: 'u', style: { display: 'flex', flexDirection: 'column', gap: 4 },
                children: [
                  'User agent (contact required — urlquery is a free community service)',
                  jsx(UserAgentField, { key: 'f', ctx, value: (s.sources || {}).user_agent, onSaved: reload }),
                ],
              }),
            ],
          }),
        }),
        jsx(Card, {
          key: 'safe', title: 'Safety', wide: true,
          children: jsxs('div', {
            style: { display: 'flex', flexDirection: 'column', gap: 12 },
            children: [
              jsx(BoolField, {
                key: 'p', ctx, section: 'safety', name: 'private_mode',
                label: 'Private mode — mask watch-term strings in the UI',
                value: (s.safety || {}).private_mode, onSaved: reload,
              }),
              jsxs('div', {
                key: 'fw',
                children: [
                  jsx('div', { key: 'l', style: { marginBottom: 4 } },
                    `Firewall mode: ${fwMode} (LOCKED)`),
                  jsx('div', { key: 'x', style: { fontSize: 12 } },
                    'The judge reads attacker-controlled evidence. "Enforcing" stays disabled until an injection-resistance eval passes. The backend rejects any other value with this explanation.'),
                  jsx(SegmentedControl, {
                    key: 'g',
                    value: fwMode,
                    disabled: true,
                    options: [
                      { value: 'off', label: 'Off' },
                      { value: 'advisory', label: 'Advisory' },
                    ],
                  }),
                ],
              }),
              jsx(AlertLevelField, { key: 'al', ctx, value: (s.safety || {}).alert_on_claim_level, onSaved: reload }),
              jsx(ExclusionEditor, { key: 'ex', initial: exclusion, onSave: saveExclusion }),
            ],
          }),
        }),
        jsx(Card, {
          key: 'chat', title: 'Chat brain', wide: true,
          children: jsxs('div', {
            style: { display: 'flex', flexDirection: 'column', gap: 12 },
            children: [
              jsx('div', { key: 'm', style: { fontSize: 12 } },
                `Active path: ${chatMode}. Rule-based works with zero model dependency. ` +
                'The optional model path only rephrases replies; actions stay rule-based.'),
              jsx(BoolField, {
                key: 'e', ctx, section: 'chat', name: 'model_enabled',
                label: 'Enable optional model path', value: (s.chat || {}).model_enabled,
                onSaved: reload,
              }),
              jsx(TextField, {
                key: 'ep', ctx, section: 'chat', name: 'endpoint',
                label: 'Model endpoint (empty disables)', value: (s.chat || {}).endpoint,
                onSaved: reload,
              }),
              jsx(TextField, {
                key: 'mo', ctx, section: 'chat', name: 'model',
                label: 'Model id (pinned)', value: (s.chat || {}).model,
                onSaved: reload,
              }),
              jsx('div', { key: 'k', style: { fontSize: 12 } },
                `API key comes from env var ${(s.chat || {}).api_key_env || 'SWARM_FORENSICS_CHAT_KEY'}. Never in config, never logged.`),
            ],
          }),
        }),
        jsx(Card, {
          key: 'res', title: 'Research', wide: true,
          children: jsx(WatchlistEditor, { initial: watchUrls, onSave: saveWatch }),
        }),
        jsx(PromptEditor, {
          key: 'pj', ctx, name: 'judge', title: 'Firewall judge prompt',
          description: 'System prompt for the optional firewall judge. Advisory only; it never promotes a term.',
        }),
        jsx(PromptEditor, {
          key: 'pc', ctx, name: 'chat_system', title: 'Chat system prompt',
          description: 'System prompt for the optional chat model path. The rule-based responder does not use it.',
        }),
        jsx(PromptEditor, {
          key: 'ph', ctx, name: 'hunt_templates', title: 'Hunt query templates',
          description: 'Query templates the scanner builds hunts from. An override shadows the shipped references file.',
        }),
        jsx(AboutCard, { key: 'about', ctx }),
        jsx(Card, {
          key: 'dz', title: 'Danger zone', wide: true,          children: jsxs('div', {
            style: { display: 'flex', gap: 8, flexWrap: 'wrap' },
            children: [
              jsx(Button, {
                key: 'r', variant: 'destructive',
                onClick: () => setConfirmReset(true),
              }, 'Reset settings to defaults'),
              jsx(Button, { key: 'd', variant: 'outline', onClick: exportDiag }, 'Export diagnostics'),
            ],
          }),
        }),
        jsx(ConfirmDialog, {
          key: 'cd',
          open: confirmReset,
          title: 'Reset all settings?',
          description: 'Restores config.example.ini defaults. State and prompt overrides are kept.',
          onConfirm: () => { setConfirmReset(false); resetDefaults(); },
          onCancel: () => setConfirmReset(false),
        }),
      ],
    }),
  });
}

function UserAgentField({ ctx, value, onSaved }) {
  return jsx(TextField, { ctx, section: 'sources', name: 'user_agent', value, onSaved });
}
function TextField({ ctx, section, name, label, value, onSaved }) {
  const [v, setV] = useState(value || '');
  useEffect(() => setV(value || ''), [value]);
  const save = async () => {
    const res = await apiPut(ctx, '/settings', { [section]: { [name]: v } });
    if (res.error) notify(ctx, 'error', res.error);
    else { notify(ctx, 'info', 'Saved.'); if (onSaved) onSaved(); }
  };
  return jsxs('div', {
    style: { display: 'flex', gap: 8 },
    children: [
      jsx(Input, { key: 'i', value: v, onChange: (e) => setV(e.target.value), placeholder: label || '' }),
      jsx(Button, { key: 's', size: 'sm', onClick: save }, 'Save'),
    ],
  });
}
function AlertLevelField({ ctx, value, onSaved }) {
  const [v, setV] = useState(value || 'L3');
  useEffect(() => setV(value || 'L3'), [value]);
  const save = async () => {
    const res = await apiPut(ctx, '/settings', { safety: { alert_on_claim_level: v } });
    if (res.error) notify(ctx, 'error', res.error);
    else { notify(ctx, 'info', 'Alert threshold saved.'); if (onSaved) onSaved(); }
  };
  return jsxs('label', {
    style: { display: 'flex', flexDirection: 'column', gap: 4 },
    children: [
      'Toast threshold (high-claim hits only; the dashboard is the inbox)',
      jsxs('div', {
        key: 'r', style: { display: 'flex', gap: 8 },
        children: [
          jsx(SegmentedControl, {
            key: 'g', value: v,
            options: CLAIM_LEVELS.map((l) => ({ value: l, label: l })),
            onChange: setV,
          }),
          jsx(Button, { key: 's', size: 'sm', onClick: save }, 'Save'),
        ],
      }),
    ],
  });
}
function WatchlistEditor({ initial, onSave }) {
  const [v, setV] = useState(initial);
  useEffect(() => setV(initial), [initial]);
  return jsxs('div', {
    style: { display: 'flex', flexDirection: 'column', gap: 8 },
    children: [
      jsx('div', { key: 'd', style: { fontSize: 12 } }, 'One URL per line.'),
      jsx('textarea', {
        key: 't', value: v, rows: 5, style: { width: '100%' },
        onChange: (e) => setV(e.target.value),
      }),
      jsx('div', { key: 'b' }, jsx(Button, { size: 'sm', onClick: () => onSave(v) }, 'Save watchlist')),
    ],
  });
}
function ExclusionEditor({ initial, onSave }) {
  const [v, setV] = useState(initial);
  useEffect(() => setV(initial), [initial]);
  return jsxs('label', {
    style: { display: 'flex', flexDirection: 'column', gap: 4 },
    children: [
      'Exclusion list (one pattern per line; scanner skips these)',
      jsx('textarea', {
        key: 't', value: v, rows: 3, style: { width: '100%' },
        onChange: (e) => setV(e.target.value),
      }),
      jsx('div', { key: 'b' }, jsx(Button, { size: 'sm', onClick: () => onSave(v) }, 'Save exclusions')),
    ],
  });
}

// ---------------------------------------------------------------------------
// Status-bar chip — statusBar.right (HERMES_DESKTOP.md §1 row).
// Always-visible answer to "is the hunter running right now?"
// Grey when paused — unmissable. Click navigates to the dashboard.
// ---------------------------------------------------------------------------
function StatusChip({ ctx }) {
  const [storeState] = useStore();
  const diag = useApi(ctx, 'diag', '/diagnostics', 15000);
  const jobsQ = useApi(ctx, 'jobs-chip', '/jobs', 10000);
  if (!storeState.uiEnabled) {
    return jsx('span', { title: 'Swarm Forensics UI hidden (Appearance)' }, '○');
  }
  const paused = diag.data && diag.data.paused;
  const jobs = (jobsQ.data && jobsQ.data.jobs) || [];
  const running = jobs.some((j) => j.status === 'running' || j.status === 'queued');
  const state = !diag.data ? 'unknown' : paused ? 'paused' : running ? 'running' : 'idle';
  const tip = !diag.data
    ? 'swarm-forensics: backend disconnected'
    : `swarm-forensics: ${state}` +
      (jobs[0] ? ` — last hunt ${jobs[0].job_id} (${jobs[0].status}, ${jobs[0].new_hits || 0} hits)` : '');
  return jsx('button', {
    onClick: () => navigate(ctx, '/swarm-forensics'),
    title: tip,
    style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' },
    children: jsxs(Fragment, {
      children: [
        jsx(StatusDot, { key: 'd', color: stateColor(state) }),
        jsx('span', { key: 't' }, 'swarm-forensics'),
      ],
    }),
  });
}

// ---------------------------------------------------------------------------
// Appearance extras — APPEARANCE_AREAS.extra (HERMES_DESKTOP.md §1 row).
// Compact trio appended to Settings → Appearance. Full settings stay
// on the Settings page (Gap 2).
// ---------------------------------------------------------------------------
function AppearanceExtra({ ctx }) {
  const [storeState, setStore] = useStore();
  const diag = useApi(ctx, 'diag', '/diagnostics', 15000);
  const settingsQ = useApi(ctx, 'settings', '/settings', 30000);
  const [cap, setCap] = useState(null);
  const paused = diag.data && diag.data.paused;
  const cur = settingsQ.data && settingsQ.data.sources &&
    settingsQ.data.sources.max_terms_per_sweep;

  const togglePause = async () => {
    await apiPost(ctx, '/settings/pause', { paused: !paused });
    diag.refetch();
  };
  const saveCap = async () => {
    if (cap === null) return;
    await apiPut(ctx, '/settings', { sources: { max_terms_per_sweep: String(cap) } });
    settingsQ.refetch();
    setCap(null);
  };

  return jsxs('div', {
    style: { display: 'flex', flexDirection: 'column', gap: 8 },
    children: [
      jsx('strong', { key: 'h' }, 'Swarm Forensics'),
      jsxs('label', {
        key: 'e', style: { display: 'flex', gap: 8, alignItems: 'center' },
        children: [
          // [INF]: no documented API toggles plugin enablement at
          // runtime. This switch dims the plugin UI surface (chip,
          // toasts) via a local pref. The Capabilities toggle stays
          // the real enable switch.
          jsx(Switch, {
            key: 's', checked: storeState.uiEnabled,
            onChange: (v) => {
              setStore({ uiEnabled: !!v });
              if (ctx.storage && ctx.storage.set) {
                ctx.storage.set('uiEnabled', !!v); // §1 row: ctx.storage
              }
            },
          }),
          'Enable UI surface',
        ],
      }),
      jsxs('label', {
        key: 'p', style: { display: 'flex', gap: 8, alignItems: 'center' },
        children: [
          jsx(Switch, { key: 's', checked: !paused, onChange: togglePause }),
          paused ? 'Hunting paused' : 'Hunting live',
        ],
      }),
      jsxs('label', {
        key: 'c', style: { display: 'flex', gap: 8, alignItems: 'center' },
        children: [
          'Sweep cap',
          jsx(Input, {
            key: 'i', type: 'number', min: 1,
            value: cap === null ? (cur || '') : cap,
            onChange: (e) => setCap(e.target.value),
            style: { width: 80 },
          }),
          jsx(Button, { key: 's', size: 'sm', onClick: saveCap }, 'Set'),
        ],
      }),
    ],
  });
}

// ---------------------------------------------------------------------------
// Palette + keybind helpers. Each command maps to the same backend
// endpoints as the GUI buttons: two faces, one state.
// ---------------------------------------------------------------------------
async function stopRunningHunt(ctx) {
  const d = await apiGet(ctx, '/jobs');
  const jobs = (d && d.jobs) || [];
  const running = jobs.find((j) => j.status === 'running' || j.status === 'queued');
  if (!running) {
    notify(ctx, 'info', 'No hunt is running.');
    return;
  }
  await apiPost(ctx, '/hunt/stop', { job_id: running.job_id });
  notify(ctx, 'info', `Hunt ${running.job_id} cancelled.`);
}

async function togglePause(ctx) {
  const d = await apiGet(ctx, '/diagnostics');
  const paused = d && d.paused;
  await apiPost(ctx, '/settings/pause', { paused: !paused });
  notify(ctx, 'info', paused ? 'Hunting resumed.' : 'All hunting paused.');
}

async function reviewDecideSelected(ctx, verdict) {
  const id = store.state.selectedReviewId;
  if (!id) {
    notify(ctx, 'info', 'No review card selected. Click a card first.');
    return;
  }
  if (verdict === 'narrow') {
    store.set({ pendingNarrowId: id });
    navigate(ctx, '/swarm-forensics/review');
    notify(ctx, 'info', `Narrow '${id}': use the Narrow button on its card.`);
    return;
  }
  const res = await apiPost(ctx, '/review/decision', { id, verdict });
  if (res.error) notify(ctx, 'error', `Decision failed: ${res.error}`);
  else notify(ctx, 'info', `${id}: ${verdict}.`);
}

// ---------------------------------------------------------------------------
// Case management (Worker-5). Routes /swarm-forensics/cases and
// /swarm-forensics/graph. The case DB is the analyst's workspace: entities
// (trace, agent, swarm, collection), links, and extracted indicators.
// Extracted indicators are NOT IOCs: nothing here promotes to the
// IOC list; promotion stays a human review-queue decision.
// ---------------------------------------------------------------------------
const CASE_TYPES = ['trace', 'agent', 'swarm', 'collection'];
const CASE_REL_KINDS = ['trace_of', 'member_of', 'part_of', 'related'];
const CASE_TYPE_COLORS = {
  trace: '#58a6ff', agent: '#3fb950', swarm: '#d29922', collection: '#bc8cff',
};

function TypeBadge({ type }) {
  return jsx(Badge, { style: { borderColor: CASE_TYPE_COLORS[type] || '#888' } }, type);
}

function EntityDetail({ ctx, entityId, entities, onChanged, onSelect }) {
  const [detail, setDetail] = useState(null);
  const [linkTarget, setLinkTarget] = useState('');
  const [linkRel, setLinkRel] = useState('related');
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [editLabel, setEditLabel] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!entityId) { setDetail(null); return undefined; }
    let live = true;
    apiGet(ctx, '/cases/entities/' + encodeURIComponent(entityId)).then((d) => {
      if (!live) return;
      if (d.error) { setDetail(null); return; }
      setDetail(d);
      setEditLabel(d.entity.label);
      setConfirmDelete(false);
    });
    return () => { live = false; };
  }, [entityId]);

  if (!entityId) {
    return jsx(EmptyState, {
      title: 'No entity selected',
      description: 'Pick an entity from the list, or a node in the graph.',
    });
  }
  if (!detail) return jsx('div', null, 'Loading…');
  const ent = detail.entity;

  const saveLabel = async () => {
    const label = editLabel.trim();
    if (!label || label === ent.label) return;
    setSaving(true);
    const res = await apiPut(ctx, '/cases/entities/' + encodeURIComponent(entityId),
      { label });
    setSaving(false);
    if (res.error) notify(ctx, 'error', `Save failed: ${res.error}`);
    else { setDetail({ ...detail, entity: res.entity }); onChanged && onChanged(); }
  };
  const addLink = async () => {
    if (!linkTarget || linkTarget === entityId) return;
    const res = await apiPost(ctx, '/cases/link',
      { from_id: entityId, to_id: linkTarget, rel: linkRel });
    if (res.error) notify(ctx, 'error', `Link failed: ${res.error}`);
    else {
      notify(ctx, 'info', 'Linked.');
      setLinkTarget('');
      const d = await apiGet(ctx, '/cases/entities/' + encodeURIComponent(entityId));
      if (!d.error) setDetail(d);
      onChanged && onChanged();
    }
  };
  const removeLink = async (linkId) => {
    const res = await apiDelete(ctx, '/cases/link/' + encodeURIComponent(linkId));
    if (res.error || !res.deleted) notify(ctx, 'error', 'Unlink failed.');
    else {
      const d = await apiGet(ctx, '/cases/entities/' + encodeURIComponent(entityId));
      if (!d.error) setDetail(d);
      onChanged && onChanged();
    }
  };
  const deleteEntity = async () => {
    const res = await apiDelete(ctx, '/cases/entities/' + encodeURIComponent(entityId));
    if (res.error || !res.deleted) notify(ctx, 'error', 'Delete failed.');
    else {
      notify(ctx, 'info', 'Entity deleted (its links and indicators went with it).');
      onChanged && onChanged(true);
    }
  };

  const linkTargets = (entities || []).filter((e) => e.id !== entityId);
  return jsxs('div', {
    children: [
      jsxs('div', {
        key: 'head', style: { display: 'flex', gap: 8, alignItems: 'center', marginBottom: 8 },
        children: [
          jsx(TypeBadge, { key: 'b', type: ent.type }),
          jsx('strong', { key: 'l' }, ent.label),
          jsx('span', { key: 'p', style: { fontSize: 12, opacity: 0.7 } },
            ent.provenance ? `provenance: ${ent.provenance}` : 'no provenance'),
        ],
      }),
      jsxs('div', {
        key: 'rename', style: { display: 'flex', gap: 8, marginBottom: 12 },
        children: [
          jsx(Input, {
            key: 'i', value: editLabel,
            onChange: (e) => setEditLabel(e.target.value),
            onKeyDown: (e) => { if (e.key === 'Enter') saveLabel(); },
            style: { maxWidth: 300 },
          }),
          jsx(Button, { key: 's', size: 'sm', onClick: saveLabel, disabled: saving }, 'Rename'),
        ],
      }),
      ent.data && ent.data.job_id ? jsx('div', {
        key: 'job', style: { fontSize: 12, marginBottom: 8 },
      }, `Hunt job: ${ent.data.job_id}`) : null,
      jsx('h4', { key: 'ih', style: { margin: '8px 0 4px' } },
        `Indicators (${detail.indicators.length})`),
      detail.indicators.length
        ? jsx('div', {
          key: 'il', style: { fontSize: 12, marginBottom: 8 },
          children: detail.indicators.map((ind, i) =>
            jsxs('div', {
              key: i, style: { display: 'flex', gap: 8, padding: '2px 0' },
              children: [
                jsx(Badge, { key: 'k' }, ind.kind),
                jsx('span', {
                  key: 'v', style: { wordBreak: 'break-all', fontFamily: 'monospace' },
                }, ind.value),
              ],
            })),
        })
        : jsx('p', { key: 'in', style: { fontSize: 12, opacity: 0.7 } },
          'No indicators. Traces gain indicators from extraction on save.'),
      jsx('p', {
        key: 'iw', style: { fontSize: 11, opacity: 0.7, marginBottom: 12 },
      }, 'Indicators are working notes, not IOCs. They never reach the IOC list.'),
      jsx('h4', { key: 'lh', style: { margin: '8px 0 4px' } },
        `Links (${detail.links.length})`),
      detail.links.length
        ? jsx('div', {
          key: 'll', style: { fontSize: 12, marginBottom: 8 },
          children: detail.links.map((l) => {
            const otherId = l.from_id === entityId ? l.to_id : l.from_id;
            const other = (detail.adjacent || {})[otherId];
            const label = other ? other.label : otherId.slice(0, 8);
            const dir = l.from_id === entityId ? '→' : '←';
            return jsxs('div', {
              key: l.id, style: { display: 'flex', gap: 8, alignItems: 'center', padding: '2px 0' },
              children: [
                jsx('span', { key: 'd' }, dir),
                jsx('button', {
                  key: 'o', onClick: () => onSelect && onSelect(otherId),
                  style: {
                    background: 'none', border: 'none', color: 'var(--swarm-forensics-link, #58a6ff)',
                    cursor: 'pointer', padding: 0, fontSize: 12, textDecoration: 'underline',
                  },
                }, label),
                jsx(Badge, { key: 'r' }, l.rel),
                jsx(Button, {
                  key: 'u', size: 'sm', variant: 'ghost', onClick: () => removeLink(l.id),
                }, 'Unlink'),
              ],
            });
          }),
        })
        : jsx('p', { key: 'ln', style: { fontSize: 12, opacity: 0.7 } }, 'No links yet.'),
      jsxs('div', {
        key: 'add', style: { display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' },
        children: [
          jsx(Select, {
            key: 't', value: linkTarget,
            onChange: (e) => setLinkTarget(e.target.value),
            children: [
              jsx('option', { key: 'e', value: '' }, 'Link to…'),
              ...linkTargets.map((e) =>
                jsx('option', { key: e.id, value: e.id }, `${e.label} (${e.type})`)),
            ],
          }),
          jsx(Select, {
            key: 'r', value: linkRel,
            onChange: (e) => setLinkRel(e.target.value),
            children: CASE_REL_KINDS.map((r) =>
              jsx('option', { key: r, value: r }, r)),
          }),
          jsx(Button, { key: 'b', size: 'sm', onClick: addLink }, 'Link'),
        ],
      }),
      confirmDelete
        ? jsxs('div', {
          key: 'cd', style: { display: 'flex', gap: 8, alignItems: 'center' },
          children: [
            jsx('span', { key: 'w', style: { fontSize: 12 } },
              'Delete this entity, its links, and its indicators?'),
            jsx(Button, { key: 'y', size: 'sm', variant: 'destructive', onClick: deleteEntity }, 'Delete'),
            jsx(Button, { key: 'n', size: 'sm', variant: 'outline', onClick: () => setConfirmDelete(false) }, 'Cancel'),
          ],
        })
        : jsx(Button, {
          key: 'del', size: 'sm', variant: 'destructive',
          onClick: () => setConfirmDelete(true),
        }, 'Delete entity'),
    ],
  });
}

function NewEntityDialog({ ctx, open, onClose, onSaved }) {
  const [type, setType] = useState('trace');
  const [label, setLabel] = useState('');
  const [provenance, setProvenance] = useState('');
  const [traceText, setTraceText] = useState('');
  const [jobId, setJobId] = useState('');
  const [preview, setPreview] = useState(null);
  const [saving, setSaving] = useState(false);

  const reset = () => {
    setType('trace'); setLabel(''); setProvenance('');
    setTraceText(''); setJobId(''); setPreview(null);
  };
  const previewIndicators = async () => {
    const res = await apiPost(ctx, '/cases/extract', { trace_text: traceText });
    if (res.error) notify(ctx, 'error', `Preview failed: ${res.error}`);
    else setPreview(res.indicators);
  };
  const save = async () => {
    if (!label.trim()) { notify(ctx, 'error', 'Label is required.'); return; }
    setSaving(true);
    const body = { type, label: label.trim(), provenance };
    if (type === 'trace') {
      body.trace_text = traceText;
      if (jobId.trim()) body.job_id = jobId.trim();
    }
    const res = await apiPost(ctx, '/cases/entities', body);
    setSaving(false);
    if (res.error) { notify(ctx, 'error', `Save failed: ${res.error}`); return; }
    notify(ctx, 'info', `'${label.trim()}' saved.`);
    reset();
    onSaved(res.entity);
  };

  return jsx(Dialog, {
    open,
    children: jsxs('div', {
      children: [
        jsx(DialogTitle, { key: 't' }, 'New case entity'),
        jsxs('div', {
          key: 'f', style: { display: 'flex', flexDirection: 'column', gap: 8, marginTop: 8 },
          children: [
            jsx(Select, {
              key: 'ty', value: type, onChange: (e) => setType(e.target.value),
              children: CASE_TYPES.map((t) =>
                jsx('option', { key: t, value: t }, t)),
            }),
            jsx(Input, {
              key: 'l', value: label, placeholder: 'Label (required)',
              onChange: (e) => setLabel(e.target.value),
            }),
            jsx(Input, {
              key: 'p', value: provenance, placeholder: 'Provenance (optional)',
              onChange: (e) => setProvenance(e.target.value),
            }),
            type === 'trace' ? jsx('textarea', {
              key: 'tt', value: traceText, rows: 5, style: { width: '100%' },
              placeholder: 'Trace text. Saving runs indicator extraction (regex, offline).',
              onChange: (e) => setTraceText(e.target.value),
            }) : null,
            type === 'trace' ? jsx(Input, {
              key: 'j', value: jobId, placeholder: 'Hunt job id (optional)',
              onChange: (e) => setJobId(e.target.value),
            }) : null,
            type === 'trace' && traceText.trim() ? jsx(Button, {
              key: 'pv', variant: 'outline', onClick: previewIndicators,
            }, 'Preview indicators') : null,
            preview ? jsx('div', {
              key: 'pvw', style: { fontSize: 12, maxHeight: 160, overflow: 'auto' },
              children: preview.length
                ? preview.map((ind, i) =>
                  jsxs('div', {
                    key: i, style: { display: 'flex', gap: 8 },
                    children: [
                      jsx(Badge, { key: 'k' }, ind.kind),
                      jsx('span', { key: 'v', style: { fontFamily: 'monospace' } }, ind.value),
                    ],
                  }))
                : jsx('span', { key: 'n' }, 'No indicators found in this text.'),
            }) : null,
          ],
        }),
        jsxs('div', {
          key: 'b', style: { display: 'flex', gap: 8, marginTop: 12 },
          children: [
            jsx(Button, { key: 's', onClick: save, disabled: saving }, 'Save entity'),
            jsx(Button, {
              key: 'c', variant: 'outline',
              onClick: () => { reset(); onClose(); },
            }, 'Cancel'),
          ],
        }),
      ],
    }),
  });
}

function CasesPage({ ctx }) {
  const entsQ = useApi(ctx, 'case-entities', '/cases/entities', 15000);
  const [typeFilter, setTypeFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [selectedId, setSelectedId] = useState(null);
  const [newOpen, setNewOpen] = useState(false);
  const [s, setS] = useStore();

  // Palette command "New case entity…" sets the flag, then navigates here.
  useEffect(() => {
    if (s.casesNewOpen) { setNewOpen(true); setS({ casesNewOpen: false }); }
  }, []);

  const entities = (entsQ.data && entsQ.data.entities) || [];
  const shown = entities.filter((e) =>
    (typeFilter === 'all' || e.type === typeFilter) &&
    (!search || e.label.toLowerCase().includes(search.toLowerCase())));

  const refresh = (deleted) => {
    entsQ.refetch();
    if (deleted) setSelectedId(null);
  };

  return jsx(Page, {
    title: 'Cases',
    actions: jsxs(Fragment, {
      children: [
        jsx(BackendBadge, { key: 'b', ctx }),
        jsx(Button, { key: 'n', onClick: () => setNewOpen(true) }, 'New entity'),
      ],
    }),
    children: jsxs(Fragment, {
      children: [
        jsx('p', {
          key: 'note', style: { fontSize: 12, opacity: 0.75, marginTop: 0 },
        }, 'The analyst workspace. Entities, links, and extracted indicators live here. ' +
          'Extracted indicators are not IOCs: promotion to the IOC list needs the review queue.'),
        jsxs('div', {
          key: 'ctl', style: { display: 'flex', gap: 8, marginBottom: 12, flexWrap: 'wrap' },
          children: [
            jsx(SearchField, {
              key: 'f', value: search,
              onChange: (e) => setSearch(e.target.value),
              placeholder: 'Search labels…',
            }),
            jsx(Select, {
              key: 't', value: typeFilter,
              onChange: (e) => setTypeFilter(e.target.value),
              children: ['all', ...CASE_TYPES].map((t) =>
                jsx('option', { key: t, value: t }, t)),
            }),
          ],
        }),
        jsxs('div', {
          key: 'cols', style: { display: 'flex', gap: 16, alignItems: 'flex-start' },
          children: [
            jsx(ScrollArea, {
              key: 'list', style: { maxHeight: 560, flex: '1 1 40%', minWidth: 240 },
              children: shown.length
                ? shown.map((e) =>
                  jsxs('button', {
                    key: e.id,
                    onClick: () => setSelectedId(e.id),
                    style: {
                      display: 'flex', gap: 8, alignItems: 'center', width: '100%',
                      padding: '6px 8px', marginBottom: 4, textAlign: 'left',
                      border: '1px solid var(--swarm-forensics-border, transparent)',
                      borderRadius: 6, cursor: 'pointer',
                      background: e.id === selectedId
                        ? 'var(--swarm-forensics-selected, rgba(88,166,255,0.12))' : 'transparent',
                    },
                    children: [
                      jsx(TypeBadge, { key: 'b', type: e.type }),
                      jsx('span', { key: 'l' }, e.label),
                    ],
                  }))
                : jsx(EmptyState, {
                  key: 'e', title: 'No entities yet',
                  description: 'Create the first one with “New entity”.',
                }),
            }),
            jsx('div', {
              key: 'detail', style: { flex: '1 1 60%', minWidth: 280 },
              children: jsx(EntityDetail, {
                ctx, entityId: selectedId, entities,
                onChanged: refresh, onSelect: setSelectedId,
              }),
            }),
          ],
        }),
        jsx(NewEntityDialog, {
          key: 'dlg', ctx, open: newOpen,
          onClose: () => setNewOpen(false),
          onSaved: (ent) => { setNewOpen(false); refresh(); setSelectedId(ent.id); },
        }),
      ],
    }),
  });
}

// ---------------------------------------------------------------------------
// Graph view. SVG via jsx() (no new imports). Layout is force-lite:
// 1. Seed: nodes on a circle, order stable across reloads.
// 2. Iterate K=90 times: pairwise Coulomb-ish repulsion (O(n^2); the
//    case DB is a human-curated set, n stays small), Hooke springs
//    along edges, weak gravity to the center. Step shrinks linearly.
// 3. Freeze. No animation loop, no physics engine, no imports.
// Interactions use plain DOM/React handlers (pointer drag for pan,
// wheel for zoom, click for select). The SDK documents no gesture
// widgets, and none are needed: this is standard React on SVG.
// ---------------------------------------------------------------------------
const GRAPH_W = 900;
const GRAPH_H = 620;

function layoutForceLite(nodes, edges) {
  const pos = {};
  nodes.forEach((n, i) => {
    const a = (2 * Math.PI * i) / Math.max(nodes.length, 1);
    pos[n.id] = {
      x: GRAPH_W / 2 + (GRAPH_W * 0.32) * Math.cos(a),
      y: GRAPH_H / 2 + (GRAPH_H * 0.32) * Math.sin(a),
    };
  });
  const REST = 150;
  const K = 90;
  for (let k = 0; k < K; k++) {
    const f = {};
    nodes.forEach((n) => { f[n.id] = { x: 0, y: 0 }; });
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const a = pos[nodes[i].id];
        const b = pos[nodes[j].id];
        let dx = a.x - b.x;
        let dy = a.y - b.y;
        if (dx === 0 && dy === 0) { dx = 1; dy = 0; }
        const d2 = dx * dx + dy * dy;
        const d = Math.sqrt(d2);
        const rep = 9000 / d2;
        f[nodes[i].id].x += (dx / d) * rep;
        f[nodes[i].id].y += (dy / d) * rep;
        f[nodes[j].id].x -= (dx / d) * rep;
        f[nodes[j].id].y -= (dy / d) * rep;
      }
    }
    edges.forEach((e) => {
      const a = pos[e.from];
      const b = pos[e.to];
      if (!a || !b) return;
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const d = Math.hypot(dx, dy) || 1;
      const s = ((d - REST) / d) * 0.05;
      f[e.from].x += dx * s;
      f[e.from].y += dy * s;
      f[e.to].x -= dx * s;
      f[e.to].y -= dy * s;
    });
    nodes.forEach((n) => {
      const p = pos[n.id];
      f[n.id].x += (GRAPH_W / 2 - p.x) * 0.01;
      f[n.id].y += (GRAPH_H / 2 - p.y) * 0.01;
    });
    const cap = 30 * (1 - k / K);
    nodes.forEach((n) => {
      const p = pos[n.id];
      const v = f[n.id];
      const m = Math.hypot(v.x, v.y);
      const s = m > cap && m > 0 ? cap / m : 1;
      p.x += v.x * s;
      p.y += v.y * s;
    });
  }
  return pos;
}

function GraphPage({ ctx }) {
  const graphQ = useApi(ctx, 'case-graph', '/cases/graph', 15000);
  const [view, setView] = useState({ tx: 0, ty: 0, k: 1 });
  const [selectedId, setSelectedId] = useState(null);
  const [hiddenTypes, setHiddenTypes] = useState([]);
  const svgRef = useRef(null);
  const drag = useRef(null);

  const nodes = ((graphQ.data && graphQ.data.nodes) || [])
    .filter((n) => !hiddenTypes.includes(n.type));
  const keep = new Set(nodes.map((n) => n.id));
  const edges = ((graphQ.data && graphQ.data.edges) || [])
    .filter((e) => keep.has(e.from) && keep.has(e.to));

  const nodeKey = nodes.map((n) => n.id).join(',');
  const edgeKey = edges.map((e) => e.id).join(',');
  const pos = useMemo(() => layoutForceLite(nodes, edges),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [nodeKey, edgeKey]);

  // Wheel zoom around the cursor. Added with { passive: false } so
  // preventDefault stops page scroll; plain DOM, no SDK surface.
  useEffect(() => {
    const el = svgRef.current;
    if (!el) return undefined;
    const onWheel = (ev) => {
      ev.preventDefault();
      const rect = el.getBoundingClientRect();
      const sx = ev.clientX - rect.left;
      const sy = ev.clientY - rect.top;
      setView((v) => {
        const k2 = Math.min(3, Math.max(0.3, v.k * (ev.deltaY < 0 ? 1.12 : 0.89)));
        const wx = (sx - v.tx) / v.k;
        const wy = (sy - v.ty) / v.k;
        return { k: k2, tx: sx - wx * k2, ty: sy - wy * k2 };
      });
    };
    el.addEventListener('wheel', onWheel, { passive: false });
    return () => el.removeEventListener('wheel', onWheel);
  }, []);

  const onPointerDown = (ev) => {
    drag.current = { x: ev.clientX, y: ev.clientY, tx: view.tx, ty: view.ty, moved: false };
    ev.currentTarget.setPointerCapture && ev.currentTarget.setPointerCapture(ev.pointerId);
  };
  const onPointerMove = (ev) => {
    const d = drag.current;
    if (!d) return;
    const dx = ev.clientX - d.x;
    const dy = ev.clientY - d.y;
    if (Math.abs(dx) + Math.abs(dy) > 6) d.moved = true;
    if (d.moved) setView((v) => ({ ...v, tx: d.tx + dx, ty: d.ty + dy }));
  };
  const onPointerUp = (ev) => {
    const d = drag.current;
    drag.current = null;
    if (d && !d.moved) {
      const nid = ev.target && ev.target.dataset
        ? ev.target.dataset.nodeid : null;
      if (nid) setSelectedId(nid);
    }
  };
  const toggleType = (t) => {
    setHiddenTypes((h) => h.includes(t) ? h.filter((x) => x !== t) : [...h, t]);
  };

  return jsx(Page, {
    title: 'Case graph',
    actions: jsxs(Fragment, {
      children: [
        jsx(BackendBadge, { key: 'b', ctx }),
        jsx(Button, {
          key: 'r', variant: 'outline',
          onClick: () => { setView({ tx: 0, ty: 0, k: 1 }); setSelectedId(null); },
        }, 'Reset view'),
      ],
    }),
    children: jsxs(Fragment, {
      children: [
        jsxs('div', {
          key: 'ctl', style: { display: 'flex', gap: 12, marginBottom: 8, alignItems: 'center', flexWrap: 'wrap' },
          children: [
            jsx('span', { key: 'l', style: { fontSize: 12, opacity: 0.7 } }, 'Show:'),
            ...CASE_TYPES.map((t) =>
              jsxs('label', {
                key: t, style: { display: 'flex', gap: 4, alignItems: 'center', fontSize: 12 },
                children: [
                  jsx(Checkbox, {
                    key: 'c', checked: !hiddenTypes.includes(t),
                    onChange: () => toggleType(t),
                  }),
                  jsx('span', {
                    key: 'd', style: {
                      width: 10, height: 10, borderRadius: '50%',
                      background: CASE_TYPE_COLORS[t],
                    },
                  }),
                  t,
                ],
              })),
            jsx('span', { key: 'h', style: { fontSize: 12, opacity: 0.6 } },
              'Drag to pan · wheel to zoom · click a node for detail.'),
          ],
        }),
        jsxs('div', {
          key: 'cols', style: { display: 'flex', gap: 16, alignItems: 'flex-start' },
          children: [
            jsx('svg', {
              key: 'svg', ref: svgRef,
              width: '100%', height: 620, viewBox: `0 0 ${GRAPH_W} ${GRAPH_H}`,
              style: {
                flex: '1 1 60%', minWidth: 320, border: '1px solid var(--swarm-forensics-border, transparent)',
                borderRadius: 8, cursor: 'grab', touchAction: 'none', background: 'transparent',
              },
              onPointerDown, onPointerMove, onPointerUp,
              children: jsx('g', {
                transform: `translate(${view.tx},${view.ty}) scale(${view.k})`,
                children: [
                  ...edges.map((e) => {
                    const a = pos[e.from];
                    const b = pos[e.to];
                    if (!a || !b) return null;
                    return jsx('line', {
                      key: e.id, x1: a.x, y1: a.y, x2: b.x, y2: b.y,
                      stroke: '#666', strokeWidth: 1.2, opacity: 0.6,
                      children: jsx('title', null, e.rel),
                    });
                  }),
                  ...nodes.map((n) => {
                    const p = pos[n.id];
                    if (!p) return null;
                    const sel = n.id === selectedId;
                    return jsxs('g', {
                      key: n.id, 'data-nodeid': n.id,
                      style: { cursor: 'pointer' },
                      children: [
                        jsx('circle', {
                          key: 'c', 'data-nodeid': n.id,
                          cx: p.x, cy: p.y, r: sel ? 16 : 12,
                          fill: CASE_TYPE_COLORS[n.type] || '#888',
                          stroke: sel ? '#fff' : 'none', strokeWidth: sel ? 2 : 0,
                          opacity: 0.9,
                          children: jsx('title', null, `${n.label} (${n.type})`),
                        }),
                        jsx('text', {
                          key: 't', 'data-nodeid': n.id,
                          x: p.x, y: p.y + 28, textAnchor: 'middle',
                          fontSize: 11, fill: 'currentColor',
                        }, n.label.length > 22 ? n.label.slice(0, 21) + '…' : n.label),
                      ],
                    });
                  }),
                ],
              }),
            }),
            jsx('div', {
              key: 'detail', style: { flex: '1 1 40%', minWidth: 280 },
              children: jsx(EntityDetail, {
                ctx, entityId: selectedId, entities: (graphQ.data && graphQ.data.nodes) || [],
                onChanged: () => { graphQ.refetch(); setSelectedId(null); },
                onSelect: setSelectedId,
              }),
            }),
          ],
        }),
      ],
    }),
  });
}

// ---------------------------------------------------------------------------
// Registration. Every ctx.* / host.* call above keys to a HERMES_DESKTOP.md
// §1 row. [INF] marks shapes inferred from doc text rather than quoted.
// ---------------------------------------------------------------------------
const ROUTES = [
  { path: '/swarm-forensics', label: 'Dashboard', codicon: 'eye', el: DashboardPage },
  { path: '/swarm-forensics/hunt', label: 'Hunt', codicon: 'search', el: HuntPage },
  { path: '/swarm-forensics/chat', label: 'Chat', codicon: 'comment-discussion', el: ChatPage },
  { path: '/swarm-forensics/review', label: 'Review Queue', codicon: 'inbox', el: ReviewPage },
  { path: '/swarm-forensics/cases', label: 'Cases', codicon: 'briefcase', el: CasesPage },
  { path: '/swarm-forensics/graph', label: 'Graph', codicon: 'type-hierarchy', el: GraphPage },
  { path: '/swarm-forensics/iocs', label: 'IOC List', codicon: 'list-unordered', el: IocsPage },
  { path: '/swarm-forensics/research', label: 'Research', codicon: 'beaker', el: ResearchPage },
  { path: '/swarm-forensics/settings', label: 'Settings', codicon: 'gear', el: SettingsPage },
];

// /swarm-forensics subcommand -> route deep links (Worker-1 CLI).
// review -> /swarm-forensics/review, status -> /swarm-forensics,
// hunt -> /swarm-forensics/hunt, chat -> /swarm-forensics/chat,
// case -> /swarm-forensics/cases, graph -> /swarm-forensics/graph,
// iocs -> /swarm-forensics/iocs, research -> /swarm-forensics/research.

export default {
  id: 'swarm-forensics',
  name: 'Swarm Forensics',
  defaultEnabled: false, // opt-in: inventories in Capabilities -> Plugins
  register(ctx) {
    // Restore the Appearance enable pref (HERMES_DESKTOP.md §1: ctx.storage).
    if (ctx.storage && ctx.storage.get) {
      ctx.storage.get('uiEnabled').then((v) => {
        if (v === false) store.set({ uiEnabled: false });
      }).catch(() => {});
    }

    // Full pages (HERMES_DESKTOP.md §1 row: ROUTES_AREA).
    ROUTES.forEach((r) => {
      ctx.register({
        id: `swarm-forensics-route-${r.path}`,
        area: 'ROUTES_AREA',
        data: { path: r.path }, // §1 row: data: { path }
        render: () => jsx(r.el, { ctx }),
      });
    });

    // Sidebar nav sections (HERMES_DESKTOP.md §1 row: SIDEBAR_NAV_AREA).
    // [INF]: grouping under one collapsible header is inferred; a flat
    // list of rows still satisfies the row contract if the host
    // ignores grouping hints.
    ROUTES.forEach((r, i) => {
      ctx.register({
        id: `swarm-forensics-nav-${r.path}`,
        area: 'SIDEBAR_NAV_AREA',
        data: {
          path: r.path,
          label: i === 0 ? 'Swarm Forensics' : r.label,
          codicon: r.codicon, // §1 row: data: { path, label, codicon }
          group: 'swarm-forensics', // [INF] grouping hint
          indent: i === 0 ? 0 : 1, // [INF] section nesting hint
        },
        render: undefined,
      });
    });

    // Status-bar chip (HERMES_DESKTOP.md §1 row: statusBar.right).
    ctx.register({
      id: 'swarm-forensics-status-chip',
      area: 'statusBar.right',
      render: () => jsx(StatusChip, { ctx }),
    });

    // Command palette (HERMES_DESKTOP.md §1 row: PALETTE_AREA).
    // [INF]: command payload shape { command, run }.
    const commands = [
      ['swarm-forensics: Open dashboard', () => navigate(ctx, '/swarm-forensics')],
      ['swarm-forensics: Start hunt...', () => navigate(ctx, '/swarm-forensics/hunt')],
      ['swarm-forensics: Stop hunt', () => stopRunningHunt(ctx)],
      ['swarm-forensics: Open review queue', () => navigate(ctx, '/swarm-forensics/review')],
      ['swarm-forensics: Open case graph', () => navigate(ctx, '/swarm-forensics/graph')],
      ['swarm-forensics: New case entity…', () => {
        store.set({ casesNewOpen: true });
        navigate(ctx, '/swarm-forensics/cases');
      }],
      ['swarm-forensics: Status', () => navigate(ctx, '/swarm-forensics')],
      ['swarm-forensics: Pause / resume hunting', () => togglePause(ctx)],
    ];
    commands.forEach(([command, run], i) => {
      ctx.register({
        id: `swarm-forensics-palette-${i}`,
        area: 'PALETTE_AREA',
        data: { command, run },
      });
    });

    // Keybinds (HERMES_DESKTOP.md §1 row: KEYBINDS_AREA).
    // [INF]: payload shape { id, title, run }. Rebindable per doc.
    const binds = [
      ['swarm-forensics.pause-resume', 'Swarm Forensics: pause / resume hunting',
        () => togglePause(ctx)],
      ['swarm-forensics.review-accept', 'Swarm Forensics review: accept selected',
        () => reviewDecideSelected(ctx, 'accept')],
      ['swarm-forensics.review-reject', 'Swarm Forensics review: reject selected',
        () => reviewDecideSelected(ctx, 'reject')],
      ['swarm-forensics.review-narrow', 'Swarm Forensics review: narrow selected',
        () => reviewDecideSelected(ctx, 'narrow')],
    ];
    binds.forEach(([id, title, run]) => {
      ctx.register({ id, area: 'KEYBINDS_AREA', data: { title, run } });
    });

    // Appearance extras (HERMES_DESKTOP.md §1 row: APPEARANCE_AREAS.extra).
    ctx.register({
      id: 'swarm-forensics-appearance',
      area: 'APPEARANCE_AREAS.extra',
      render: () => jsx(AppearanceExtra, { ctx }),
    });
  },
};
