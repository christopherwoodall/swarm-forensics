export class OperationClient {
 async connect(link){this.operations=link.operations;}
 async listTools(){const tools=this.operations.catalog();if(!tools.length)throw Error('No operations available.');return {tools:tools.map(t=>({...t,annotations:{readOnlyHint:t.readOnly}}))};}
 async callTool({name,arguments:args}){try{return {content:[{type:'text',text:JSON.stringify(await this.operations.invoke(name,args))}]};}catch(e){return {isError:true,content:[{type:'text',text:e.message}]};}}
 async close(){}
}
export function testOperations(deps,factory){const operations=factory(deps);operations.connect=async link=>{link.operations=operations;};operations.close=async()=>{};return operations;}
export function linkedPair(){const link={};return [link,link];}
