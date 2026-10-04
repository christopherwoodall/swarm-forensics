import fs from 'node:fs';
import path from 'node:path';
import {fairystackConfig} from './deploy/fairystack/adapter.js';
const localHttp=url=>['localhost','127.0.0.1','[::1]'].includes(url.hostname)&&url.protocol==='http:';
function url(value,name,{origin=false}={}){let u;try{u=new URL(value);}catch{throw Error(`${name} must be an absolute URL.`);}if(u.username||u.password||u.search||u.hash||(u.protocol!=='https:'&&!localHttp(u)))throw Error(`${name} requires HTTPS (HTTP is permitted only on loopback).`);if(origin&&u.pathname!=='/')throw Error(`${name} must contain only an origin.`);return origin?u.origin:value.replace(/\/$/,'');}
export function loadConfig(env=process.env,root=process.cwd()){
 const explicit=!!env.PUBLIC_ORIGIN;
 const hosted=explicit?null:fairystackConfig(root);
 const publicOrigin=url(env.PUBLIC_ORIGIN||hosted?.publicOrigin,'PUBLIC_ORIGIN',{origin:true});
 const port=Number(env.PORT||3000);if(!Number.isInteger(port)||port<1||port>65535)throw Error('PORT must be an integer from 1 to 65535.');
 if(!env.DATA_DIR||!path.isAbsolute(env.DATA_DIR))throw Error('DATA_DIR must be an absolute path to a private directory.');
 let auth;if(env.OIDC_ISSUER||env.OIDC_CLIENT_ID){if(!env.OIDC_ISSUER||!env.OIDC_CLIENT_ID)throw Error('OIDC_ISSUER and OIDC_CLIENT_ID are both required.');auth={mode:'oidc',issuer:url(env.OIDC_ISSUER,'OIDC_ISSUER'),clientId:env.OIDC_CLIENT_ID,scope:env.OIDC_SCOPE||'openid profile email'};}
 else if(hosted)auth=hosted.auth;else throw Error('OIDC_ISSUER and OIDC_CLIENT_ID are required.');
 const dataDir=env.DATA_DIR;fs.mkdirSync(dataDir,{recursive:true,mode:0o700});const stat=fs.lstatSync(dataDir);if(!stat.isDirectory()||stat.uid!==process.getuid())throw Error('DATA_DIR must be a private directory owned by the service user.');if((stat.mode&0o077)!==0)fs.chmodSync(dataDir,0o700);
 return {port,publicOrigin,dataDir,auth,database:databaseConfig(env,hosted)};
}
export function databaseConfig(env={},hosted=null,{test=false}={}){
 const connectionString=test?env.TEST_DATABASE_URL:env.DATABASE_URL;
 const base={max:5,connectionTimeoutMillis:3000,idleTimeoutMillis:10000,statement_timeout:5000,query_timeout:6000};
 if(connectionString){let u;try{u=new URL(connectionString);}catch{throw Error('Database URL is invalid.');}if(!['postgres:','postgresql:'].includes(u.protocol))throw Error('Database URL must use PostgreSQL.');if(test&&!u.pathname.endsWith('_test'))throw Error('Test database name must end in _test.');return {...base,connectionString};}
 const database=test?(env.PGTESTDATABASE||'discord_bot_swarm_test'):(env.PGDATABASE||'discord_bot_swarm');if(test&&!database.endsWith('_test'))throw Error('Test database name must end in _test.');
 return {...base,host:env.PGHOST||hosted?.databaseHost||'localhost',port:Number(env.PGPORT||5432),database,...(env.PGUSER?{user:env.PGUSER}:{}),...(env.PGPASSWORD?{password:env.PGPASSWORD}:{})};
}
