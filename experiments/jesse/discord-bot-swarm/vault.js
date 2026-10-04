import crypto from 'node:crypto';
export function seal(key,plain,context){const iv=crypto.randomBytes(12),c=crypto.createCipheriv('aes-256-gcm',key,iv);c.setAAD(Buffer.from(context));return Buffer.concat([iv,c.update(plain),c.final(),c.getAuthTag()]).toString('base64');}
export function open(key,value,context){const b=Buffer.from(value,'base64');if(b.length<28)throw Error('Invalid encrypted credential.');const c=crypto.createDecipheriv('aes-256-gcm',key,b.subarray(0,12));c.setAAD(Buffer.from(context));c.setAuthTag(b.subarray(-16));return Buffer.concat([c.update(b.subarray(12,-16)),c.final()]);}
export class Vault{
 constructor(pool,master){this.pool=pool;this.master=master;}
 async init(){await this.pool.query('CREATE TABLE IF NOT EXISTS user_encryption_keys(owner text PRIMARY KEY,wrapped_key text NOT NULL)');}
 async userKey(owner){let row=(await this.pool.query('SELECT wrapped_key FROM user_encryption_keys WHERE owner=$1',[owner])).rows[0];if(!row){const plain=crypto.randomBytes(32),wrapped=seal(this.master,plain,`user-key:${owner}`);await this.pool.query('INSERT INTO user_encryption_keys VALUES($1,$2) ON CONFLICT DO NOTHING',[owner,wrapped]);plain.fill(0);row=(await this.pool.query('SELECT wrapped_key FROM user_encryption_keys WHERE owner=$1',[owner])).rows[0];}return open(this.master,row.wrapped_key,`user-key:${owner}`);}
 async encrypt(owner,purpose,value){const k=await this.userKey(owner);try{return 'v2:'+seal(k,Buffer.from(value),`${owner}:${purpose}`);}finally{k.fill(0);}}
 async decrypt(owner,purpose,value){if(!value.startsWith('v2:'))throw Error('Legacy credential must be reconnected.');const k=await this.userKey(owner);try{return open(k,value.slice(3),`${owner}:${purpose}`).toString();}finally{k.fill(0);}}
}
