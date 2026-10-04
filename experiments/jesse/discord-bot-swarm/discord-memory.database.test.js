import {test,before,after} from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import pg from 'pg';
import {databaseConfig} from './config.js';
import {memorySchema,DiscordMemory} from './discord-memory.js';
const pool=new pg.Pool(databaseConfig(process.env,null,{test:true})),memory=new DiscordMemory(pool),owner='memory-'+crypto.randomUUID();
const cfg={guildId:'12345678901234567',channelId:'22345678901234567'},m={id:'32345678901234567',author:{id:'42345678901234567',name:'Synthetic'},content:'Shared telescope context',timestamp:'2026-10-04T00:00:00Z'};
before(()=>memorySchema(pool));after(async()=>{await pool.query('DELETE FROM discord_messages WHERE owner=$1',[owner]);await pool.query('DELETE FROM discord_collection_status WHERE owner=$1',[owner]);await pool.end();});
test('persistent collection deduplicates, updates, and isolates owners and channels',async()=>{
 await memory.save(owner,cfg,[m]);await memory.save(owner,cfg,[m]);assert.equal((await memory.search(owner,cfg,'telescope',20)).messages.length,1);assert.equal(await memory.latest(owner,cfg.channelId),m.id);
 assert.equal((await memory.search('another-owner',cfg,'telescope',20)).messages.length,0);assert.equal((await memory.search(owner,{...cfg,channelId:'other'},'telescope',20)).messages.length,0);
 await memory.save(owner,cfg,[{...m,content:'Updated galaxy context'}]);assert.equal((await memory.search(owner,cfg,'telescope',20)).messages.length,0);assert.equal((await memory.search(owner,cfg,'galaxy',20)).messages.length,1);
 await memory.status(owner,cfg.channelId,'failed','Synthetic timeout');assert.equal((await memory.search(owner,cfg,'galaxy',20)).collection.state,'failed');await memory.status(owner,cfg.channelId,'completed');assert.equal((await memory.search(owner,cfg,'galaxy',20)).collection.error,null);
});
