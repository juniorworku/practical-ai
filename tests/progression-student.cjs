const {chromium}=require('/Users/Junior/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const root=path.join(__dirname,'..'),origin='http://127.0.0.1:8080';
const sources=[...JSON.parse(fs.readFileSync(path.join(root,'backend/academy/starter_curriculum.json'))),...JSON.parse(fs.readFileSync(path.join(root,'backend/academy/content/reviewed_workshop.json')))];
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 try{
  const page=await browser.newPage({reducedMotion:'reduce'}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  const registration=await page.request.post(origin+'/api/auth/register/',{data:{username:'path-'+Date.now(),email:'path-'+Date.now()+'@example.invalid',password:'Private-test-password-421!'}});assert.equal(registration.status(),201);
  const {token}=await registration.json(),headers={Authorization:'Token '+token};
  for(const p of sources)assert.ok((await page.request.post(origin+'/api/programs/'+p.slug+'/enroll/',{headers})).ok());
  await page.addInitScript(t=>sessionStorage.setItem('academy-token',t),token);
  const catalog=await(await page.request.get(origin+'/api/programs/')).json();let sessions=0,projects=0;
  for(const source of sources){
   const live=catalog.find(p=>p.slug===source.slug);assert.equal(live.progression.entry,source.lessons[0].resources.learning.progression.entry);
   for(let i=0;i<source.lessons.length;i++){
    assert.equal(live.lessons[i].title,source.lessons[i].title);
    const response=await page.request.get(origin+`/api/lessons/${live.lessons[i].id}/`,{headers});assert.equal(response.status(),200);
    const published=(await response.json()).resources.learning;
    assert.equal(published.revision,source.lessons[i].resources.learning.revision);
    assert.deepEqual(published.progression,source.lessons[i].resources.learning.progression);sessions++;
   }
   await page.goto(origin);await page.getByRole('button',{name:'My learning',exact:true}).first().click();
   const card=page.locator('.dashboard-course').filter({has:page.getByRole('heading',{name:source.title,exact:true})});
   await card.getByRole('button',{name:'View program syllabus'}).click();
   await page.getByRole('region',{name:'Program preparation'}).getByText(live.progression.entry,{exact:true}).waitFor();
   if(source.slug==='genai-accelerator'){
    for(const details of await page.locator('.course-module').all())await details.evaluate(el=>el.open=true);
    const actual=await page.locator('.course-module ol li>span').allTextContents();
    assert.deepEqual(actual.map(t=>t.trim()),source.lessons.map(l=>l.title));
   }
   await page.getByRole('button',{name:'Start this program',exact:true}).click();
   const chosen=source.lessons.filter(l=>l.resources.learning.progression.coverage.length);
   for(const lesson of [source.lessons[0],...chosen]){
    const index=source.lessons.indexOf(lesson);await page.locator('.lesson-layout aside>button').nth(index).click();
    await page.getByRole('article',{name:'Chapter reading'}).getByRole('heading',{name:'Learning progression and project preparation',exact:true}).waitFor();
    if(lesson.resources.learning.progression.coverage.length){
     await page.getByRole('heading',{name:'Taught-to-project evidence map',exact:true}).waitFor();
     const text=await page.getByRole('article',{name:'Chapter reading'}).innerText();
     for(const group of lesson.resources.learning.progression.coverage)assert.ok(text.includes(group.requirement));
     await page.getByRole('tab',{name:'Practical task',exact:true}).click();
     await page.getByText('Project evidence traces each mapped capability to its taught lesson, retains its negative check, and records the combined path with unresolved or untested boundaries explicitly labeled.',{exact:true}).waitFor();
     projects++;
    }
   }
   console.log('PASS learner entry, lesson path and project maps: '+source.slug);
  }
  await page.setViewportSize({width:390,height:844});
  await page.getByRole('tab',{name:'Lesson',exact:true}).click();
  await page.screenshot({path:path.join(root,'docs/screenshots/progression-mobile.png')});
  assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(root,'docs/progression-browser.json'),JSON.stringify({programs:sources.length,sessions,projects,source_parity:true,entry_requirements:true,interleaved_outline:true,console_errors:errors},null,2));
  console.log(`PASS ${sessions} served sessions, ${projects} project chapters and rubrics, all six entry panels, interleaved outline and mobile view.`);
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
