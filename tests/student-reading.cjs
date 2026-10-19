// Render every lesson chapter/exercise to detect missing code, truncated examples,
// and mismatches between published teaching and what the learner actually sees.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/Users/Junior/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const filter=new Set((process.env.REVIEW_LESSONS||'').split(',').filter(Boolean));
 const origin=process.env.APP_URL||'http://127.0.0.1:8080';
 const source=JSON.parse(fs.readFileSync(path.join(__dirname,'../backend/academy/starter_curriculum.json'),'utf8'));
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 page.setDefaultTimeout(15000);page.setDefaultNavigationTimeout(15000);
 const errors=[]; page.on('pageerror',e=>errors.push(e.message));
 try {
  const name='reading_'+Date.now();
  const registration=await page.request.post(origin+'/api/auth/register/',{data:{username:name,email:name+'@example.com',password:'Content-review-fixtures-947!'}});
  assert.equal(registration.status(),201);
  const {token}=await registration.json(); const headers={Authorization:'Token '+token};
  for(const program of source) assert.ok([200,201].includes((await page.request.post(origin+`/api/programs/${program.slug}/enroll/`,{headers})).status()));
  await page.addInitScript(token=>sessionStorage.setItem('academy-token',token),token);
  let chapters=0,lessons=0;
  for(const [programIndex,program] of source.entries()) {
   await page.goto(origin);
   await page.getByRole('button',{name:'My learning',exact:true}).first().click();
   await page.locator('.dashboard-course').filter({has:page.getByRole('heading',{name:program.title,exact:true})}).getByRole('button',{name:'Continue learning',exact:true}).click();
   for(let index=0;index<program.lessons.length;index++) {
    const id='BWF'[programIndex]+String(index+1).padStart(2,'0');
    if(filter.size && !filter.has(id))continue;
    const lesson=program.lessons[index], learning=lesson.resources.learning;
    console.log('Reading '+program.slug+' '+(index+1)+': '+lesson.title);
    await page.locator('.lesson-layout aside>button').nth(index).click();
    await page.getByRole('tab',{name:'Lesson',exact:true}).click();
    await page.getByRole('article',{name:'Chapter reading'}).getByRole('heading',{name:learning.chapters[0].title,exact:true}).waitFor();
    await page.locator('.book-contents>summary').click();
    const buttons=page.getByRole('navigation',{name:'Lesson chapters'}).getByRole('button');
    for(let i=0;i<learning.chapters.length;i++) {
     await buttons.nth(i).click();
     const expected=learning.chapters[i];
     await page.getByRole('article',{name:'Chapter reading'}).getByRole('heading',{name:expected.title,exact:true}).waitFor();
     const displayed=await page.locator('.chapter-reading .markdown-reader').innerText();
     assert.ok(displayed.length>200,lesson.title);
     const code=[...expected.body.matchAll(/^```[^\n]*\n([\s\S]*?)^```/gm)].map(match=>match[1].trim());
     const rendered=await page.locator('.chapter-reading pre code').allTextContents();
     assert.deepEqual(rendered.map(t=>t.trim()),code,lesson.title+' complete code fences');
     if(expected.id==='worked-implementation' && ['B04','B20','W06','F03'].includes(id)) {
      await page.screenshot({path:path.join(__dirname,`../docs/screenshots/review-${program.slug}-${index+1}.png`)});
     }
     chapters++;
    }
    await page.getByRole('tab',{name:'Exercise',exact:true}).click();
    const exercise=await page.locator('.inline-practice').innerText();
    assert.ok(exercise.includes('Make the targeted change') && exercise.includes('What to submit and check'));
    for(const criterion of learning.task.criteria) assert.ok(exercise.includes(criterion),lesson.title+' aligned criterion');
    await page.getByRole('tab',{name:'Questions',exact:true}).click();
    for(const question of learning.questions) await page.getByText(question.prompt,{exact:true}).waitFor();
    await page.getByRole('tab',{name:'Quiz',exact:true}).click();
    assert.equal(await page.getByRole('radio').count(),9);
    assert.equal(await page.locator('a[href*="github.com/rohitg00"]').count(),0);
    lessons++;
   }
  }
  assert.equal(lessons,filter.size||60);assert.deepEqual(errors,[]);
  console.log(`PASS: all ${lessons} lessons, ${chapters} rendered chapters, every code fence intact, exercises and questions aligned, three quizzes per session.`);
 } catch(error) {await page.screenshot({path:path.join(__dirname,'../docs/screenshots/reading-failure.png')});console.error((await page.locator('body').innerText()).slice(-2500));throw error;} finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
