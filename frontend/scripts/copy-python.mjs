import {mkdir,copyFile} from 'node:fs/promises'
const output=new URL('../public/python/',import.meta.url)
await mkdir(output,{recursive:true})
for(const name of ['pyodide.js','pyodide.asm.js','pyodide.asm.wasm','python_stdlib.zip','pyodide-lock.json']) {
 await copyFile(new URL('../node_modules/pyodide/'+name,import.meta.url),new URL(name,output))
}
