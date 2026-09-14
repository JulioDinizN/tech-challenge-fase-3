import { mkdir, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const repoRoot = path.resolve(path.dirname(__filename), "../..");
const reportHtmlPath = path.join(repoRoot, "docs", "report.html");
const outputDir = path.join(repoRoot, "dist");
const outputPath = path.join(outputDir, "delivery-report.pdf");

async function ensureFileExists(filePath, label) {
  try {
    const stats = await stat(filePath);
    if (!stats.isFile()) {
      throw new Error(`${label} is not a file: ${filePath}`);
    }
  } catch (error) {
    if (error.code === "ENOENT") {
      throw new Error(`${label} was not found: ${filePath}`);
    }
    throw error;
  }
}

async function loadPlaywright() {
  try {
    return await import("playwright");
  } catch (error) {
    if (error.code === "ERR_MODULE_NOT_FOUND") {
      throw new Error(
        "Playwright is not installed. Run `npm install` before `npm run report:pdf`."
      );
    }
    throw error;
  }
}

async function waitForStableReport(page) {
  await page.evaluate(async () => {
    if (document.fonts?.ready) {
      await document.fonts.ready;
    }

    await Promise.all(
      Array.from(document.images).map((image) => {
        if (image.complete) {
          return undefined;
        }

        return new Promise((resolve) => {
          image.addEventListener("load", resolve, { once: true });
          image.addEventListener("error", resolve, { once: true });
        });
      })
    );
  });

  await page.waitForTimeout(250);
}

async function renderPdf() {
  await ensureFileExists(reportHtmlPath, "Report HTML");
  await mkdir(outputDir, { recursive: true });

  const { chromium } = await loadPlaywright();
  const reportUrl = pathToFileURL(reportHtmlPath).href;

  let browser;
  try {
    browser = await chromium.launch({ headless: true });
  } catch (error) {
    const missingBrowser =
      error.message?.includes("Executable doesn't exist") ||
      error.message?.includes("Please run the following command");

    if (missingBrowser) {
      throw new Error(
        "Playwright Chromium is not installed. Run `npm run report:install`, then run `npm run report:pdf` again."
      );
    }

    throw error;
  }

  try {
    const page = await browser.newPage({ viewport: { width: 1240, height: 1754 } });
    await page.goto(reportUrl, { waitUntil: "networkidle" });
    await page.emulateMedia({ media: "print" });
    await waitForStableReport(page);

    await page.pdf({
      path: outputPath,
      format: "A4",
      landscape: false,
      printBackground: true,
      preferCSSPageSize: true
    });
  } finally {
    await browser.close();
  }

  console.log(`Generated ${path.relative(repoRoot, outputPath)}`);
}

renderPdf().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
