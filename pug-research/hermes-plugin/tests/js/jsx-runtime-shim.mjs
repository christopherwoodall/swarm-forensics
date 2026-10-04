// The real react/jsx-runtime, shared with the same React instance.

import { createRequire } from 'node:module'

const require = createRequire(`${process.env.SF_JS_DEPS}/`)
const runtime = require('react/jsx-runtime')

export const jsx = runtime.jsx
export const jsxs = runtime.jsxs
export const Fragment = runtime.Fragment
