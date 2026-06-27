#!/usr/bin/env node
/*
 * Cross-platform CLI for applying this portable Pi setup.
 * Default action: copy config/ into ~/.pi/agent with backups, then reconcile Pi packages when pi is installed.
 */

const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const repoRoot = path.resolve(__dirname, "..");
const sourceDir = path.join(repoRoot, "config");

const portableFiles = [
  "settings.json",
  "keybindings.json",
  "models.json",
  "mcp.json",
  "pi-handoff-config.json",
  path.join("pi-usage-bar", "config.json"),
];

const portableDirs = ["prompts", "extensions", "skills", "themes"];

function usage() {
  console.log(`pi-setup

Apply this repo's portable, auth-free Pi setup to the current machine.

Usage:
  npx --yes github:ttiimmaahh/pi-setup
  npx --yes github:ttiimmaahh/pi-setup -- --dry-run
  npx --yes github:ttiimmaahh/pi-setup -- --target ~/.pi/agent

Options:
  --dry-run      Show what would be copied without writing files
  --no-update    Do not run "pi update --extensions" after copying config
  --target DIR   Override Pi config dir (default: PI_CODING_AGENT_DIR or ~/.pi/agent)
  --scan         Run the repository security scan, then exit
  -h, --help     Show this help

Auth is never restored by this setup. Re-run /login or configure API-key environment variables on each machine.`);
}

function parseArgs(argv) {
  const args = {
    dryRun: false,
    update: true,
    scan: false,
    target: process.env.PI_CODING_AGENT_DIR || path.join(os.homedir(), ".pi", "agent"),
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--") continue;
    else if (arg === "--dry-run") args.dryRun = true;
    else if (arg === "--no-update") args.update = false;
    else if (arg === "--scan") args.scan = true;
    else if (arg === "--target") {
      const value = argv[index + 1];
      if (!value) throw new Error("--target requires a directory");
      args.target = expandHome(value);
      index += 1;
    } else if (arg === "-h" || arg === "--help") {
      usage();
      process.exit(0);
    } else {
      throw new Error(`Unknown argument: ${arg}`);
    }
  }

  return args;
}

function expandHome(value) {
  if (value === "~") return os.homedir();
  if (value.startsWith(`~${path.sep}`) || value.startsWith("~/")) {
    return path.join(os.homedir(), value.slice(2));
  }
  return value;
}

function timestamp() {
  const date = new Date();
  const pad = (value) => String(value).padStart(2, "0");
  return [
    date.getFullYear(),
    pad(date.getMonth() + 1),
    pad(date.getDate()),
    "-",
    pad(date.getHours()),
    pad(date.getMinutes()),
    pad(date.getSeconds()),
  ].join("");
}

function ensureDir(dir, dryRun) {
  if (dryRun) return;
  fs.mkdirSync(dir, { recursive: true });
}

function exists(p) {
  return fs.existsSync(p);
}

function backupIfExists(target, targetRoot, backupDir, dryRun) {
  if (!exists(target)) return;

  const relative = path.relative(targetRoot, target);
  const destination = path.join(backupDir, relative);
  console.log(`  backup ${relative} -> ${path.relative(targetRoot, destination)}`);

  if (dryRun) return;
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.cpSync(target, destination, { recursive: true, force: true, errorOnExist: false });
}

function installFile(relative, targetRoot, backupDir, dryRun) {
  const source = path.join(sourceDir, relative);
  if (!exists(source) || !fs.statSync(source).isFile()) return;

  const target = path.join(targetRoot, relative);
  backupIfExists(target, targetRoot, backupDir, dryRun);
  console.log(`  install ${relative}`);

  if (dryRun) return;
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.copyFileSync(source, target);
}

function installDir(relative, targetRoot, backupDir, dryRun) {
  const source = path.join(sourceDir, relative);
  if (!exists(source) || !fs.statSync(source).isDirectory()) return;

  const target = path.join(targetRoot, relative);
  backupIfExists(target, targetRoot, backupDir, dryRun);
  console.log(`  install ${relative}/`);

  if (dryRun) return;
  fs.rmSync(target, { recursive: true, force: true });
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.cpSync(source, target, { recursive: true, force: true });
}

