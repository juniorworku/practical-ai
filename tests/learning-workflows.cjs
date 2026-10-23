const assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/Users/Junior/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const origin=process.env.APP_URL||'http://127.0.0.1:8080';
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_EXECUTABLE||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const context=await browser.newContext({viewport:{width:1440,height:1000}});
 const page=await context.newPage();const errors=[];page.on('pageerror',error=>errors.push(error.message));page.on('console',message=>{if(message.type()==='error')console.log('Browser:',message.text().slice(0,1000))});
 try{
  await page.goto(origin+'/#/programs/ai-agent-bootcamp');
  await page.getByRole('button',{name:'Preview a full lesson',exact:true}).click();
  await page.getByRole('heading',{name:'Enforce the read-only task boundary',exact:true}).waitFor();
  assert.match(page.url(),/#\/preview\/ai-agent-bootcamp/);
  const preview=await(await page.request.get(origin+'/api/programs/ai-agent-bootcamp/preview/')).json();
  await page.getByRole('button',{name:'Run tests',exact:true}).click();
  await page.locator('.lab-results .failed').first().waitFor({timeout:35000});
  assert.equal(await page.locator('.lab-results .failed').count(),4);
  await page.getByLabel('Python solution',{exact:true}).fill(preview.lab.solution);
  await page.getByRole('button',{name:'Run tests',exact:true}).click();
  await page.locator('.lab-results .passed').first().waitFor({timeout:35000});
  assert.equal(await page.locator('.lab-results .passed').count(),4);
  console.log('Public preview: actual Python failure and success feedback passed');
  await page.goBack();await page.getByRole('button',{name:'Preview a full lesson',exact:true}).waitFor();
  await page.goForward();await page.getByRole('heading',{name:'Enforce the read-only task boundary',exact:true}).waitFor();
  await page.getByRole('button',{name:'Join for free and save progress',exact:true}).click();
  const username='workflow_'+Date.now();
  await page.getByLabel('Username',{exact:true}).fill(username);
  await page.getByLabel('Email address',{exact:true}).fill(username+'@example.com');
  await page.getByLabel('Password',{exact:true}).fill('Practical-workflow-test-password-859!');
  await page.getByLabel('Confirm password',{exact:true}).fill('Practical-workflow-test-password-859!');
  await page.getByRole('button',{name:'Create free account',exact:true}).click();
  await page.getByRole('tab',{name:'Notes',exact:true}).waitFor();
  const token=await page.evaluate(()=>sessionStorage.getItem('academy-token'));
  const headers=token?{Authorization:'Token '+token}:{'X-CSRFToken':(await context.cookies(origin)).find(cookie=>cookie.name==='csrftoken').value};
  const catalog=await(await page.request.get(origin+'/api/programs/')).json();
  const program=catalog.find(p=>p.slug==='ai-agent-bootcamp');
  const first=program.lessons[0];
  assert.match(page.url(),new RegExp('#/learn/ai-agent-bootcamp/'+first.id));
  // Leave before debounce fires: the recovery draft must survive component unmount.
  await page.getByRole('tab',{name:'Notes',exact:true}).click();
  const note='A saved learning observation: unknown requests fail closed; human review does not approve a refund.';
  await page.getByLabel('Your notes & observations',{exact:true}).fill(note);
  await page.getByRole('button',{name:'Next lesson',exact:true}).click();
  await page.getByRole('heading',{name:program.lessons[1].title,exact:true}).waitFor();
  await page.locator('.lesson-layout aside>button').first().click();
  await page.getByRole('tab',{name:'Notes',exact:true}).click();
  await assert.equal(await page.getByLabel('Your notes & observations',{exact:true}).inputValue(),note);
  await page.getByRole('status').filter({hasText:'Notes saved'}).waitFor();
  assert.equal((await(await page.request.get(origin+`/api/lessons/${first.id}/`,{headers})).json()).notes,note);
  // Practice also recovers and syncs after leaving immediately.
  await page.getByRole('tab',{name:'Questions',exact:true}).click();
  const reflection='I would choose a fixed workflow until an observed failure requires a bounded agent loop. Scope is explicit.';
  await page.getByLabel('Reflection response',{exact:true}).first().fill(reflection);
  await page.getByRole('button',{name:'Next lesson',exact:true}).click();
  await page.getByRole('heading',{name:program.lessons[1].title,exact:true}).waitFor();
  await page.locator('.lesson-layout aside>button').first().click();
  await page.getByRole('tab',{name:'Questions',exact:true}).click();
  await page.getByLabel('Reflection response',{exact:true}).first().waitFor();
  assert.equal(await page.getByLabel('Reflection response',{exact:true}).first().inputValue(),reflection);
  await page.getByRole('status').filter({hasText:'Practice autosaved'}).waitFor();
  // Chapter and direct route persist across full reload.
  await page.getByRole('tab',{name:'Lesson',exact:true}).click();
  await page.locator('.book-contents>summary').click();
  await page.getByRole('navigation',{name:'Lesson chapters'}).getByRole('button').nth(2).click();
  const chapterUrl=page.url();assert.match(chapterUrl,/chapter=concept-tutorial/);
  await page.reload();
  await page.getByRole('article',{name:'Chapter reading'}).waitFor();
  assert.match(await page.locator('.chapter-caption').innerText(),/CHAPTER 3/);
  assert.equal(page.url(),chapterUrl);
  console.log('Notes, reflections, lesson URL and chapter resume persisted through API and reload');
  await page.getByRole('tab',{name:'Python lab',exact:true}).click();
  await page.getByLabel('Python solution',{exact:true}).fill(preview.lab.solution);
  await page.getByRole('button',{name:'Run tests',exact:true}).click();
  await page.locator('.lab-results .passed').first().waitFor({timeout:35000});
  await page.waitForFunction(async(id)=>{const token=sessionStorage.getItem('academy-token');const data=await(await fetch('/api/me/',{headers:token?{Authorization:'Token '+token}:{}})).json();return data.progress.lab_passed.includes(id)},first.id);
  await page.getByText('Browser checks: passed · browser-reported',{exact:true}).waitFor();
  // A sandboxed program cannot contact an academy API.
  await page.getByLabel('Python solution',{exact:true}).fill(`import js\ntry:\n    req = js.XMLHttpRequest.new()\n    req.open("GET", "${origin}/api/health/", False)\n    req.send()\n    print("UNEXPECTED API ACCESS")\nexcept Exception:\n    print("Sandbox API access blocked")\n`+preview.lab.solution);
  await page.getByRole('button',{name:'Run tests',exact:true}).click();
  await page.getByText('Sandbox API access blocked',{exact:true}).waitFor({timeout:35000});
  assert.equal(await page.getByText('UNEXPECTED API ACCESS',{exact:true}).count(),0);
  // Stop a runaway function; the main UI must remain responsive.
  await page.getByLabel('Python solution',{exact:true}).fill('while True:\n    pass\n');
  await page.getByRole('button',{name:'Run tests',exact:true}).click();
  await page.getByRole('button',{name:'Stop execution',exact:true}).click();
  await page.getByText('Stopped. Your code draft is retained.',{exact:true}).waitFor();
  console.log('Authenticated browser lab saved; sandbox API boundary and stop control passed');
  // Run the other two authored labs in the actual Python browser runtime.
  for(const index of [2,3]){
   await page.locator('.lesson-layout aside>button').nth(index).click();
   await page.getByRole('heading',{name:program.lessons[index].title,exact:true}).waitFor();
   await page.getByRole('tab',{name:'Python lab',exact:true}).click();
   const detail=await(await page.request.get(origin+`/api/lessons/${program.lessons[index].id}/`,{headers})).json();
   await page.getByLabel('Python solution',{exact:true}).fill(detail.lab.solution);
   await page.getByRole('button',{name:'Run tests',exact:true}).click();
   await page.locator('.lab-results .passed').first().waitFor({timeout:35000});
   assert.equal(await page.locator('.lab-results .passed').count(),detail.lab.checks.length);
  }
  await page.locator('.lesson-layout aside>button').first().click();
  await page.getByRole('heading',{name:program.lessons[0].title,exact:true}).waitFor();
  console.log('All three Bootcamp labs executed successfully in browser Python');
  // A project is awaiting human review, never automatically approved.
  await page.getByRole('tab',{name:'Practical task',exact:true}).click();
  await page.getByLabel('Artifact or repository URL',{exact:true}).fill('https://example.com/student/synthetic-agent');
  await page.getByLabel('Commit or release identifier',{exact:true}).fill('test-release-1');
  await page.getByLabel('Evidence and reproduction steps',{exact:true}).fill('I ran all four scope checks with synthetic labels in the browser. Unknown requests stayed out of scope. No refund action or live provider call occurred.');
  for(const label of ['Latency: measured value, method and conditions','Cost: measured usage or explicit offline / unmeasured status','Quality: metric, score and dataset size','Evaluation: dataset / test revision and observed failures','Context: selection, limits, truncation and caching','Limitations: deployment, failure recovery and untested claims'])await page.getByLabel(label,{exact:true}).fill('Offline synthetic evidence only; no production measurement claimed.');
  await page.getByRole('button',{name:'Submit project revision',exact:true}).click();
  await page.getByText('Revision submitted for human review. This is not an automatic pass.',{exact:true}).waitFor();
  await page.getByText('Browse the reference capstone files',{exact:true}).click();
  await page.getByRole('button',{name:'Load reference files',exact:true}).click();
  await page.getByRole('button',{name:'core.py',exact:true}).click();
  await page.locator('.capstone-files').getByRole('heading',{name:'core.py',exact:true}).waitFor();
  const submissions=await(await page.request.get(origin+`/api/lessons/${first.id}/submissions/`,{headers})).json();
  assert.equal(submissions[0].review_status,'awaiting_review');
  await page.getByRole('tab',{name:'Get help',exact:true}).click();
  await page.getByRole('button',{name:'Show next guiding question',exact:true}).click();
  await page.getByLabel('Expected result, actual result and what you tried',{exact:true}).fill('Expected the unknown label to fail closed. Actual result was draft. I compared the fallback branch with the named request branches.');
  await page.getByRole('button',{name:'Post lesson question',exact:true}).click();
  await page.getByText('Question posted to this lesson.',{exact:true}).waitFor();
  await page.locator('.workspace-nav').getByRole('button',{name:'My learning',exact:true}).click();
  await page.getByLabel('Your goal',{exact:true}).selectOption('agents');
  for(const value of ['a','b','c']){const index=['a','b','c'].indexOf(value);await page.locator('.learning-hub fieldset').nth(index).locator('input').nth(index).check()}
  await page.getByRole('button',{name:'Save my learning plan',exact:true}).click();
  await page.getByText('Learning plan saved. Recommendations are guidance, not enrollment requirements.',{exact:true}).waitFor();
  await page.getByRole('button',{name:'Reveal answer',exact:true}).click();
  await page.getByRole('button',{name:'good',exact:true}).click();
  const plan=await(await page.request.get(origin+'/api/learning-plan/',{headers})).json();assert.equal(plan.goal,'agents');
  await page.setViewportSize({width:390,height:844});
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Learning dashboard must fit mobile width');
  await page.screenshot({path:'docs/screenshots/learning-workflow-mobile.png',fullPage:true});
  await page.setViewportSize({width:1440,height:1000});
  await page.screenshot({path:'docs/screenshots/learning-workflow-dashboard.png',fullPage:true});
  assert.deepEqual(errors,[]);
  console.log('Project evidence, lesson help, diagnostic plan, scheduled recall and mobile checks passed');
  console.log('All learning workflow checks passed against PostgreSQL');
 }catch(error){console.log('Runner state:',await page.locator('.browser-lab').innerText().catch(()=>''));await page.screenshot({path:'docs/screenshots/learning-workflow-failure.png',fullPage:true}).catch(()=>{});throw error}finally{await browser.close()}
})().catch(error=>{console.error(error);process.exit(1)});
