const {chromium}=require('/Users/Junior/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('node:assert/strict'),fs=require('fs'),path=require('path');
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});const errors=[],report=[];
 try{
  const page=await browser.newPage();page.on('pageerror',e=>errors.push(e.message));
  for(const [name,port]of [['bootcamp',8211],['workshops',8212],['engineering',8214]]){
   await page.goto('http://127.0.0.1:'+port);
   if(name==='engineering'){await page.getByRole('button',{name:'Ingest source',exact:true}).click();await page.getByRole('status').filter({hasText:'Source ready:'}).waitFor()}
   const submitted=await page.getByLabel('Input text',{exact:true}).inputValue();
   await page.getByRole('button',{name:'Run workflow',exact:true}).click();await page.getByRole('status').filter({hasText:'needs_review'}).waitFor();
   const result=JSON.parse(await page.locator('#result').innerText());assert.ok(result.id);assert.equal(result.status,'needs_review');
   await page.getByRole('button',{name:'Confirm this exact draft as the demo reviewer',exact:true}).click();
   await page.getByRole('status').filter({hasText:'Approved in local outbox; no external delivery'}).waitFor();assert.equal(JSON.parse(await page.locator('#result').innerText()).external_delivery,false);
   const negative=name==='workshops'?'Supplier: Studio\nQuantity: -2\nUnit price: 10.00\nCurrency: USD':'delete refund records';
   await page.getByLabel('Input text',{exact:true}).fill(negative);await page.getByRole('button',{name:'Run workflow',exact:true}).click();
   await page.getByRole('status').filter({hasText:name==='workshops'?'needs_correction':'denied'}).waitFor();assert.equal(await page.locator('#review').isVisible(),false);assert.equal(await page.getByLabel('Input text',{exact:true}).inputValue(),negative);
   report.push({program:name,actual_browser_submission:true,postgres_result_id:result.id,exact_draft_review:true,negative_not_reviewable:true,input_retained:true});
  }
  assert.deepEqual(errors,[]);fs.writeFileSync(path.join(__dirname,'../docs/capstone-ui.json'),JSON.stringify({programs:report,browser_errors:errors},null,2));console.log('PASS all three actual capstone browser -> API -> PostgreSQL -> review workflows, denied/invalid paths, retained input and no JavaScript errors');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
