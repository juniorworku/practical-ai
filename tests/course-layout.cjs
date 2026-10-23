const assert = require("node:assert/strict"),
  fs = require("node:fs");
const { chromium } = require(
  process.env.PLAYWRIGHT_MODULE ||
    "/Users/Junior/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright",
);
const origin = process.env.APP_URL || "http://127.0.0.1:8080";
const slugs = [
  "ai-agent-bootcamp",
  "ai-workshops",
  "freelancing-masterclass",
  "ai-engineering-12-week",
  "genai-accelerator",
  "terminal-tutor",
  "python-for-ai",
];
(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath:
      process.env.CHROME_EXECUTABLE ||
      "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  });
  const context = await browser.newContext({
      viewport: { width: 1440, height: 1000 },
    }),
    page = await context.newPage(),
    errors = [],
    failed = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("response", (r) => {
    if (r.url().includes("/api/") && r.status() >= 400)
      failed.push({ url: new URL(r.url()).pathname, status: r.status() });
  });
  try {
    await page.goto(origin);
    await page.locator(".program-card").first().waitFor();
    assert.equal(await page.locator(".program-card").count(), 7);
    assert.equal(
      await page
        .locator("body")
        .evaluate((e) => getComputedStyle(e).backgroundColor),
      "rgb(11, 16, 24)",
    );
    await page
      .getByLabel("Search programs and topics", { exact: true })
      .fill("Python for AI");
    assert.equal(await page.locator(".program-card").count(), 1);
    await page
      .getByLabel("Search programs and topics", { exact: true })
      .fill("");
    const catalog = (
      await (await page.request.get(origin + "/api/programs/")).json()
    ).filter((p) => slugs.includes(p.slug));
    assert.equal(catalog.length, 7);
    assert.equal(
      catalog.find((p) => p.slug === "python-for-ai").lessons.length,
      12,
    );
    await page.request.get(origin + "/api/auth/session/");
    const csrf = async () => ({
      "X-CSRFToken": (await context.cookies(origin)).find(
        (c) => c.name === "csrftoken",
      ).value,
    });
    const username = "course_layout_" + Date.now();
    const registry = "/tmp/academy-course-layout-users.json";
    const names = fs.existsSync(registry) ? JSON.parse(fs.readFileSync(registry)) : [];
    const legacy = "/tmp/academy-course-layout-user.json";
    if (fs.existsSync(legacy)) names.push(JSON.parse(fs.readFileSync(legacy)).username);
    names.push(username);
    fs.writeFileSync(registry, JSON.stringify([...new Set(names)]), {mode: 0o600});
    fs.writeFileSync(
      "/tmp/academy-course-layout-user.json",
      JSON.stringify({ username }),
      { mode: 0o600 },
    );
    assert.equal(
      (
        await page.request.post(origin + "/api/auth/session/register/", {
          headers: await csrf(),
          data: {
            username,
            email: username + "@example.com",
            password: "Synthetic-course-layout-4962!",
          },
        })
      ).status(),
      201,
    );
    for (const p of catalog)
      await page.request.post(origin + `/api/programs/${p.slug}/enroll/`, {
        headers: await csrf(),
      });
    await page.reload();
    await page.getByRole("button", { name: "Sign out", exact: true }).waitFor();
    for (const width of [1440, 390, 320]) {
      await page.setViewportSize({
        width,
        height: width === 1440 ? 1000 : 844,
      });
      if (width === 320) await page.emulateMedia({ reducedMotion: "reduce" });
      for (const program of catalog) {
        const id = program.lessons[0].id;
        await page.goto(origin + `/#/learn/${program.slug}/${id}`);
        await page
          .locator(".lesson-content>h1")
          .filter({ hasText: program.lessons[0].title })
          .waitFor();
        await page.getByRole("tab", { name: "Lesson", exact: true }).click();
        await page.getByRole("article", { name: "Chapter reading" }).waitFor();
        assert.equal(
          await page
            .getByRole("navigation", { name: "Program modules" })
            .getByRole("button")
            .count(),
          new Set(program.lessons.map((l) => l.module)).size,
        );
        if (width === 1440) {
          await page
            .getByLabel("Search lessons", { exact: true })
            .fill("zzzz-no-match");
          await page
            .getByRole("button", { name: "Clear lesson search", exact: true })
            .click();
          await page
            .getByRole("complementary", { name: "Course lessons" })
            .getByRole("button", {
              name: program.lessons[1].title,
              exact: true,
            })
            .click();
        } else {
          const trigger = page.getByRole("button", {
            name: "Course contents",
            exact: true,
          });
          await trigger.click();
          await page.getByRole("dialog").waitFor();
          await page.keyboard.press("Escape");
          await page.getByRole("dialog").waitFor({ state: "hidden" });
          assert.equal(
            await trigger.evaluate((e) => document.activeElement === e),
            true,
          );
          await trigger.click();
          const dialog = page.getByRole("dialog");
          await dialog
            .getByLabel("Search lessons", { exact: true })
            .fill(program.lessons[1].title);
          await dialog
            .getByRole("button", {
              name: program.lessons[1].title,
              exact: true,
            })
            .click();
          await dialog.waitFor({ state: "hidden" });
        }
        await page
          .locator(".lesson-content>h1")
          .filter({ hasText: program.lessons[1].title })
          .waitFor();
        await page.getByRole("tab", { name: "Lesson", exact: true }).click();
        await page.locator(".book-contents>summary").click();
        await page
          .getByRole("navigation", { name: "Lesson chapters" })
          .getByRole("button")
          .filter({ hasText: "Learn each concept step by step" })
          .click();
        await page
          .locator(".chapter-reading > h2")
          .filter({ hasText: "Learn each concept step by step" })
          .waitFor();
        const before = page.url();
        if (width === 1440) {
          const outline = page.getByRole("navigation", {
            name: "On this page",
            exact: true,
          });
          await outline.getByRole("button").first().click();
        } else {
          await page.locator(".mobile-reading-outline>summary").click();
          await page.locator(".mobile-reading-outline>button").first().click();
        }
        assert.equal(page.url(), before);
        assert(
          await page.evaluate(() =>
            document.activeElement?.id.startsWith("reading-"),
          ),
        );
        await page.getByRole("tab", { name: "Exercise", exact: true }).click();
        await page
          .getByRole("button", { name: "I’d like a hint", exact: true })
          .click();
        await page.locator(".hint-box").waitFor();
        await page.getByRole("tab", { name: "Quiz", exact: true }).click();
        const retry = page.getByRole("button", {name: "Try again", exact: true});
        if (await retry.isVisible()) await retry.click();
        for (const q of await page.locator(".quiz-question").all())
          await q.getByRole("radio").first().check();
        await page
          .getByRole("button", { name: "Check my answers", exact: true })
          .click();
        await page.locator(".quiz-result").waitFor();
        await page.getByRole("tab", { name: "Notes", exact: true }).click();
        const note = `${width} dark layout student note for ${program.slug}`;
        await page
          .getByLabel("Your notes & observations", { exact: true })
          .fill(note);
        await page
          .getByRole("button", { name: "Save notes", exact: true })
          .click();
        await page
          .getByRole("status")
          .filter({ hasText: "Notes saved" })
          .waitFor();
        await page.reload();
        await page
          .getByLabel("Your notes & observations", { exact: true })
          .waitFor();
        assert.equal(
          await page
            .getByLabel("Your notes & observations", { exact: true })
            .inputValue(),
          note,
        );
        assert(
          await page.evaluate(
            () => document.documentElement.scrollWidth <= innerWidth + 1,
          ),
          "overflow " + width + " " + program.slug,
        );
        await page.getByRole("tab", { name: "Lesson", exact: true }).click();
        if (program.slug === "python-for-ai") {
          await page.evaluate(() => scrollTo(0, 0));
          await page.screenshot({
            path: `docs/screenshots/course-redesign-${width}.png`,
          });
        }
        console.log(
          "PASS " +
            width +
            " " +
            program.title +
            ": module nav, sidebar/sheet, outline, exercise, quiz, saved notes.",
        );
      }
    }
    const python = catalog.find((p) => p.slug === "python-for-ai");
    for (const summary of python.lessons) {
      const lesson = await (
        await page.request.get(origin + `/api/lessons/${summary.id}/`)
      ).json();
      assert(lesson.resources.learning.chapters.length >= 5);
      assert(lesson.resources.learning.exercise.solution.includes("```python"));
      assert.equal(lesson.resources.learning.quiz.length, 5);
      assert(lesson.content.length > 5000);
    }
    assert.equal(
      (
        await (
          await page.request.get(
            origin + "/api/programs/python-for-ai/capstone-files/",
          )
        ).json()
      ).length,
      11,
    );
    assert.deepEqual(errors, []);
    assert.deepEqual(failed, []);
    console.log(
      "PASS all seven programs and all 12 advanced Python lesson contracts. Synthetic learner: " +
        username,
    );
  } catch (error) {
    console.error("FAILED", page.url(), failed);
    await page
      .screenshot({ path: "/tmp/course-layout-failure.png", fullPage: true })
      .catch(() => {});
    throw error;
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
