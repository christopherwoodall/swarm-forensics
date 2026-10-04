import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {loadConfig,databaseConfig} from './config.js';
const temp=fs.mkdtempSync(path.join(os.tmpdir(),'swarm-config-'));
process.on('exit',()=>fs.rmSync(temp,{recursive:true,force:true}));
const env={PUBLIC_ORIGIN:'http://127.0.0.1:3000',DATA_DIR:path.join(temp,'private'),OIDC_ISSUER:'https://id.example/realm',OIDC_CLIENT_ID:'public-client'};
test('independent configuration needs no deployment manifest or hosted authentication',()=>{const c=loadConfig(env,temp);assert.equal(c.auth.mode,'oidc');assert.equal(c.database.host,'localhost');assert.equal(c.port,3000);assert.equal(c.publicOrigin,env.PUBLIC_ORIGIN);});
test('explicit configuration never inherits the hosted identity',()=>{const c=loadConfig(env,process.cwd());assert.equal(c.auth.issuer,env.OIDC_ISSUER);assert.throws(()=>loadConfig({...env,OIDC_CLIENT_ID:''},process.cwd()),/both required/);});
test('unsafe origins, partial auth and symlinked data directories fail closed',()=>{assert.throws(()=>loadConfig({...env,PUBLIC_ORIGIN:'http://remote.example'},temp),/HTTPS/);assert.throws(()=>loadConfig({...env,PUBLIC_ORIGIN:'https://example.com/path'},temp),/origin/);assert.throws(()=>loadConfig({...env,OIDC_ISSUER:''},temp),/both required/);assert.throws(()=>loadConfig({...env,PORT:'invalid'},temp),/PORT/);const link=path.join(temp,'link');fs.symlinkSync(env.DATA_DIR,link);assert.throws(()=>loadConfig({...env,DATA_DIR:link},temp),/private directory/);});
test('PostgreSQL accepts standard URL or environment variables, without fallback',()=>{assert.equal(databaseConfig({DATABASE_URL:'postgresql://u:p@db/sample'}).connectionString,'postgresql://u:p@db/sample');assert.equal(databaseConfig({PGHOST:'db',PGUSER:'u',PGPASSWORD:'p'}).password,'p');assert.throws(()=>databaseConfig({DATABASE_URL:'sqlite://db'}),/PostgreSQL/);assert.throws(()=>databaseConfig({TEST_DATABASE_URL:'postgresql://db/production'},null,{test:true}),/end in _test/);});

test('startup tightens owned data permissions restored by a host deployer',()=>{const directory=path.join(temp,'deployer-owned');fs.mkdirSync(directory,{mode:0o750});loadConfig({...env,DATA_DIR:directory},temp);assert.equal(fs.statSync(directory).mode&0o777,0o700);});
