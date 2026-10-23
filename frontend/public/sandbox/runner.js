// This document has an opaque origin (sandbox without allow-same-origin).
// Its CSP only permits loading runtime assets, never academy APIs or external sites.
const runtime=new URL('/python/',location.href).href;
const program=`
importScripts(${JSON.stringify(runtime+'pyodide.js')});
self.onmessage=async({data})=>{
 try {
  const py=await loadPyodide({indexURL:${JSON.stringify(runtime)}});
  const code=data.code, checks=data.checks;
  py.globals.set('student_code',code);
  py.globals.set('check_json',JSON.stringify(checks));
  const output=await py.runPythonAsync(\`
import json, contextlib, io, traceback
class BoundedOutput(io.StringIO):
    def write(self, value):
        if self.tell() + len(value) > 12000:
            raise RuntimeError("Output limit reached. Print a smaller sample.")
        return super().write(value)
stream = BoundedOutput()
namespace = {}
results = []
setup_error = None
with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
    try:
        exec(student_code, namespace)
    except BaseException:
        setup_error = traceback.format_exc()[-2000:]
    for check in json.loads(check_json):
        try:
            if setup_error:
                raise RuntimeError(setup_error)
            passed = bool(eval(check['expression'], namespace))
            detail = "Passed" if passed else check['feedback']
        except BaseException as error:
            passed = False
            detail = str(error)[-1500:] + " | " + check['feedback']
        results.append({'name': check['name'], 'passed': passed, 'detail': detail})
json.dumps({'results': results, 'output': stream.getvalue()})
\`);
  self.postMessage({type:'result',...JSON.parse(output)});
 } catch(error) {self.postMessage({type:'error',message:String(error).slice(0,2000)});}
};`;
let worker;
window.addEventListener('message',event=>{
 if(event.source!==parent||event.data?.type!=='run')return;
 worker?.terminate();
 const blob=URL.createObjectURL(new Blob([program],{type:'text/javascript'}));
 worker=new Worker(blob);
 worker.onmessage=({data})=>{parent.postMessage(data,'*');worker.terminate();URL.revokeObjectURL(blob)};
 worker.onerror=()=>parent.postMessage({type:'error',message:'Python runtime could not load. Reload and retry.'},'*');
 worker.postMessage({code:event.data.code,checks:event.data.checks});
});
window.addEventListener('pagehide',()=>worker?.terminate());
parent.postMessage({type:'ready'},'*');
