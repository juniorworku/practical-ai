/* Live-mail check: use only a recipient you control. No SMTP secret is read here.
 * 1. RESET_E2E_EMAIL=you+academy-test@example.com node tests/password-reset-email.cjs request
 * 2. Save the link received in that inbox to /tmp/academy-reset-link (mode 0600).
 * 3. node tests/password-reset-email.cjs confirm
 */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/Users/Junior/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const origin=process.env.APP_URL||'http://127.0.0.1:8080';
const stateFile=process.env.RESET_E2E_STATE||'/tmp/academy-password-reset-e2e.json';
const linkFile=process.env.RESET_E2E_LINK_FILE||'/tmp/academy-reset-link';
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_EXECUTABLE||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 try{
  if(process.argv[2]==='request'){
   const email=process.env.RESET_E2E_EMAIL;assert(email,'Set RESET_E2E_EMAIL to an inbox you control.');
   const username='mail_delivery_'+Date.now(),password='Synthetic-course-password-3258!';
   const context=await browser.newContext();const page=await context.newPage();await page.goto(origin);
   await page.request.get(origin+'/api/auth/session/');
   const csrf=()=>context.cookies(origin).then(rows=>({'X-CSRFToken':rows.find(row=>row.name==='csrftoken').value}));
   const registration=await page.request.post(origin+'/api/auth/session/register/',{headers:await csrf(),data:{username,email,password}});assert.equal(registration.status(),201);
   const catalog=await(await page.request.get(origin+'/api/programs/')).json();const program=catalog.find(row=>row.slug==='ai-agent-bootcamp');
   assert.equal((await page.request.post(origin+`/api/programs/${program.slug}/enroll/`,{headers:await csrf()})).status(),201);
   const lesson=program.lessons[0].id;assert((await page.request.post(origin+`/api/lessons/${lesson}/complete/`,{headers:await csrf()})).ok());
   fs.writeFileSync(stateFile,JSON.stringify({username,email,password,lesson,storageState:await context.storageState()}),{mode:0o600});
   const recovery=await browser.newContext();const form=await recovery.newPage();await form.goto(origin);
   await form.getByRole('button',{name:'Log in',exact:true}).click();await form.getByRole('button',{name:'Forgot password?',exact:true}).click();
   await form.getByLabel('Account email',{exact:true}).fill(email);await form.getByRole('button',{name:'Send recovery email',exact:true}).click();
   await form.getByRole('status').filter({hasText:'If an account matches'}).waitFor();
   console.log('Recovery requested through the browser. Confirm receipt in the controlled inbox. Synthetic learner: '+username);
  }else if(process.argv[2]==='confirm'){
   const state=JSON.parse(fs.readFileSync(stateFile,'utf8')),link=fs.readFileSync(linkFile,'utf8').trim();
   assert(link.startsWith(origin+'/#/reset/'),'Reset origin must match the running app.');
   const context=await browser.newContext();const page=await context.newPage();const errors=[];page.on('pageerror',error=>errors.push(error.message));await page.goto(link);
   await page.getByLabel('New password',{exact:true}).fill('Replacement-course-password-9583!');await page.getByRole('button',{name:'Set new password',exact:true}).click();
   await page.getByRole('status').filter({hasText:'Password updated.'}).waitFor();await page.getByRole('button',{name:'Return to login',exact:true}).click();
   await page.getByLabel('Username',{exact:true}).fill(state.email);await page.getByLabel('Password',{exact:true}).fill('Replacement-course-password-9583!');await page.getByRole('dialog').getByRole('button',{name:'Log in',exact:true}).click();
   await page.getByRole('heading',{name:`Welcome back, ${state.username}.`,exact:true}).waitFor();
   const me=await(await page.request.get(origin+'/api/me/')).json();assert(me.completed.includes(state.lesson),'Reset must preserve saved learning progress.');
   const old=await browser.newContext({storageState:state.storageState});assert.equal((await old.request.get(origin+'/api/me/')).status(),401);
   const csrf=(await old.cookies(origin)).find(row=>row.name==='csrftoken').value;
   assert.equal((await old.request.post(origin+'/api/auth/session/login/',{headers:{'X-CSRFToken':csrf},data:{username:state.username,password:state.password}})).status(),400);
   const [,uid,token]=new URL(link).hash.split('/').slice(1);
   const anonymous=await browser.newContext();assert.equal((await anonymous.request.post(origin+'/api/auth/password-reset/confirm/',{data:{uid,token,password:'Another-course-password-9583!'}})).status(),400);
   assert.deepEqual(errors,[]);console.log('PASS: delivered email link opened in browser; password reset and new-email login succeeded; old password/session rejected; link reuse rejected; learning progress preserved.');
  }else throw new Error('Choose request or confirm.');
 }finally{await browser.close()}
})().catch(error=>{console.error(error.message);process.exit(1)});
