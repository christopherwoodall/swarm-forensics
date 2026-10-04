// Real React from the test dependency folder, with one test hook.
// `useState` can start from a scripted value, so a server render can reach
// states that normally need a click (an open row, a selected entity).
// Rules live in globalThis.__sf.stateRules as [initial, replacement] pairs.

import { createRequire } from 'node:module'

const require = createRequire(`${process.env.SF_JS_DEPS}/`)
const React = require('react')

export const useState = init => {
  const state = globalThis.__sf || {}
  const rules = state.stateRules || []
  const counts = state.stateCounts || (state.stateCounts = new Map())
  const occurrence = counts.get(init) || 0
  counts.set(init, occurrence + 1)
  const hit = rules.find(([from, , index]) => Object.is(from, init) &&
    (index === undefined || index === occurrence))
  return React.useState(hit ? hit[1] : init)
}
export const useEffect = React.useEffect
export const useMemo = React.useMemo
export const useRef = React.useRef
export default React
