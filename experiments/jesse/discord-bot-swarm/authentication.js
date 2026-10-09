import {createRemoteJWKSet,jwtVerify} from 'jose';
export async function createAuthenticator(auth){
 let jwksUrl;if(auth.mode==='authreturn')jwksUrl=auth.issuer+'/.well-known/jwks.json';
 else{const response=await fetch(auth.issuer+'/.well-known/openid-configuration',{signal:AbortSignal.timeout(10000)});if(!response.ok)throw Error('OIDC discovery failed.');const metadata=await response.json();if(metadata.issuer!==auth.issuer)throw Error('OIDC discovery issuer mismatch.');let u;try{u=new URL(metadata.jwks_uri);}catch{throw Error('Invalid OIDC JWKS URL.');}if(u.username||u.password||(u.protocol!=='https:'&&!(u.protocol==='http:'&&['127.0.0.1','localhost','[::1]'].includes(u.hostname))))throw Error('OIDC JWKS requires HTTPS.');jwksUrl=u.href;}
 const jwks=createRemoteJWKSet(new URL(jwksUrl),{timeoutDuration:5000,cooldownDuration:10000});
 return async token=>{const {payload}=await jwtVerify(token,jwks,{issuer:auth.issuer,algorithms:['RS256','ES256'],...(auth.mode==='oidc'?{audience:auth.clientId}:{})});if(typeof payload.sub!=='string'||!payload.sub||typeof payload.exp!=='number')throw Error('Invalid identity token.');if(auth.mode==='authreturn'&&!((payload.token_use==='id'&&payload.aud===auth.clientId)||(payload.token_use==='access'&&payload.client_id===auth.clientId)))throw Error('Invalid application token.');return `${auth.issuer}:${payload.sub}`;};
}
