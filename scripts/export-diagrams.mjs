import { access, stat } from "node:fs/promises";
import path from "node:path";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { fileURLToPath } from "node:url";

const execFileAsync = promisify(execFile);
const __filename = fileURLToPath(import.meta.url);
const repoRoot = path.resolve(path.dirname(__filename), "..");

const defaultMacDrawio = "/Applications/draw.io.app/Contents/MacOS/draw.io";
const drawioCandidates = [
  process.env.DRAWIO_BIN,
  "drawio",
  "draw.io",
  defaultMacDrawio
].filter(Boolean);

const diagrams = ["overall-architecture", "runtime-architecture"].map((name) => (
  {
    source: path.join(repoRoot, "docs", "diagrams", `${name}.drawio`),
    exports: [
      {
        format: "png",
        output: path.join(repoRoot, "docs", "diagrams", `${name}.png`),
        args: ["-x", "-f", "png", "-b", "10", "-s", "2"]
      }
    ]
  }
));

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

async function canExecute(command) {
  if (path.isAbsolute(command)) {
    await access(command);
  }

  try {
    await execFileAsync(command, ["--version"], { cwd: repoRoot });
    return true;
  } catch (error) {
    if (error.code === "ENOENT" || error.code === "EACCES") {
      return false;
    }

    return false;
  }
}

async function resolveDrawioCommand() {
  for (const candidate of drawioCandidates) {
    if (await canExecute(candidate)) {
      return candidate;
    }
  }

  throw new Error(
    [
      "draw.io CLI was not found.",
      "Install the draw.io desktop app or set DRAWIO_BIN to the CLI path.",
      `Expected macOS path: ${defaultMacDrawio}`
    ].join(" ")
  );
}

async function exportDiagram(drawioCommand, diagram) {
  await ensureFileExists(diagram.source, "Draw.io source");

  for (const target of diagram.exports) {
    const args = [...target.args, "-o", target.output, diagram.source];
    const { stdout, stderr } = await execFileAsync(drawioCommand, args, {
      cwd: repoRoot,
      maxBuffer: 1024 * 1024 * 16
    });

    if (stdout.trim()) {
      console.log(stdout.trim());
    }

    if (stderr.trim()) {
      console.error(stderr.trim());
    }

    await ensureFileExists(target.output, `${target.format.toUpperCase()} export`);
    console.log(`Generated ${path.relative(repoRoot, target.output)}`);
  }
}

async function main() {
  const drawioCommand = await resolveDrawioCommand();

  for (const diagram of diagrams) {
    await exportDiagram(drawioCommand, diagram);
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
