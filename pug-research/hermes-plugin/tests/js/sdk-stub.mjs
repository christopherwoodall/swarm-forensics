// Stand-in for @hermes/plugin-sdk. It serves canned backend data.
//
// plugin.js calls `useQuery({ queryKey, queryFn })`, and queryFn calls
// `ctx.rest(path)`. The test's `rest` records the path synchronously, so
// useQuery can look up a fixture for that path without any network.

const sf = () => globalThis.__sf

export const host = {
  notify() {},
  notifyError() {},
  navigate() {},
  state: {
    // Tests set globalThis.__sf.sessionId / .storedSessionId to focus a chat.
    focusedSessionId: { get: () => (globalThis.__sf && globalThis.__sf.sessionId) || null },
    focusedStoredSessionId: { get: () => (globalThis.__sf && globalThis.__sf.storedSessionId) || null }
  }
}

// Stand-in for the SDK's useValue (nanostores useStore). Server rendering is
// single-pass, so a plain get() is enough.
export function useValue(atom) {
  return atom && typeof atom.get === 'function' ? atom.get() : null
}

export const queryClient = { invalidateQueries() {} }

export function useQuery({ queryFn, enabled }) {
  const state = sf()
  if (enabled === false) return { data: undefined, isError: false, isLoading: false }
  state.lastPath = null
  const pending = queryFn()
  if (pending && pending.catch) pending.catch(() => {})
  const path = state.lastPath
  if (state.paths && path) state.paths.push(path)
  if (state.mode === 'loading') return { data: undefined, isError: false, isLoading: true }
  if (state.mode === 'error') return { data: undefined, isError: true, error: new Error('offline') }
  return { data: state.fixture(path), isError: false }
}

export const ROUTES_AREA = 'routes'
export const SIDEBAR_NAV_AREA = 'sidebar-nav'
export const PALETTE_AREA = 'palette'
export const KEYBINDS_AREA = 'keybinds'
export const STATUSBAR_AREAS = { left: 'statusbar-left', right: 'statusbar-right' }
export const COMPOSER_AREAS = { top: 'composer-top', underside: 'composer-underside' }
export const PANES_AREA = 'panes'
