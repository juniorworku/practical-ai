const assert=require('node:assert/strict');
const fs=require('node:fs');
(async()=>{
 const origin=process.env.APP_URL||'http://127.0.0.1:8080';
 const snapshot=JSON.parse(fs.readFileSync(process.env.PERSISTENCE_FILE,'utf8'));
 const login=await fetch(origin+'/api/auth/login/',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:snapshot.username,password:snapshot.password})});
 assert.equal(login.status,200);const {token}=await login.json();const headers={Authorization:'Token '+token};
 const get=async path=>{const r=await fetch(origin+'/api/'+path,{headers});assert.equal(r.status,200);return r.json()};
 assert.equal((await get('health/')).database,'postgresql');
 const me=await get('me/');assert.ok(me.completed.includes(snapshot.lessonId));
 const lesson=await get(`lessons/${snapshot.lessonId}/`);assert.equal(lesson.notes,'I tested the workflow boundaries with three synthetic examples.');
 const project=await get(`projects/${snapshot.projectId}/`);assert.equal(project.title,'Research helper');
 console.log('PASS: PostgreSQL account, enrollments, completion, private notes, and saved project survive full service restart.');
})().catch(e=>{console.error(e);process.exitCode=1});
