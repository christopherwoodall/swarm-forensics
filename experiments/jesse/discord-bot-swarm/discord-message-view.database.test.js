import {test,before,after} from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import pg from 'pg';
import {databaseConfig} from './config.js';
import {DiscordMessageView,messageViewSchema} from './discord-message-view.js';
import {listenerSchema} from './chat-listener.js';
const config=databaseConfig(process.env,null,{test:true}),namespace='message_view_'+crypto.randomBytes(6).toString('hex');
const admin=new pg.Pool(config),pool=new pg.Pool({...config,options:`-c search_path=${namespace}`}),relay=crypto.randomUUID(),owner='message-view-'+crypto.randomUUID();
const run={swarm:relay,channelId:'123456789012345678'},bot='123456789012345679',guild='123456789012345680',message='123456789012345681',content='Persistent full text. '.repeat(60);
before(async()=>{
 await admin.query(`CREATE SCHEMA ${namespace}`);
 await pool.query('CREATE TABLE IF NOT EXISTS swarms(id uuid PRIMARY KEY,owner text NOT NULL,config jsonb NOT NULL,enabled boolean NOT NULL DEFAULT false,error text,created_at timestamptz NOT NULL DEFAULT now())');
 await pool.query('CREATE TABLE IF NOT EXISTS bots(id uuid PRIMARY KEY,swarm uuid NOT NULL REFERENCES swarms ON DELETE CASCADE,bot_id text UNIQUE NOT NULL,name text NOT NULL,role text NOT NULL,secret text NOT NULL,position integer NOT NULL)');
 await listenerSchema(pool);await messageViewSchema(pool);
 await pool.query('INSERT INTO swarms(id,owner,config) VALUES($1,$2,$3)',[relay,owner,{guildId:guild}]);
 await pool.query('INSERT INTO bots(id,swarm,bot_id,name,role,secret,position) VALUES($1,$2,$3,$4,$5,$6,0)',[crypto.randomUUID(),relay,bot,'Synthetic','relay','synthetic']);
 await pool.query('INSERT INTO discord_chat_listener(relay,enabled) VALUES($1,true)',[relay]);
});
after(async()=>{await pool.end();await admin.query(`DROP SCHEMA ${namespace} CASCADE`);await admin.end();});
function click(overrides={}){const replies=[];return {replies,isButton:()=>true,customId:'swarm:expand:123',guildId:guild,channelId:run.channelId,message:{id:message,author:{id:bot}},client:{user:{id:bot}},deferReply:async()=>{},editReply:async body=>replies.push(body),...overrides};}
test('persisted body survives new instances, exact retries are safe and cross-scope clicks fail',async()=>{
 const view=new DiscordMessageView(pool);await view.prepare(run,content,'123');await view.prepare(run,content,'123');
 await assert.rejects(view.prepare(run,content+' different','123'),/different content/);await assert.rejects(view.prepare({...run,channelId:'other'},content,'123'),/different content/);
 await view.delivered(run,'123',message);const restarted=new DiscordMessageView(pool),interaction=click();await restarted.interaction(relay,interaction);assert.equal(interaction.replies[0].content,content);
 for(const overrides of [{guildId:'other'},{channelId:'other'},{message:{id:'other',author:{id:bot}}}]){const wrong=click(overrides);await restarted.interaction(relay,wrong);assert.equal(wrong.replies[0].content,'This message is no longer available.');}
 const wrongRelay=click();await restarted.interaction(crypto.randomUUID(),wrongRelay);assert.equal(wrongRelay.replies[0].content,'This message is no longer available.');
 const restored=await restarted.restore(run,[{id:message,author:{id:bot},content:'preview',components:[{components:[{custom_id:'swarm:expand:123'}]}]}],bot);assert.equal(restored[0].content,content);
 await restarted.prepare(run,content+' Updated','124');await restarted.delivered(run,'124',message);await restarted.clear(run,message,'124');
 assert.deepEqual((await pool.query('SELECT nonce FROM discord_message_view WHERE relay=$1',[relay])).rows,[{nonce:'124'}]);
 const stale=click();await restarted.interaction(relay,stale);assert.equal(stale.replies[0].content,'This message is no longer available.');
 const updated=click({customId:'swarm:expand:124'});await restarted.interaction(relay,updated);assert.equal(updated.replies[0].content,content+' Updated');
 await pool.query('UPDATE discord_chat_listener SET enabled=false WHERE relay=$1',[relay]);const disabled=click();await restarted.interaction(relay,disabled);assert.equal(disabled.replies[0].content,'This message is no longer available.');
 await restarted.clear(run,message);assert.equal((await pool.query('SELECT * FROM discord_message_view WHERE relay=$1',[relay])).rows.length,0);
});
