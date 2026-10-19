const assert=require('node:assert/strict');
const fs=require('node:fs');
(async()=>{
 const state=JSON.parse(fs.readFileSync(process.env.PRACTICE_SNAPSHOT||'/tmp/practical-ai-learning-state.json','utf8'));
 const origin=process.env.APP_URL||'http://127.0.0.1:8080';
 const headers={Authorization:'Token '+state.token};
 const health=await(await fetch(origin+'/api/health/')).json();assert.equal(health.database,'postgresql');
 const response=await fetch(origin+`/api/lessons/${state.lessonId}/practice/`,{headers});assert.equal(response.status,200);
 const saved=await response.json();assert.equal(saved.last_quiz.score,state.quizTotal);assert.equal(saved.attempt_count,1);assert.equal(saved.task_status,'submitted');assert.deepEqual(saved.known_cards,['card-1']);assert.ok(saved.reflection_answers.reflection.length>30);assert.ok(saved.task_evidence.length>80);
 const lesson=await(await fetch(origin+`/api/lessons/${state.lessonId}/`,{headers})).json();assert.equal(lesson.notes,'Private notes for AI Agent Bootcamp');
 console.log('PASS: PostgreSQL retains quiz, reflection, flashcard review, practical submission and notes after all services restart.');
})().catch(e=>{console.error(e);process.exitCode=1});
