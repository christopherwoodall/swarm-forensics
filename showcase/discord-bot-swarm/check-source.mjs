import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const root=path.dirname(fileURLToPath(import.meta.url));
const source=JSON.parse(fs.readFileSync(path.join(root,'SOURCE.json'),'utf8'));
if(!/^[a-f0-9]{40}$/.test(source.revision))throw Error('Invalid source revision.');
for(const [name,digest] of Object.entries(source.sha256)){
 if(name.startsWith('/')||name.split('/').includes('..'))throw Error('Invalid source path.');
 const bytes=fs.readFileSync(path.join(root,'discord-bot-swarm',name));
 if(crypto.createHash('sha256').update(bytes).digest('hex')!==digest)throw Error(`Source differs: ${name}`);
}
for(const name of source.excluded){
 if(fs.existsSync(path.join(root,'discord-bot-swarm',name)))throw Error(`Excluded source exists: ${name}`);
}
console.log(`Verified ${Object.keys(source.sha256).length} files from ${source.revision}.`);
