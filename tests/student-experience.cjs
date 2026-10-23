/* Student-facing regression audit: all six programs on desktop and narrow phones. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || '/Users/Junior/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const origin = process.env.APP_URL || 'http://127.0.0.1:8080';
(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: process.env.CHROME_EXECUTABLE || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
  const users = fs.existsSync(`/tmp/academy-student-ui-users${process.env.REVIEW_TAG || ''}.json`) ? JSON.parse(fs.readFileSync(`/tmp/academy-student-ui-users${process.env.REVIEW_TAG || ''}.json`)) : [];
  const errors = [], failures = [], report = [];
  let page;
  async function fits(label) {
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), 'Page overflows: ' + label);
    assert.equal(await page.locator('.global-error').count(), 0, label);
  }
  async function activity(name) {
    await page.getByRole('tab', { name, exact: true }).click();
    await page.getByRole('tabpanel', { name, exact: true }).waitFor();
    await fits(name);
  }
  try {
    for (const width of (process.env.REVIEW_WIDTHS || '1440,390,320').split(',').map(Number)) {
      const context = await browser.newContext({ viewport: { width, height: width === 1440 ? 1000 : 844 }, reducedMotion: width === 320 ? 'reduce' : 'no-preference' });
      page = await context.newPage();
      page.on('pageerror', e => errors.push(e.message));
      page.on('response', r => { if (r.url().includes('/api/') && r.status() >= 400) failures.push({ path: new URL(r.url()).pathname, status: r.status() }); });
      await page.goto(origin); await page.locator('.program-card').first().waitFor();
      const catalog = (await (await page.request.get(origin + '/api/programs/')).json()).filter(p => ['ai-agent-bootcamp','ai-workshops','freelancing-masterclass','ai-engineering-12-week','genai-accelerator','terminal-tutor','python-for-ai'].includes(p.slug));
      await page.request.get(origin + '/api/auth/session/');
      const csrf = async () => ({ 'X-CSRFToken': (await context.cookies(origin)).find(c => c.name === 'csrftoken').value });
      const username = 'student_ui_' + width + '_' + Date.now(); users.push(username);
      fs.writeFileSync(`/tmp/academy-student-ui-users${process.env.REVIEW_TAG || ''}.json`, JSON.stringify(users), { mode: 0o600 });
      assert.equal((await page.request.post(origin + '/api/auth/session/register/', { headers: await csrf(), data: { username, email: username + '@example.com', password: 'Synthetic-student-review-7951!' } })).status(), 201);
      for (const program of catalog) assert.equal((await page.request.post(origin + `/api/programs/${program.slug}/enroll/`, { headers: await csrf() })).status(), 201);
      await page.reload(); await page.getByRole('button', { name: 'Sign out', exact: true }).waitFor();
      for (const program of catalog.filter(p => !process.env.REVIEW_PROGRAMS || process.env.REVIEW_PROGRAMS.split(',').includes(p.slug))) {
        let chapterCount = 0;
        for (const index of [...new Set([0, Math.floor(program.lessons.length / 2), program.lessons.length - 1])]) {
          const summary = program.lessons[index];
          await page.goto(origin + `/#/learn/${program.slug}/${summary.id}`);
          await page.getByRole('tab', { name: 'Lesson', exact: true }).waitFor();
          await activity('Lesson');
          await page.getByRole('article', { name: 'Chapter reading' }).waitFor();
          const detail = await (await page.request.get(origin + `/api/lessons/${summary.id}/`)).json();
          const chapters = detail.resources.learning.chapters;
          for (let i = 0; i < chapters.length; i++) {
            await page.locator('.book-contents > summary').click();
            await page.getByRole('navigation', { name: 'Lesson chapters' }).getByRole('button').nth(i).click();
            const heading = page.locator('.chapter-reading > h2');
            await heading.filter({ hasText: chapters[i].title }).waitFor();
            assert.equal(await heading.evaluate(e => document.activeElement === e), true, 'Chapter heading receives focus');
            await page.waitForFunction(() => { const top = document.querySelector('.chapter-reading').getBoundingClientRect().top; return top >= 0 && (top < 80 || scrollY + innerHeight >= document.documentElement.scrollHeight - 2); });
            assert.equal(await page.locator('.book-contents').getAttribute('open'), null);
            assert((await page.locator('.chapter-reading .markdown-reader').innerText()).length > 100);
            await fits(program.slug + ' chapter ' + i); chapterCount++;
            if (i === 3 && index === 0) await page.screenshot({ path: `/tmp/student-ui-${width}-${program.slug}.png` });
          }
          await page.getByRole('button', { name: 'Begin the exercise', exact: true }).click();
          await page.getByRole('tabpanel', { name: 'Exercise', exact: true }).waitFor();
          assert.equal(await page.evaluate(() => document.activeElement?.getAttribute('role')), 'tabpanel');
          assert(await page.locator('.activity-panel').evaluate(e => e.getBoundingClientRect().top >= 0 && (e.getBoundingClientRect().top < 80 || scrollY + innerHeight >= document.documentElement.scrollHeight - 2)));
          if (index !== 0) continue;
          await page.getByRole('button', { name: 'I’d like a hint', exact: true }).click();
          assert((await page.locator('.hint-box').innerText()).length > 20);
          await fits('exercise and hint');
          await activity('Questions');
          await page.getByLabel('Reflection response', { exact: true }).first().fill('I would test the taught boundary using a fixed input, assert the expected output, and record latency, cost and context limitations.');
          await page.getByRole('button', { name: 'Save reflection', exact: true }).first().click();
          await page.getByRole('status').filter({ hasText: /Reflection saved|Practice autosaved/ }).waitFor();
          await activity('Quiz');
          for (const question of await page.locator('.quiz-question').all()) await question.getByRole('radio').first().check();
          await page.getByRole('button', { name: 'Check my answers', exact: true }).click();
          await page.locator('.quiz-result').waitFor();
          assert.equal(await page.locator('.quiz-feedback').count(), detail.resources.learning.quiz.length);
          await page.getByRole('button', { name: 'Try again', exact: true }).click();
          await page.reload(); await page.locator('.quiz-question').first().waitFor();
          assert.equal(await page.locator('.quiz-feedback').count(), 0, 'Retry must not restore earlier feedback');
          assert.equal(await page.getByRole('radio', { checked: true }).count(), 0);
          await page.locator('.quiz-question').first().getByRole('radio').last().check();
          await page.reload(); await page.locator('.quiz-question').first().waitFor();
          assert.equal(await page.getByRole('radio', { checked: true }).count(), 1);
          assert.equal(await page.locator('.quiz-feedback').count(), 0, 'Draft answers must not show earlier grading');
          for (const question of await page.locator('.quiz-question').all()) await question.getByRole('radio').first().check();
          await page.getByRole('button', { name: 'Check my answers', exact: true }).click(); await page.locator('.quiz-result').waitFor();
          const review = page.getByRole('button', { name: 'Review explanation for question 1', exact: true });
          if (await review.count()) { await review.click(); assert.equal(await page.evaluate(() => document.activeElement?.getAttribute('role')), 'tabpanel'); await page.locator('.chapter-reading > h2').filter({ hasText: 'Learn each concept step by step' }).waitFor(); }
          await activity('Flashcards'); await page.getByRole('button', { name: 'Reveal flashcard answer', exact: true }).click(); await page.getByRole('button', { name: 'Next flashcard', exact: true }).click();
          await activity('Practical task'); await page.locator('.acceptance-checklist').waitFor();
          const evidence = page.getByLabel('Your evidence & observations', { exact: true });
          const observation = 'Student audit draft: fixed inputs, observed outputs and failure cases are recorded here. This is a UI check rather than an actual submitted project.';
          await evidence.fill(observation); await page.getByRole('button', { name: 'Save draft', exact: true }).click(); await page.getByRole('status').filter({ hasText: 'Task draft saved' }).waitFor();
          await page.reload(); await evidence.waitFor(); assert.equal(await evidence.inputValue(), observation);
          await activity('Notes'); const note = `${width}: ${program.title} — student notes retained across reload and lesson navigation.`;
          await page.getByLabel('Your notes & observations', { exact: true }).fill(note); await page.getByRole('button', { name: 'Save notes', exact: true }).click(); await page.getByRole('status').filter({ hasText: 'Notes saved' }).waitFor();
          await page.reload(); await page.getByLabel('Your notes & observations', { exact: true }).waitFor(); assert.equal(await page.getByLabel('Your notes & observations', { exact: true }).inputValue(), note);
          await activity('Get help'); await page.locator('.lesson-help').waitFor();
          await page.getByRole('button', { name: 'Next lesson', exact: true }).click();
          await page.locator('.lesson-content > h1').filter({ hasText: program.lessons[1].title }).waitFor();
          await page.waitForFunction(() => document.activeElement?.matches('.lesson-content > h1'));
        }
        report.push({ width, program: program.slug, lessons: 3, chapters: chapterCount, activities: true });
        console.log(`PASS ${width}px: ${program.title}; ${chapterCount} chapters across first/middle/final lessons, exercise, reflection, quiz retries, flashcards, task draft, notes and next-lesson focus.`);
      }
      await context.close();
    }
    assert.deepEqual(errors, []); assert.deepEqual(failures, []);
    fs.writeFileSync(`/tmp/academy-student-ui-report${process.env.REVIEW_TAG || ''}.json`, JSON.stringify({ report, errors, failures }, null, 2));
    console.log('PASS: all requested programs and viewport widths; no JavaScript errors or failed API responses.');
  } catch (error) {
    console.error('At', page?.url(), 'API failures', failures);
    await page?.screenshot({ path: '/tmp/academy-student-ui-failure.png', fullPage: true }).catch(() => {});
    throw error;
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
