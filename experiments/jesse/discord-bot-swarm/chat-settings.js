export const chatDefaults={mode:'mentions',cooldownSeconds:15,maxRepliesPerHour:30};
export function chatConfig(value={}){
 const c={...chatDefaults,...value};
 if(Object.keys(c).some(k=>!Object.keys(chatDefaults).includes(k))||!['off','mentions','normal'].includes(c.mode)||!Number.isInteger(c.cooldownSeconds)||c.cooldownSeconds<5||c.cooldownSeconds>3600||!Number.isInteger(c.maxRepliesPerHour)||c.maxRepliesPerHour<1||c.maxRepliesPerHour>120)throw Error('Invalid chat settings: choose Off, Mentions or Normal, cooldown 5–3600 seconds and 1–120 replies/hour.');
 return c;
}
export function savedChat(config){const {mode,cooldownSeconds,maxRepliesPerHour}=config.chat||{};return chatConfig({...chatDefaults,...(mode!==undefined?{mode}:{}),...(cooldownSeconds!==undefined?{cooldownSeconds}:{}),...(maxRepliesPerHour!==undefined?{maxRepliesPerHour}:{})});}
