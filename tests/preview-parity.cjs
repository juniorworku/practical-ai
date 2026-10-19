const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/Users/Junior/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const origin=process.env.APP_URL||'http://127.0.0.1:5173';
 const state=JSON.parse(fs.readFileSync(process.env.PRACTICE_SNAPSHOT||'/tmp/practical-ai-learning-state.json','utf8'));
 const headers={Authorization:'Token '+state.token};
 const preview=await(await fetch(origin+'/api/programs/')).json();
 const docker=await(await fetch('http://127.0.0.1:8080/api/programs/')).json();
 assert.deepEqual(preview,docker);
 assert.equal((await(await fetch(origin+'/api/health/')).json()).database,'postgresql');
 const saved=await(await fetch(origin+`/api/lessons/${state.lessonId}/practice/`,{headers})).json();assert.equal(saved.last_quiz.score,state.quizTotal);
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_EXECUTABLE||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000}});
  await page.addInitScript(token=>sessionStorage.setItem('academy-token',token),state.token);
  await page.goto(origin);
  await page.getByRole('button',{name:'My learning',exact:true}).first().click();
  await page.locator('.dashboard-course').filter({has:page.getByRole('heading',{name:'AI Agent Bootcamp',exact:true})}).getByRole('button',{name:'Continue learning',exact:true}).click();
  await page.locator('.lesson-layout aside>button').first().click();
  await page.getByRole('article',{name:'Chapter reading'}).getByRole('heading',{name:'The Agent Loop: Observe, Think, Act',exact:true}).waitFor();
  assert.equal(await page.locator('.book-contents').getAttribute('open'),null);
  await page.locator('.chapter-reading').scrollIntoViewIfNeeded();
  await page.screenshot({path:path.join(__dirname,'../docs/screenshots/book-reading-preview.png')});
  await page.getByRole('tab',{name:'Exercise',exact:true}).click();
  await page.locator('.inline-practice').getByRole('heading',{name:'Separate a draft from an action',exact:true}).waitFor();
  assert.equal(await page.getByRole('button',{name:/Download.*workbook/i}).count(),0);
  const expired=await browser.newPage();
  await expired.addInitScript(()=>sessionStorage.setItem('academy-token','expired-preview-token'));
  await expired.goto(origin);
  await expired.getByRole('dialog').waitFor();
  await expired.keyboard.press('Escape');
  await expired.locator('.program-card').first().waitFor();
  assert.equal(await expired.locator('.program-card').count(),4);
  await expired.close();
  console.log('PASS: Vite 5173 and Docker 8080 serve identical PostgreSQL course books and saved practice; the existing preview renders the actual chapter and inline exercise.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
