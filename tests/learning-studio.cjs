const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/Users/Junior/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_EXECUTABLE||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const origin=process.env.APP_URL||'http://127.0.0.1:8080';
 const source=JSON.parse(fs.readFileSync(path.join(__dirname,'../backend/academy/starter_curriculum.json'),'utf8'));
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 try{
  assert.equal((await (await page.request.get(origin+'/api/health/')).json()).database,'postgresql');
  await page.goto(origin);
  await page.locator('.program-card').first().waitFor();
  assert.equal(await page.locator('.program-card').count(),4);
  const palette=await page.evaluate(()=>{const css=getComputedStyle(document.documentElement);return ['--sage','--sage-light','--sand','--cream'].map(key=>css.getPropertyValue(key).trim().toLowerCase())});
  assert.deepEqual(palette,['#778873','#a1bc98','#dccfc0','#fdf6ed']);
  await page.screenshot({path:path.join(__dirname,'../docs/screenshots/sage-home-desktop.png'),fullPage:true});
  await page.locator('.program-card').filter({has:page.getByRole('heading',{name:'AI Agent Bootcamp',exact:true})}).getByRole('button',{name:'Explore program',exact:true}).click();
  await page.getByRole('heading',{name:'Your learning path',exact:true}).waitFor();
  assert.equal(await page.locator('.course-module').count(),8);
  await page.screenshot({path:path.join(__dirname,'../docs/screenshots/sage-course-overview.png'),fullPage:true});
  await page.getByRole('button',{name:'Start this program',exact:true}).click();
  const username='studio_'+Date.now();
  await page.getByLabel('Username',{exact:true}).fill(username);
  await page.getByLabel('Email address').fill(username+'@example.com');
  await page.getByLabel('Password',{exact:true}).fill('My-private-practice-password-947!');
  await page.getByRole('button',{name:'Create free account',exact:true}).click();
  await page.getByRole('tab',{name:'Lesson',exact:true}).waitFor();
  const token=await page.evaluate(()=>sessionStorage.getItem('academy-token'));
  const headers={Authorization:'Token '+token};
  const catalog=await(await page.request.get(origin+'/api/programs/')).json();
  let firstId;
  for(let index=0;index<source.length;index++){
   const course=source[index];const live=catalog.find(p=>p.slug===course.slug);
   await page.request.post(origin+`/api/programs/${course.slug}/enroll/`,{headers});
   if(index>0){
    await page.locator('.workspace-nav').getByRole('button',{name:'My learning',exact:true}).click();
    await page.reload();await page.getByRole('button',{name:'My learning',exact:true}).first().click();
    await page.locator('.dashboard-course').filter({has:page.getByRole('heading',{name:course.title,exact:true})}).getByRole('button',{name:'Continue learning',exact:true}).click();
    await page.getByRole('tab',{name:'Lesson',exact:true}).waitFor();
   }
   assert.equal(await page.locator('.lesson-layout aside>button').count(),course.lessons.length);
   assert.equal(await page.getByRole('button',{name:'Open the learning lab',exact:true}).count(),0);
   for(const summary of live.lessons){
    const response=await page.request.get(origin+`/api/lessons/${summary.id}/`,{headers});assert.equal(response.status(),200);
    const lesson=await response.json();assert.ok(!lesson.content.toLowerCase().includes('accelerator'));
    const learning=lesson.resources.learning;assert.ok(learning.quiz.length>2);assert.ok(learning.flashcards.length>=3);assert.equal(learning.questions.length,3);assert.ok(learning.chapters.length>=3);assert.ok(lesson.content.split(/\s+/).length>1000);assert.ok(!lesson.content.includes('](https://github.com'));assert.ok(learning.exercise.material.includes('Inspect the input'));
    assert.ok(learning.quiz.every(q=>!('correct'in q)&&!('explanation'in q)));
   }
   const lessonId=live.lessons[0].id;firstId??=lessonId;
   await page.locator('.book-contents>summary').click();
   await page.getByRole('navigation',{name:'Lesson chapters'}).waitFor();
   const chapterButtons=page.getByRole('navigation',{name:'Lesson chapters'}).getByRole('button');
   assert.equal(await chapterButtons.count(),course.lessons[0].resources.learning.chapters.length);
   for(let chapter=0;chapter<await chapterButtons.count();chapter++){
    await chapterButtons.nth(chapter).click();
    await page.getByRole('article',{name:'Chapter reading'}).getByRole('heading',{name:course.lessons[0].resources.learning.chapters[chapter].title,exact:true}).waitFor();
    assert.ok((await page.locator('.chapter-reading .markdown-reader').innerText()).length>500);
   }
   await chapterButtons.first().click();
   await page.locator('.book-contents>summary').click();
   assert.equal(await page.locator('a[href*="github.com/rohitg00/ai-engineering-from-scratch"]').count(),0);
   await page.screenshot({path:path.join(__dirname,`../docs/screenshots/book-${course.slug}.png`),fullPage:false});
   await page.getByRole('tab',{name:'Exercise',exact:true}).click();
   await page.getByRole('button',{name:'I’d like a hint',exact:true}).click();
   await page.locator('.hint-box').waitFor();
   assert.equal(await page.getByRole('button',{name:/Download.*workbook/i}).count(),0);
   await page.locator('.inline-practice').getByRole('heading',{name:'1. Inspect the input and predict the outcome',exact:true}).waitFor();
   assert.ok(await page.locator('.inline-practice pre').count()>=2);
   await page.getByRole('tab',{name:'Questions',exact:true}).click();
   await page.getByLabel('Reflection response',{exact:true}).first().fill('My scoped decision for '+course.title+' depends on source evidence and an observed failure, not a plausible demo.');
   await page.getByRole('button',{name:'Save reflection',exact:true}).click();
   await page.getByRole('status').filter({hasText:'Reflection saved'}).waitFor();
   await page.getByRole('tab',{name:'Quiz',exact:true}).click();
   for(const question of course.lessons[0].resources.learning.quiz){const answer=question.options.find(o=>o.id===question.correct);await page.getByRole('radio',{name:answer.text,exact:true}).check()}
   await page.getByRole('button',{name:'Check my answers',exact:true}).click();
   const total=course.lessons[0].resources.learning.quiz.length;await page.getByText(`${total} of ${total} correct`,{exact:true}).waitFor();
   await page.getByRole('tab',{name:'Flashcards',exact:true}).click();
   await page.getByRole('button',{name:'Reveal flashcard answer',exact:true}).click();
   await page.getByRole('button',{name:'I know this',exact:true}).click();
   await page.getByRole('status').filter({hasText:'Flashcard review saved'}).waitFor();
   await page.getByRole('tab',{name:'Practical task',exact:true}).click();
   for(const input of await page.locator('.acceptance-checklist input').all())await input.check();
   await page.getByLabel('Your evidence & observations',{exact:true}).fill('I completed the exercise in a separate synthetic workspace, tested the normal case and the named failure case, and recorded observed outputs and remaining limitations for '+course.title+'.');
   await page.getByRole('button',{name:'Submit practical task',exact:true}).click();
   await page.getByRole('status').filter({hasText:'Practical task submitted'}).waitFor();
   await page.getByRole('tab',{name:'Notes',exact:true}).click();
   await page.getByLabel('Your notes & observations',{exact:true}).fill('Private notes for '+course.title);
   await page.getByRole('button',{name:'Save notes',exact:true}).click();
   await page.getByRole('status').filter({hasText:'Notes saved'}).waitFor();
   const state=await(await page.request.get(origin+`/api/lessons/${lessonId}/practice/`,{headers})).json();
   assert.equal(state.last_quiz.score,total);assert.equal(state.task_status,'submitted');assert.deepEqual(state.known_cards,['card-1']);
   await page.getByRole('button',{name:'Mark lesson complete',exact:true}).click();
   await page.getByRole('button',{name:'Completed · mark incomplete',exact:true}).waitFor();
   if(index===0){
    await page.getByRole('tab',{name:'Quiz',exact:true}).click();
    await page.screenshot({path:path.join(__dirname,'../docs/screenshots/sage-quiz-desktop.png'),fullPage:true});
    await page.setViewportSize({width:390,height:844});
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Mobile quiz overflow');
    await page.getByRole('tab',{name:'Practical task',exact:true}).click();
    await page.screenshot({path:path.join(__dirname,'../docs/screenshots/sage-task-mobile.png'),fullPage:true});
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Mobile task overflow');
    await page.setViewportSize({width:1440,height:1000});
   }
  }
  // Reload and a second account exercise persistence and owner scoping.
  await page.reload();await page.getByRole('button',{name:'My learning',exact:true}).first().click();
  await page.getByRole('heading',{name:'Your learning paths',exact:true}).waitFor();
  const persisted=await(await page.request.get(origin+`/api/lessons/${firstId}/practice/`,{headers})).json();assert.equal(persisted.task_status,'submitted');assert.equal(persisted.attempt_count,1);
  const second=await(await page.request.post(origin+'/api/auth/register/',{data:{username:username+'_other',email:username+'_other@example.com',password:'Other-private-practice-password-947!'}})).json();
  const secondHeaders={Authorization:'Token '+second.token};await page.request.post(origin+'/api/programs/ai-agent-bootcamp/enroll/',{headers:secondHeaders});
  const isolated=await(await page.request.get(origin+`/api/lessons/${firstId}/practice/`,{headers:secondHeaders})).json();assert.equal(isolated.last_quiz,null);assert.equal(isolated.task_evidence,'');assert.deepEqual(isolated.known_cards,[]);
  // The Accelerator remains independently enrollable with its own source course.
  await page.locator('.workspace-nav').getByRole('button',{name:'GenAI Accelerator',exact:true}).click();
  await page.getByRole('button',{name:'Open curriculum',exact:true}).click();
  await page.getByRole('heading',{name:'Guided practice',exact:true}).waitFor();
  assert.equal(await page.locator('.lesson-layout aside>button').count(),105);
  assert.equal(await page.getByRole('tab',{name:'Quiz',exact:true}).count(),0);
  await page.getByRole('button',{name:'Practical AI home',exact:true}).click();
  await page.setViewportSize({width:390,height:844});
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Mobile home overflow');
  await page.screenshot({path:path.join(__dirname,'../docs/screenshots/sage-home-mobile.png'),fullPage:true});
  assert.deepEqual(errors,[]);
  if(process.env.PRACTICE_SNAPSHOT)fs.writeFileSync(process.env.PRACTICE_SNAPSHOT,JSON.stringify({token,lessonId:firstId,username,quizTotal:source[0].lessons[0].resources.learning.quiz.length}),{mode:0o600});
  console.log('PASS: exact sage palette, four independent program cards, public syllabus, own lessons for all three programs, 60 substantial course books with sequenced teaching chapters and expanded concept quizzes/flashcards, reflections, grading, flashcard review, practical submissions, inline input/output experiments without workbook redirects, notes, completion, reload persistence, owner isolation, independent Accelerator, desktop/mobile layout.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
