import {build} from 'esbuild';
import fs from 'node:fs';
await build({entryPoints:['scripts/auth-oidc.js'],outfile:'frontend/auth-oidc.js',bundle:true,format:'esm',platform:'browser',target:'es2022',minify:true,legalComments:'eof',banner:{js:'/* Bundled dependencies retain their licenses; see /THIRD_PARTY_NOTICES.txt. */'}});

fs.writeFileSync('frontend/THIRD_PARTY_NOTICES.txt',['oidc-client-ts (unmodified library bundled with esbuild)\n'+fs.readFileSync('node_modules/oidc-client-ts/LICENSE','utf8'),'jwt-decode\n'+fs.readFileSync('node_modules/jwt-decode/LICENSE','utf8')].join('\n\n'));
