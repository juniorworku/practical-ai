const assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/Users/Junior/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{const b=await chromium.launch({headless:true,executablePath:process.env.CHROME_EXECUTABLE||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});try{
 const p=await b.newPage();const origin=process.env.APP_URL||'http://127.0.0.1:8080';
 await p.goto(origin+'/admin/login/');
 await p.getByLabel('Username:').fill('nonexistent-admin-fixture');
 await p.getByLabel('Password:').fill('Deliberately-invalid-password');
 const response=p.waitForResponse(r=>r.url().includes('/admin/login/')&&r.request().method()==='POST');
 await p.getByRole('button',{name:'Log in',exact:true}).click();
 assert.equal((await response).status(),200);
 await p.getByText('Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive.').waitFor();
 assert.equal((await p.request.get(origin+'/static/admin/css/base.css')).status(),200);
 console.log('PASS: Django admin login handles CSRF correctly through port-8080 proxy and Nginx serves collected static assets.');
}finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
