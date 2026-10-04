// Module resolve hook for the render tests.
// It maps the three imports Hermes provides to local shims, so plugin.js
// loads unchanged under Node with a real React.

const MAP = {
  '@hermes/plugin-sdk': './sdk-stub.mjs',
  'react': './react-shim.mjs',
  'react/jsx-runtime': './jsx-runtime-shim.mjs'
}

export async function resolve(specifier, context, next) {
  if (MAP[specifier]) {
    return { url: new URL(MAP[specifier], import.meta.url).href, shortCircuit: true }
  }
  return next(specifier, context)
}
