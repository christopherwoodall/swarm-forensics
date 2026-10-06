import test from 'node:test';
import assert from 'node:assert/strict';
import {MessageFlags} from 'discord.js';
import {DiscordMessageView,messagePreview} from './discord-message-view.js';

const content='The message stays compact in the shared channel.\n\n'+('Full text with **Markdown** and @everyone remains available to each reader. '.repeat(12));
function click(overrides={}){
 const calls=[];return {calls,isButton:()=>true,customId:'swarm:expand:123',guildId:'guild',channelId:'channel',message:{id:'message',author:{id:'bot'}},client:{user:{id:'bot'}},deferReply:async body=>calls.push(['defer',body]),editReply:async body=>calls.push(['edit',body]),...overrides};
}
test('short messages stay intact; character and line thresholds produce compact previews',()=>{
 assert.equal(messagePreview('a'.repeat(700)),null);assert.ok(messagePreview('a'.repeat(701)).length<400);
 assert.equal(messagePreview(Array(12).fill('line').join('\n')),null);assert.ok(messagePreview(Array(13).fill('line').join('\n')));
 assert.equal(messagePreview(content),'The message stays compact in the shared channel.\n…');
 const code=messagePreview('```js\n'+('const x = 1; '.repeat(80))+'\n```');assert.equal((code.match(/```/g)||[]).length,2);
 assert.ok(!/[\uD800-\uDBFF]\n…$/.test(messagePreview('x'.repeat(349)+'🦅'.repeat(300))));
});
test('persist before publishing, preserve exact original and reject conflicting nonce reuse',async()=>{
 const queries=[],view=new DiscordMessageView({query:async q=>{queries.push(q);return {rows:[{nonce:'123'}]};}});
 assert.deepEqual(await view.prepare({swarm:'relay',channelId:'channel'},'short','123'),{content:'short'});assert.equal(queries.length,0);
 const payload=await view.prepare({swarm:'relay',channelId:'channel'},content,'123');assert.equal(payload.components[0].components[0].label,'Show more');assert.equal(payload.components[0].components[0].custom_id,'swarm:expand:123');assert.equal(queries[0].values[3],content);assert.equal(queries[0].query_timeout,3000);
 await assert.rejects(view.prepare({swarm:'relay'},content,'invalid'),/numeric nonce/);
 const conflicting=new DiscordMessageView({query:async()=>({rows:[]})});await assert.rejects(conflicting.prepare({swarm:'relay'},content,'123'),/different content or channel/);
});
test('every reader receives original text privately; relay, guild, channel, message and bot are bound',async()=>{
 const interaction=click(),view=new DiscordMessageView({query:async q=>{assert.equal(interaction.calls[0][0],'defer');assert.deepEqual(q.values,['relay','123','channel','message','guild','bot']);assert.match(q.text,/l.enabled=true/);return {rows:[{content}]};}});
 await view.interaction('relay',interaction);assert.deepEqual(interaction.calls,[['defer',{flags:MessageFlags.Ephemeral}],['edit',{content,allowedMentions:{parse:[]}}]]);
});
test('foreign messages, malformed IDs and DMs cannot disclose stored text',async()=>{
 for(const overrides of [{message:{id:'message',author:{id:'foreign'}}},{customId:'swarm:expand:bad'},{guildId:null}]){
 const interaction=click(overrides);await new DiscordMessageView({query:async()=>{throw Error('must not query');}}).interaction('relay',interaction);
 assert.equal(interaction.calls[1][1].content,'This message is no longer available.');
 }
 const unrelated=click({customId:'another-button'});await new DiscordMessageView({}).interaction('relay',unrelated);assert.deepEqual(unrelated.calls,[]);
});
test('missing saved bodies and database failure terminate with visible private errors',async()=>{
 for(const query of [async()=>({rows:[]}),async()=>{throw Error('private database detail');}]){
 const interaction=click();await new DiscordMessageView({query}).interaction('relay',interaction);assert.equal(interaction.calls.length,2);assert.ok(!interaction.calls[1][1].content.includes('private database'));
 }
 const failedAck=click({deferReply:async()=>{throw Error('expired');}});await new DiscordMessageView({query:async()=>{throw Error('must not query');}}).interaction('relay',failedAck);assert.deepEqual(failedAck.calls,[]);
});
test('API context restores complete bot content without replacing human text or other channels',async()=>{
 const view=new DiscordMessageView({query:async q=>{assert.deepEqual(q.values,['relay','channel',['saved']]);return {rows:[{message_id:'saved',nonce:'123',content},{message_id:'human',content:'must not disclose'}]};}});
 const input=[{id:'saved',author:{id:'bot'},content:'preview',components:[{components:[{custom_id:'swarm:expand:123'}]}]},{id:'human',author:{id:'human'},content:'human text'}];
 const restored=await view.restore({swarm:'relay',channelId:'channel'},input,'bot');assert.equal(restored[0].content,content);assert.equal(restored[0].preview,'preview');assert.equal(restored[1].content,'human text');assert.equal(input[0].content,'preview');
 const edited=await view.restore({swarm:'relay',channelId:'channel'},[{...input[0],content:'New edit',components:[]}], 'bot');assert.equal(edited[0].content,'New edit');
});
