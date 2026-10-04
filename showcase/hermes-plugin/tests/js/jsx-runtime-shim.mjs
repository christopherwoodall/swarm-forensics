// The real react/jsx-runtime, shared with the same React instance.

import { createRequire } from 'node:module'

const require = createRequire(`${process.env.SF_JS_DEPS}/`)
const runtime = require('react/jsx-runtime')

export const jsx = (...args) => {
  const element = runtime.jsx(...args)
  globalThis.__sf?.elements?.push(element)
  return element
}
export const jsxs = (...args) => {
  const element = runtime.jsxs(...args)
  globalThis.__sf?.elements?.push(element)
  return element
}
export const Fragment = runtime.Fragment
