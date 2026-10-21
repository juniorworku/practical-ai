const assert=require('node:assert/strict'),fs=require('fs'),path=require('path'),crypto=require('crypto');
const {chromium}=require('/Users/Junior/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.join(__dirname,'..'),origin='http://127.0.0.1:8080';
const programs=[...JSON.parse(fs.readFileSync(path.join(root,'backend/academy/starter_curriculum.json'))),...JSON.parse(fs.readFileSync(path.join(root,'backend/academy/content/reviewed_workshop.json')))];
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 try{
  const page=await browser.newPage({reducedMotion:'reduce'}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  const name='capstudent'+Date.now();const response=await page.request.post(origin+'/api/auth/register/',{data:{username:name,email:name+'@example.invalid',password:'Student-review-private-947!'}});assert.equal(response.status(),201);
  const {token}=await response.json(),headers={Authorization:'Token '+token};await page.addInitScript(t=>sessionStorage.setItem('academy-token',t),token);
  const catalog=await(await page.request.get(origin+'/api/programs/')).json();let files=0,chapters=0;
  for(const source of programs){
   assert.ok((await page.request.post(origin+'/api/programs/'+source.slug+'/enroll/',{headers})).ok());
   const final=source.lessons.find(l=>l.resources.learning.capstone),live=catalog.find(p=>p.slug===source.slug),index=source.lessons.indexOf(final);
   const served=await(await page.request.get(origin+`/api/lessons/${live.lessons[index].id}/`,{headers})).json();assert.equal(served.resources.learning.revision,final.resources.learning.revision);
   assert.deepEqual(served.resources.learning.capstone,final.resources.learning.capstone);
   for(const [name,digest]of Object.entries(served.resources.learning.capstone.files)){
    const bytes=fs.readFileSync(path.join(root,'backend/academy/content/capstones',source.slug,name));assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),digest);files++;
   }
   await page.goto(origin);await page.getByRole('button',{name:'My learning',exact:true}).first().click();
   await page.locator('.dashboard-course').filter({has:page.getByRole('heading',{name:source.title,exact:true})}).getByRole('button',{name:'Continue learning',exact:true}).click();
   await page.locator('.lesson-layout aside>button').nth(index).click();
   await page.getByRole('article',{name:'Chapter reading'}).getByRole('heading',{name:'Learning progression and project preparation',exact:true}).waitFor();
   await page.locator('.book-contents>summary').click();
   await page.getByRole('navigation',{name:'Lesson chapters'}).getByRole('button').filter({hasText:'Build the complete final project from these files'}).click();
   await page.getByRole('article',{name:'Chapter reading'}).getByRole('heading',{name:'Complete project files — no omitted application imports',exact:true}).waitFor();
   const blocks=await page.locator('.chapter-reading pre code').allTextContents();
   for(const name of Object.keys(final.resources.learning.capstone.files))if(name!=='README.md'){
    const expected=fs.readFileSync(path.join(root,'backend/academy/content/capstones',source.slug,name),'utf8').trim();assert.ok(blocks.some(b=>b.trim()===expected),source.slug+'/'+name);
   }
   await page.getByRole('tab',{name:'Practical task',exact:true}).click();
   await page.getByText('The complete independent capstone runs from the published files; actual checks, negative cases and required restart/restore evidence are retained, with untested claims labeled.',{exact:true}).waitFor();
   chapters++;console.log('PASS published complete capstone:',source.slug);
  }
  assert.deepEqual(errors,[]);fs.writeFileSync(path.join(root,'docs/capstone-published.json'),JSON.stringify({programs:6,chapters,files,served_revisions_match:true,inline_code_matches_files:true,browser_errors:errors},null,2));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
