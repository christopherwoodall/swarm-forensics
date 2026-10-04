import {test} from 'node:test';
import assert from 'node:assert/strict';
import {commandPolicy,commandText,runtimeAllowance} from './discord-commands.js';
const bot='123456789012345678',owner='223456789012345678';
test('command authorization requires explicit prefix, bot mention and configured human ID',()=>{const m={author:{id:owner,bot:false},content:`<@${bot}> !swarm Build a useful app`};assert.equal(commandText(m,bot,owner),'Build a useful app');assert.equal(commandText({...m,content:`!swarm <@!${bot}> Build a useful app`},bot,owner),'Build a useful app');for(const msg of [{...m,author:{id:'other',bot:false}},{...m,author:{id:owner,bot:true}},{...m,content:'Build a useful app'},{...m,content:`<@${bot}> hello`},{...m,content:`<@${bot}> !swarm `}])assert.equal(commandText(msg,bot,owner),null);});
test('user-adjustable runtime budgets, command rate and polling have finite validated bounds',()=>{const defaults=commandPolicy.parse({authorizedUserId:owner});assert.equal(defaults.enabled,false);assert.equal(defaults.dailyRuntimeMinutes,30);for(const bad of [{dailyRuntimeMinutes:0},{commandsPerHour:121},{pollSeconds:4},{maxRunSeconds:3601},{authorizedUserId:'wrong'},{key:'fake'}])assert.equal(commandPolicy.safeParse({authorizedUserId:owner,...bad}).success,false);});


test('runtime reservations fit remaining budget and stop at the UTC daily reset',()=>{const p={maxRunSeconds:300,dailyRuntimeMinutes:30};assert.equal(runtimeAllowance(p,1780,Date.parse('2026-10-04T12:00:00Z')),20);assert.equal(runtimeAllowance(p,0,Date.parse('2026-10-04T23:59:50Z')),10);assert.equal(runtimeAllowance(p,0,Date.parse('2026-10-05T00:00:00Z')),300);});