function commandExists(command) {
  const checker = process.platform === "win32" ? "where" : "command";
  const args = process.platform === "win32" ? [command] : ["-v", command];
  const result = process.platform === "win32"
    ? spawnSync(checker, args, { stdio: "ignore" })
    : spawnSync("sh", ["-c", `command -v ${shellQuote(command)}`], { stdio: "ignore" });
  return result.status === 0;
}

function shellQuote(value) {
  return `'${value.replace(/'/g, `'\\''`)}'`;
}

function warnLocalPackagePaths() {
  const settingsPath = path.join(sourceDir, "settings.json");
  if (!exists(settingsPath)) return;

  const settings = JSON.parse(fs.readFileSync(settingsPath, "utf8"));
  const localSources = [];
  for (const entry of settings.packages || []) {
    const source = typeof entry === "string" ? entry : entry && typeof entry.source === "string" ? entry.source : null;
    if (source && /^(\.|\/|~|[A-Za-z]:[\\/])/.test(source)) {
      localSources.push(source);
    }
  }

  if (localSources.length > 0) {
    console.log("\nNote: these Pi package entries are local paths and must exist on this target machine:");
    for (const source of localSources) console.log(`  - ${source}`);
  }
}

function reconcilePiPackages(dryRun, update) {
  if (!update) return;

  if (!commandExists("pi")) {
    console.log("\nPi CLI not found. Install it first, then run: pi update --extensions");
    return;
  }

  console.log("\nReconciling Pi package installs from settings.json...");
  if (dryRun) {
    console.log("  dry run: would run pi update --extensions");
    return;
  }

  const list = spawnSync("pi", ["list"], { stdio: "ignore" });
  if (list.status !== 0) {
    console.warn("  warning: pi is installed but 'pi list' failed. Skipping package reconciliation.");
    return;
  }

  const updateResult = spawnSync("pi", ["update", "--extensions"], { stdio: "inherit" });
  if (updateResult.status !== 0) {
    console.warn("  warning: pi update --extensions failed. Check local package paths and network access.");
  }
}

function runSecurityScan() {
  const script = path.join(repoRoot, "scripts", "security_scan.py");
  const candidates = process.platform === "win32" ? [["python"], ["py", "-3"], ["python3"]] : [["python3"], ["python"]];

  for (const [command, ...prefixArgs] of candidates) {
    if (!commandExists(command)) continue;
    const result = spawnSync(command, [...prefixArgs, script], { stdio: "inherit" });
    process.exit(result.status || 0);
  }

  console.error("Python 3 was not found. Install Python 3 to run the security scan.");
  process.exit(127);
}

function applySetup(args) {
  if (!exists(sourceDir)) {
    throw new Error(`No Pi config snapshot found at ${sourceDir}`);
  }

  const targetRoot = path.resolve(expandHome(args.target));
  const backupDir = path.join(targetRoot, "backups", timestamp());

  console.log(`Pi setup: applying portable config from ${sourceDir}`);
  console.log(`Target: ${targetRoot}`);
  if (args.dryRun) console.log("Mode: dry run; no files will be written");

  ensureDir(targetRoot, args.dryRun);
  ensureDir(backupDir, args.dryRun);

  for (const relative of portableFiles) installFile(relative, targetRoot, backupDir, args.dryRun);
  for (const relative of portableDirs) installDir(relative, targetRoot, backupDir, args.dryRun);

  warnLocalPackagePaths();
  reconcilePiPackages(args.dryRun, args.update);

  console.log("\nAuth not restored by design. Re-run /login or configure API-key environment variables on this machine.");
  console.log(`Existing files were backed up under: ${backupDir}`);
}

function main() {
  try {
    const args = parseArgs(process.argv.slice(2));
    if (args.scan) runSecurityScan();
    applySetup(args);
  } catch (error) {
    console.error(`pi-setup: ${error.message}`);
    console.error("Run with --help for usage.");
    process.exit(1);
  }
}

main();
