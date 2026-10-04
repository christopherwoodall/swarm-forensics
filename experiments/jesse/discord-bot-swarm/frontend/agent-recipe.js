// Shared prompt preview and copy feedback; callers own authorization and errors.
export function agentRecipe({title,prompt,copyLabel,loadPrompt,onCopied,mask,button}){
 const el=(tag,cls,text)=>{const node=document.createElement(tag);if(cls)node.className=cls;if(text!==undefined)node.textContent=text;return node;};
 const recipe=el('section','agent-recipe'),heading=el('h2','',title),snippet=el('pre');
 if(mask){const parts=prompt.split(mask);if(parts.length!==2)throw Error('Recipe token preview is invalid.');const line=el('span','agent-token-mask',mask);line.setAttribute('aria-label','Agent API key, masked. The copy button includes the actual key.');snippet.append(document.createTextNode(parts[0]),line,document.createTextNode(parts[1]));}else snippet.textContent=prompt;
 const feedback=el('span','copy-feedback');feedback.setAttribute('role','status');feedback.setAttribute('aria-live','polite');let timer;
 const copy=button(copyLabel,async()=>{await navigator.clipboard.writeText(await loadPrompt());clearTimeout(timer);feedback.textContent='Copied!';feedback.classList.add('visible');timer=setTimeout(()=>feedback.classList.remove('visible'),3000);onCopied?.();});copy.classList.add('agent-recipe-cta');
 const actions=el('div','setup-actions copy-actions');actions.append(copy,feedback);recipe.append(heading,actions,snippet);return recipe;
}
