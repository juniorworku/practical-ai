/* Exact published reading, selected exercise/feedback flows and responsive access. */
const assert=require('node:assert/strict'),fs=require('node:fs');
const {chromium}=require('/Users/Junior/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const origin='http://127.0.0.1:8080';
const slugs=new Set(['ai-agent-bootcamp','ai-workshops','ai-engineering-12-week','genai-accelerator']);
const source=['backend/academy/starter_curriculum.json','backend/academy/content/reviewed_workshop.json'].flatMap(p=>JSON.parse(fs.readFileSync(p))).filter(p=>slugs.has(p.slug));
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const context=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion:'reduce'}),page=await context.newPage();
 const errors=[],failed=[],report=[];page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.url().includes('/api/')&&r.status()>=400)failed.push([new URL(r.url()).pathname,r.status()])});
 const fits=async()=>assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'page overflow');
 const chapter=async(learning,index)=>{
  const contents=page.locator('.book-contents');if(await contents.getAttribute('open')===null)await contents.locator('summary').click();
  await page.getByRole('navigation',{name:'Lesson chapters'}).getByRole('button').nth(index).click();
  await page.locator('.chapter-reading>h2').filter({hasText:learning.chapters[index].title}).waitFor();
  const blocks=[...learning.chapters[index].body.matchAll(/^```[^\n]*\n([\s\S]*?)^```/gm)].map(m=>m[1].trim());
  assert.deepEqual((await page.locator('.chapter-reading pre code').allTextContents()).map(x=>x.trim()),blocks);
  await fits();
 };
 try{
  await page.goto(origin);await page.locator('.program-card').first().waitFor();
  const catalog=await(await page.request.get(origin+'/api/programs/')).json();
  await page.request.get(origin+'/api/auth/session/');
  const csrf=async()=>({'X-CSRFToken':(await context.cookies(origin)).find(c=>c.name==='csrftoken').value});
  const username='four_program_depth_'+Date.now();fs.writeFileSync('/tmp/academy-four-depth-user.json',JSON.stringify({username}),{mode:0o600});
  assert.equal((await page.request.post(origin+'/api/auth/session/register/',{headers:await csrf(),data:{username,email:username+'@example.com',password:'Synthetic-reading-check-9341!'}})).status(),201);
  for(const program of source)assert.equal((await page.request.post(origin+'/api/programs/'+program.slug+'/enroll/',{headers:await csrf()})).status(),201);
  await page.reload();await page.getByRole('button',{name:'Sign out',exact:true}).waitFor();
  for(const program of source){
   const live=catalog.find(p=>p.slug===program.slug);let chapters=0,studios=0;
   for(let n=0;n<program.lessons.length;n++){
    const authored=program.lessons[n],learning=authored.resources.learning,id=live.lessons[n].id;
    const response=await page.request.get(origin+`/api/lessons/${id}/`);assert.equal(response.status(),200);const served=await response.json();
    assert.equal(served.content_hash,authored.content_hash);assert.equal(served.resources.learning.revision,learning.revision);
    assert.deepEqual(served.resources.learning.chapters,learning.chapters);
    assert(served.resources.learning.quiz.every(q=>!('correct'in q)&&!('option_feedback'in q)));
    await page.goto(origin+`/#/learn/${program.slug}/${id}`);await page.getByRole('tab',{name:'Lesson',exact:true}).click();await page.getByRole('article',{name:'Chapter reading'}).waitFor();
    for(let i=0;i<learning.chapters.length;i++){await chapter(learning,i);chapters++}
    if(!learning.chapters.some(c=>c.id==='runtime-studio'))continue;
    studios++;
    await page.getByRole('tab',{name:'Exercise',exact:true}).click();
    await page.getByRole('button',{name:'I’d like a hint',exact:true}).click();assert((await page.locator('.hint-box').innerText()).includes(learning.exercise.hints[0]));
    await page.locator('.practice-reference>summary').click();
    const expected=[...learning.exercise.solution.matchAll(/^```[^\n]*\n([\s\S]*?)^```/gm)].map(m=>m[1].trim());
    assert.deepEqual((await page.locator('.practice-reference pre code').allTextContents()).map(x=>x.trim()),expected);
    await page.getByRole('tab',{name:'Quiz',exact:true}).click();
    const index=learning.quiz.findIndex(q=>q.id==='runtime-studio');
    for(const q of learning.quiz){const answer=q.id==='runtime-studio'?q.options.find(o=>o.id!==q.correct).id:q.correct;await page.locator(`input[name="quiz-${id}-${q.id}"][value="${answer}"]`).check()}
    await page.getByRole('button',{name:'Check my answers',exact:true}).click();
    await page.locator('.quiz-result').filter({hasText:`${learning.quiz.length-1} of ${learning.quiz.length} correct`}).waitFor();
    await page.getByRole('button',{name:`Review explanation for question ${index+1}`,exact:true}).click();
    await page.locator('.chapter-reading>h2').filter({hasText:learning.chapters.find(c=>c.id==='runtime-studio').title}).waitFor();
    await page.getByRole('tab',{name:'Quiz',exact:true}).click();await page.getByRole('button',{name:'Try again',exact:true}).click();
    for(const q of learning.quiz)await page.locator(`input[name="quiz-${id}-${q.id}"][value="${q.correct}"]`).check();
    await page.getByRole('button',{name:'Check my answers',exact:true}).click();await page.locator('.quiz-result').filter({hasText:`${learning.quiz.length} of ${learning.quiz.length} correct`}).waitFor();
    await page.getByRole('tab',{name:'Flashcards',exact:true}).click();await page.getByRole('button',{name:'Reveal flashcard answer',exact:true}).click();assert((await page.locator('.flashcard').innerText()).includes(learning.flashcards[0].back));
    await page.getByRole('tab',{name:'Notes',exact:true}).click();const note='Runtime studio review: '+authored.title;
    await page.getByLabel('Your notes & observations',{exact:true}).fill(note);await page.getByRole('button',{name:'Save notes',exact:true}).click();await page.getByRole('status').filter({hasText:'Notes saved'}).waitFor();await page.reload();assert.equal(await page.getByLabel('Your notes & observations',{exact:true}).inputValue(),note);
   }
   const files=await(await page.request.get(origin+'/api/programs/'+program.slug+'/capstone-files/')).json();
   for(const file of files)assert.equal(file.content,fs.readFileSync('backend/academy/content/capstones/'+program.slug+'/'+file.path,'utf8'));
   report.push({program:program.slug,lessons:program.lessons.length,chapters,studios,capstone_files:files.length});console.log('PASS reading and feedback:',report.at(-1));
  }
  for(const width of [390,320]){
   await page.setViewportSize({width,height:844});
   for(const program of source){
    const live=catalog.find(p=>p.slug===program.slug),index=program.lessons.findIndex(l=>l.resources.learning.chapters.some(c=>c.id==='runtime-studio'));
    for(const n of [index,program.lessons.findIndex(l=>l.resources.learning.capstone)]){
     const learning=program.lessons[n].resources.learning,id=live.lessons[n].id;
     await page.goto(origin+`/#/learn/${program.slug}/${id}`);await page.getByRole('tab',{name:'Lesson',exact:true}).click();await page.getByRole('article',{name:'Chapter reading'}).waitFor();
     const c=learning.chapters.findIndex(c=>c.id==='runtime-studio'||c.id==='capstone-build');await chapter(learning,c);
     await page.getByRole('button',{name:'Course contents',exact:true}).click();await page.getByRole('dialog').waitFor();await page.keyboard.press('Escape');await page.getByRole('dialog').waitFor({state:'hidden'});await fits();
     if(width===390&&n===index)await page.screenshot({path:`docs/screenshots/depth-${program.slug}-390.png`});
    }
   }
  }
  const anonymous=await browser.newContext(),preview=await anonymous.newPage();
  for(const program of source){await preview.goto(origin+'/#/preview/'+program.slug);await preview.getByRole('article',{name:'Chapter reading'}).waitFor();assert(!/Teaching credits|Source snapshot|MIT License/.test(await preview.locator('main').innerText()))}
  await anonymous.close();assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);
  fs.writeFileSync('docs/student-depth-browser.json',JSON.stringify({programs:report,desktop:1440,mobile:[390,320],wrong_answer_remediation:true,notes_persisted:true,preview_reading:true,errors,failed},null,2));
 }catch(error){console.error('Failed route',page.url(),failed);await page.screenshot({path:'/tmp/four-depth-failure.png'}).catch(()=>{});throw error}
 finally{await browser.close()}
})().catch(error=>{console.error(error);process.exitCode=1});
