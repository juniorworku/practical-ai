const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
(async()=>{
 const base=process.env.APP_URL||'http://127.0.0.1:8080';
 const source=JSON.parse(fs.readFileSync(path.join(__dirname,'../backend/academy/content/reviewed_workshop.json'),'utf8'));
 const username='reviewed_feedback_'+Date.now();
 const registration=await fetch(base+'/api/auth/register/',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username,email:username+'@example.invalid',password:'Review-fixture-password-628!'})});
 assert.equal(registration.status,201);const {token}=await registration.json();
 const headers={'Content-Type':'application/json',Authorization:'Token '+token};
 const catalog=await(await fetch(base+'/api/programs/')).json();let choices=0,lessons=0;
 for(const program of source){
  assert.ok((await fetch(base+'/api/programs/'+program.slug+'/enroll/',{method:'POST',headers})).ok);
  const live=catalog.find(p=>p.slug===program.slug);
  for(let index=0;index<program.lessons.length;index++){
   const lesson=program.lessons[index],learning=lesson.resources.learning,id=live.lessons[index].id;
   const response=await fetch(base+`/api/lessons/${id}/`,{headers});assert.equal(response.status,200);
   const published=(await response.json()).resources.learning;
   assert.equal(published.revision,learning.revision);
   assert.deepEqual(published.chapters,learning.chapters);
   assert.ok(!published.quiz[0].prompt.startsWith('At the marked assertion'));
   assert.ok(published.quiz.every(q=>!('correct'in q)&&!('option_feedback'in q)&&!('explanation'in q)));
   for(let rotation=0;rotation<3;rotation++){
    const answers=Object.fromEntries(learning.quiz.map(q=>[q.id,q.options[rotation].id]));
    const graded=await fetch(base+`/api/lessons/${id}/quiz/`,{method:'POST',headers,body:JSON.stringify({revision:learning.revision,answers})});assert.equal(graded.status,201);
    for(const item of (await graded.json()).feedback){
     const question=learning.quiz.find(q=>q.id===item.id);
     assert.equal(item.explanation,question.option_feedback[item.selected]);assert.equal(item.correct,item.selected===question.correct);choices++;
    }
   }
   lessons++;
  }
  console.log('PASS final authored checkpoints, protected keys and every feedback choice: '+program.slug);
 }
 assert.equal(lessons,113);assert.equal(choices,678);
 fs.writeFileSync(path.join(__dirname,'../docs/imported-feedback-review.json'),JSON.stringify({lessons,feedback_choices:choices,all_served_revisions_match:true,authored_scenarios:true,protected_keys:true},null,2));
 console.log(`PASS ${lessons} final lessons; ${choices} selected-choice explanations; protected answer keys; exact served chapter and revision parity.`);
})().catch(error=>{console.error(error);process.exitCode=1});
