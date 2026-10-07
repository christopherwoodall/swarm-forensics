// Compatibility adapter for the existing deployment; never used with PUBLIC_ORIGIN.
import fs from 'node:fs';
import path from 'node:path';
export function fairystackConfig(root){
 const manifestPath=path.join(root,'fairystack.json'),authPath=path.join(root,'deploy/fairystack/auth-config.json');
 if(!fs.existsSync(manifestPath)||!fs.existsSync(authPath))return null;
 const manifest=JSON.parse(fs.readFileSync(manifestPath)),a=JSON.parse(fs.readFileSync(authPath));
 return {publicOrigin:`https://${manifest.public_host}`,databaseHost:'/var/run/postgresql',auth:{mode:'authreturn',appId:a.appId,clientId:a.clientId,issuer:`https://cognito-idp.${a.region}.amazonaws.com/${a.userPoolId}`,...(a.legacyIssuer?{legacyIssuer:a.legacyIssuer}:{}),script:'https://authreturn.com/static/auth_component.js'}};
}
