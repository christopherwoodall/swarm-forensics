// Shared prompt preview and copy feedback; callers own authorization and errors.
export function agentRecipe({title,prompt,copyLabel,loadPrompt,onCopied,button}){
 const el=(tag,cls,text)=>{const node=document.createElement(tag);if(cls)node.className=cls;if(text!==undefined)node.textContent=text;return node;};
 const recipe=el('section','agent-recipe'),heading=el('h2','',title),snippet=el('pre');
 snippet.textContent=prompt;
 const feedback=el('span','copy-feedback');feedback.setAttribute('role','status');feedback.setAttribute('aria-live','polite');let timer;
 const copy=button(copyLabel,async()=>{await navigator.clipboard.writeText(await loadPrompt());clearTimeout(timer);feedback.textContent='Copied!';feedback.classList.add('visible');timer=setTimeout(()=>feedback.classList.remove('visible'),3000);onCopied?.();});copy.classList.add('agent-recipe-cta');
 const actions=el('div','setup-actions copy-actions');actions.append(copy,feedback);recipe.append(heading,actions,snippet);return recipe;
}
