// Read all three practical programs, then exercise the actual guidance and feedback.
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/Users/Junior/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const origin=process.env.APP_URL||'http://127.0.0.1:8080';
 const programs=JSON.parse(fs.readFileSync(path.join(__dirname,'../backend/academy/starter_curriculum.json'),'utf8')).slice(0,3);
 const filter=new Set((process.argv[2]||'').split(',').filter(Boolean));
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});page.setDefaultTimeout(15000);
 const errors=[];page.on('pageerror',e=>errors.push(e.message));let chapters=0,feedbackEntries=0,sessions=0;
 try{
  const name='practical_student_'+Date.now();
  const registration=await page.request.post(origin+'/api/auth/register/',{data:{username:name,email:name+'@example.invalid',password:'Student-review-private-947!'}});assert.equal(registration.status(),201);
  const {token}=await registration.json();const headers={Authorization:'Token '+token};
  for(const source of programs)assert.ok((await page.request.post(origin+'/api/programs/'+source.slug+'/enroll/',{headers})).ok());
  const catalog=await(await page.request.get(origin+'/api/programs/')).json();
  await page.addInitScript(t=>sessionStorage.setItem('academy-token',t),token);
  for(const [programIndex,source] of programs.entries()){
  const prefix='BWF'[programIndex];
  const live=catalog.find(p=>p.slug===source.slug);
  for(let i=0;i<source.lessons.length;i++){
   const response=await page.request.get(origin+`/api/lessons/${live.lessons[i].id}/`,{headers});assert.equal(response.status(),200);
   const published=(await response.json()).resources.learning,authored=source.lessons[i].resources.learning;
   assert.equal(published.revision,authored.revision);assert.deepEqual(published.chapters,authored.chapters);
   assert.deepEqual(published.exercise,authored.exercise);assert.deepEqual(published.questions,authored.questions);
  }
  console.log(`PASS: all ${source.lessons.length} served ${source.slug} lesson revisions, chapters, exercises, solutions and reflection guidance match reviewed source.`);
  await page.goto(origin);
  await page.getByRole('button',{name:'My learning',exact:true}).first().click();
  await page.locator('.dashboard-course').filter({has:page.getByRole('heading',{name:source.title,exact:true})}).getByRole('button',{name:'Continue learning',exact:true}).click();
  const indices=Array.from({length:source.lessons.length},(_,i)=>i).filter(i=>!filter.size||filter.has(prefix+String(i+1).padStart(2,'0')));
  for(const index of indices){
   const lesson=source.lessons[index],learning=lesson.resources.learning,id=live.lessons[index].id;
   sessions++;const key=prefix+String(index+1).padStart(2,'0');console.log(`Student review ${key}: ${lesson.title}`);
   await page.locator('.lesson-layout aside>button').nth(index).click();
   await page.getByRole('article',{name:'Chapter reading'}).getByRole('heading',{name:learning.chapters[0].title,exact:true}).waitFor();
   await page.locator('.book-contents>summary').click();
   const buttons=page.getByRole('navigation',{name:'Lesson chapters'}).getByRole('button');
   for(let i=0;i<learning.chapters.length;i++){
    const expected=learning.chapters[i];await buttons.nth(i).click();
    await page.getByRole('article',{name:'Chapter reading'}).getByRole('heading',{name:expected.title,exact:true}).waitFor();
    const blocks=[...expected.body.matchAll(/^```[^\n]*\n([\s\S]*?)^```/gm)].map(m=>m[1].trim());
    assert.deepEqual((await page.locator('.chapter-reading pre code').allTextContents()).map(t=>t.trim()),blocks,lesson.title);
    if(expected.id==='concept-tutorial')for(let j=0;j<3;j++)await page.getByRole('heading',{name:`Step ${j+1} · ${learning.concepts[j].term}`,exact:true}).waitFor();
    chapters++;
   }
   await page.getByRole('tab',{name:'Exercise',exact:true}).click();
   await page.getByRole('button',{name:'I’d like a hint',exact:true}).click();
   assert.equal(await page.locator('.hint-box li').count(),1);
   await page.getByRole('button',{name:'Show next hint',exact:true}).click();assert.equal(await page.locator('.hint-box li').count(),2);
   await page.getByRole('button',{name:'Show next hint',exact:true}).click();assert.equal(await page.locator('.hint-box li').count(),3);
   assert.equal(await page.getByRole('button',{name:'Show next hint',exact:true}).count(),0);
   await page.locator('.practice-reference>summary').click();
   const expected=[...learning.exercise.solution.matchAll(/^```[^\n]*\n([\s\S]*?)^```/gm)].map(m=>m[1].trim());
   assert.deepEqual((await page.locator('.practice-reference pre code').allTextContents()).map(t=>t.trim()),expected);
   await page.getByRole('tab',{name:'Questions',exact:true}).click();
   const guidance=page.locator('.reflection-guidance');assert.equal(await guidance.count(),3);
   for(let j=0;j<3;j++){await guidance.nth(j).locator('summary').click();assert.equal(await guidance.nth(j).locator('p').textContent(),learning.questions[j].guidance)}
   await page.getByLabel('Reflection response',{exact:true}).first().fill('I traced the input and actual state transitions, ran the published baseline and reference assertions, and kept the untested integration claims separate.');
   await page.getByRole('button',{name:'Save reflection',exact:true}).click();await page.getByRole('status').filter({hasText:'Reflection saved'}).waitFor();
   await page.getByRole('tab',{name:'Quiz',exact:true}).click();
   const wrong=learning.quiz.map(q=>q.options.find(o=>o.id!==q.correct));
   for(let j=0;j<3;j++)await page.getByRole('radio',{name:wrong[j].text,exact:true}).check();
   await page.getByRole('button',{name:'Check my answers',exact:true}).click();await page.getByText('0 of 3 correct',{exact:true}).waitFor();
   assert.deepEqual(await page.locator('.quiz-feedback p').allTextContents(),learning.quiz.map((q,j)=>q.option_feedback[wrong[j].id]));
   if(index===0||index===source.lessons.length-1)await page.screenshot({path:path.join(__dirname,`../docs/screenshots/student-${key}-review-feedback.png`)});
   await page.getByRole('button',{name:'Review explanation for question 1',exact:true}).click();
   await page.getByRole('article',{name:'Chapter reading'}).getByRole('heading',{name:'Learn each concept step by step',exact:true}).waitFor();
   await page.getByRole('tab',{name:'Quiz',exact:true}).click();await page.getByRole('button',{name:'Try again',exact:true}).click();
   for(const q of learning.quiz)await page.getByRole('radio',{name:q.options.find(o=>o.id===q.correct).text,exact:true}).check();
   await page.getByRole('button',{name:'Check my answers',exact:true}).click();await page.getByText('3 of 3 correct',{exact:true}).waitFor();
   // Check every answer choice's actual server response, including the unchosen distractors.
   const publicLesson=await(await page.request.get(origin+`/api/lessons/${id}/`,{headers})).json();
   assert.ok(publicLesson.resources.learning.quiz.every(q=>!('option_feedback'in q)&&!('correct'in q)));
   const persisted=await(await page.request.get(origin+`/api/lessons/${id}/practice/`,{headers})).json();
   assert.equal(persisted.reflection_answers[learning.questions[0].id],'I traced the input and actual state transitions, ran the published baseline and reference assertions, and kept the untested integration claims separate.');
   for(let rotation=0;rotation<3;rotation++){
    const answers=Object.fromEntries(learning.quiz.map(q=>[q.id,q.options[rotation].id]));
    const response=await page.request.post(origin+`/api/lessons/${id}/quiz/`,{headers,data:{revision:learning.revision,answers}});assert.equal(response.status(),201);
    for(const f of (await response.json()).feedback){const q=learning.quiz.find(q=>q.id===f.id);assert.equal(f.explanation,q.option_feedback[answers[q.id]]);feedbackEntries++}
   }
   if(index===source.lessons.length-1)await page.screenshot({path:path.join(__dirname,`../docs/screenshots/student-${key}-feedback.png`)});
   if(index===0){
    await page.setViewportSize({width:390,height:844});await page.getByRole('tab',{name:'Exercise',exact:true}).click();
    await page.locator('.practice-reference>summary').click();
    await page.locator('.lesson-tabs>button[aria-selected=true]').evaluate(button=>Promise.all(button.getAnimations().map(animation=>animation.finished)));
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'mobile practice/reference overflow');
    await page.locator('.practice-reference').scrollIntoViewIfNeeded();
    await page.screenshot({path:path.join(__dirname,`../docs/screenshots/student-${prefix}-mobile.png`)});await page.setViewportSize({width:1440,height:1000});
   }
   // Returning to Lesson resets chapter state through the explicit review target.
   await page.getByRole('tab',{name:'Lesson',exact:true}).click();
  }
  }
  assert.equal(sessions,filter.size||60);assert.equal(feedbackEntries,sessions*9);assert.deepEqual(errors,[]);
  console.log(`PASS:${sessions} student sessions;${chapters} rendered chapters;${sessions*3} taught concepts;${sessions} exact complete reference solutions;${sessions*3} staged hints;${feedbackEntries} answer-choice feedback entries; remediation navigation, reflection persistence and mobile reading checked.`);
 }catch(e){await page.screenshot({path:path.join(__dirname,'../docs/screenshots/practical-student-failure.png')});throw e}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
