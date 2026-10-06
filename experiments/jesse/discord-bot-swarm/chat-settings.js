import {DEFAULT_CHAT} from './frontend/bot-defaults.js';
export const chatDefaults=DEFAULT_CHAT;
export function chatConfig(value={}){
 const c={...chatDefaults,...value};
 if(Object.keys(c).some(k=>!Object.keys(chatDefaults).includes(k)&&k!=='replyStyle')||(c.replyStyle!==undefined&&!['default','brief'].includes(c.replyStyle))||!['off','mentions','normal'].includes(c.mode)||!Number.isInteger(c.cooldownSeconds)||c.cooldownSeconds<0||c.cooldownSeconds>3600||!Number.isInteger(c.maxRepliesPerHour)||c.maxRepliesPerHour<1||c.maxRepliesPerHour>120)throw Error('Invalid chat settings: choose Off, Mentions or Normal, cooldown 0–3600 seconds, 1–120 replies/hour and default or brief reply style.');
 return c;
}
export function savedChat(config){const {mode,cooldownSeconds,maxRepliesPerHour,replyStyle}=config.chat||{};return chatConfig({...chatDefaults,...(mode!==undefined?{mode}:{}),...(cooldownSeconds!==undefined?{cooldownSeconds}:{}),...(maxRepliesPerHour!==undefined?{maxRepliesPerHour}:{}),...(replyStyle!==undefined?{replyStyle}:{})});}
