/* Read the actual teaching and test feedback handoffs, not just route availability. */
const assert=require('node:assert/strict'),fs=require('node:fs');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/Users/Junior/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const origin=process.env.APP_URL||'http://127.0.0.1:8080';
const authored=JSON.parse(fs.readFileSync('backend/academy/starter_curriculum.json')).find(p=>p.slug==='python-for-ai');
const technical=new Set(['ai-agent-bootcamp','ai-workshops','ai-engineering-12-week','genai-accelerator','python-for-ai']);
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_EXECUTABLE||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const context=await browser.newContext({viewport:{width:1440,height:1000}}),page=await context.newPage();
 const errors=[],failed=[];let chapters=0;
 page.on('pageerror',e=>errors.push(e.message));
 page.on('response',r=>{if(r.url().includes('/api/')&&r.status()>=400)failed.push({path:new URL(r.url()).pathname,status:r.status()})});
 const fits=async()=>assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'horizontal overflow');
 try{
  await page.goto(origin);await page.locator('.program-card').first().waitFor();
  const catalog=(await(await page.request.get(origin+'/api/programs/')).json()).filter(p=>technical.has(p.slug)||['freelancing-masterclass','terminal-tutor'].includes(p.slug));
  assert.equal(catalog.length,7);
  for(const program of catalog){
   assert.equal(Boolean(program.pedagogy),technical.has(program.slug));
   await page.goto(origin+'/#/programs/'+program.slug);
   await page.locator('.course-hero h1').filter({hasText:program.title}).waitFor();
   assert.equal(await page.locator('.engineering-contract').count()>0,technical.has(program.slug));
  }
  const program=catalog.find(p=>p.slug==='python-for-ai');
  assert(!JSON.stringify(program.pedagogy).includes('three synthetic policies'));
  await page.request.get(origin+'/api/auth/session/');
  const csrf=async()=>({'X-CSRFToken':(await context.cookies(origin)).find(c=>c.name==='csrftoken').value});
  const username='python_depth_'+Date.now();
  fs.writeFileSync('/tmp/academy-python-depth-user.json',JSON.stringify({username}),{mode:0o600});
  assert.equal((await page.request.post(origin+'/api/auth/session/register/',{headers:await csrf(),data:{username,email:username+'@example.com',password:'Synthetic-depth-review-62941!'}})).status(),201);
  assert.equal((await page.request.post(origin+'/api/programs/python-for-ai/enroll/',{headers:await csrf()})).status(),201);
  await page.reload();await page.getByRole('button',{name:'Sign out',exact:true}).waitFor();
  for(let number=0;number<program.lessons.length;number++){
   const lesson=program.lessons[number],expected=authored.lessons[number].resources.learning;
   await page.goto(origin+`/#/learn/python-for-ai/${lesson.id}`);
   await page.getByRole('tab',{name:'Lesson',exact:true}).click();
   await page.getByRole('article',{name:'Chapter reading'}).waitFor();
   const detail=await(await page.request.get(origin+`/api/lessons/${lesson.id}/`)).json();
   assert.equal(detail.resources.learning.revision,expected.revision,'served authored revision');
   assert.equal(detail.content_hash,authored.lessons[number].content_hash);
   assert.equal(detail.resources.learning.quiz.length,5);
   for(let index=0;index<expected.chapters.length;index++){
    const contents=page.locator('.book-contents');
    if(await contents.getAttribute('open')===null)await contents.locator('summary').click();
    await page.getByRole('navigation',{name:'Lesson chapters'}).getByRole('button').nth(index).click();
    await page.locator('.chapter-reading>h2').filter({hasText:expected.chapters[index].title}).waitFor();
    assert((await page.locator('.chapter-reading .markdown-reader').innerText()).length>100);
    await fits();chapters++;
   }
   await page.getByRole('tab',{name:'Exercise',exact:true}).click();
   await page.getByRole('button',{name:'I’d like a hint',exact:true}).click();
   assert((await page.locator('.hint-box').innerText()).includes(expected.exercise.hints[0]));
   await page.locator('.practice-reference>summary').click();
   assert((await page.locator('.practice-reference').innerText()).includes('Complete reference variation'));
   await page.getByRole('tab',{name:'Quiz',exact:true}).click();
   // Intentionally get the advanced questions wrong; feedback must route to their teaching.
   for(let i=0;i<expected.quiz.length;i++){
    const q=expected.quiz[i],choice=i>=3?q.options.find(o=>o.id!==q.correct).id:q.correct;
    await page.locator(`input[name="quiz-${lesson.id}-${q.id}"][value="${choice}"]`).check();
   }
   await page.getByRole('button',{name:'Check my answers',exact:true}).click();
   await page.locator('.quiz-result').filter({hasText:'3 of 5 correct'}).waitFor();
   assert.equal(await page.locator('.quiz-feedback').count(),5);
   await page.getByRole('button',{name:'Review explanation for question 4',exact:true}).click();
   await page.locator('.chapter-reading>h2').filter({hasText:expected.chapters.find(c=>c.id==='advanced-studio').title}).waitFor();
   await page.getByRole('tab',{name:'Quiz',exact:true}).click();
   await page.getByRole('button',{name:'Try again',exact:true}).click();
   for(const q of expected.quiz)await page.locator(`input[name="quiz-${lesson.id}-${q.id}"][value="${q.correct}"]`).check();
   await page.getByRole('button',{name:'Check my answers',exact:true}).click();
   await page.locator('.quiz-result').filter({hasText:'5 of 5 correct'}).waitFor();
   await page.getByRole('tab',{name:'Flashcards',exact:true}).click();
   await page.getByRole('button',{name:'Reveal flashcard answer',exact:true}).click();
   assert((await page.locator('.flashcard').innerText()).includes(expected.flashcards[0].back));
   await page.getByRole('tab',{name:'Notes',exact:true}).click();
   const note='Student review '+number+': '+expected.exercise.hints[0];
   await page.getByLabel('Your notes & observations',{exact:true}).fill(note);
   await page.getByRole('button',{name:'Save notes',exact:true}).click();
   await page.getByRole('status').filter({hasText:'Notes saved'}).waitFor();
   await page.reload();await page.getByLabel('Your notes & observations',{exact:true}).waitFor();
   assert.equal(await page.getByLabel('Your notes & observations',{exact:true}).inputValue(),note);
   console.log('PASS student lesson '+(number+1)+': all teaching chapters, complete solution, five graded questions, aligned review handoff, flashcard and saved notes');
  }
  assert.equal(chapters,77);
  const files=await(await page.request.get(origin+'/api/programs/python-for-ai/capstone-files/')).json();
  assert.equal(files.length,11);
  for(const file of files)assert.equal(file.content,fs.readFileSync('backend/academy/content/capstones/python-for-ai/'+file.path,'utf8'));
  for(const width of [390,320]){
   await page.setViewportSize({width,height:844});if(width===320)await page.emulateMedia({reducedMotion:'reduce'});
   for(const index of [0,7,11]){
    const lesson=program.lessons[index];await page.goto(origin+`/#/learn/python-for-ai/${lesson.id}`);
    await page.getByRole('tab',{name:'Lesson',exact:true}).click();await page.getByRole('article',{name:'Chapter reading'}).waitFor();
    await page.getByRole('button',{name:'Course contents',exact:true}).click();await page.getByRole('dialog').waitFor();
    await page.keyboard.press('Escape');await page.getByRole('dialog').waitFor({state:'hidden'});await fits();
    if(index===7)await page.screenshot({path:`docs/screenshots/python-depth-${width}.png`});
   }
  }
  assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);
  console.log('PASS all 77 chapters, 60 quiz answers and targeted mobile readers; engineering briefs shown only in the five technical programs. Synthetic learner: '+username);
 }catch(error){console.error('Failed route:',page.url(),failed);await page.screenshot({path:'/tmp/python-depth-failure.png',fullPage:true}).catch(()=>{});throw error}
 finally{await browser.close()}
})().catch(error=>{console.error(error);process.exitCode=1});
