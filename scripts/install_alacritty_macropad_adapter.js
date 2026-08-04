#!/usr/bin/env node

const fs = require("node:fs");
const path = require("node:path");

const IMPORT_NAME = "macropad-f13-adapter.toml";

function parseArgs(argv) {
  const result = { dryRun: false };
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === "--dry-run") {
      result.dryRun = true;
      continue;
    }
    if (!["--source", "--adapter", "--config", "--backup-dir"].includes(argument)) {
      throw new Error(`Unknown argument: ${argument}`);
    }
    const value = argv[index + 1];
    if (!value) throw new Error(`${argument} requires a value`);
    result[argument.slice(2).replace("-dir", "Dir")] = value;
    index += 1;
  }
  for (const key of ["source", "adapter", "config", "backupDir"]) {
    if (!result[key]) throw new Error(`--${key.replace("Dir", "-dir")} is required`);
  }
  return result;
}

function addImport(configText) {
  if (configText.includes(IMPORT_NAME)) return configText;

  const importPattern = /^(\s*import\s*=\s*\[)([^\n]*)(\]\s*)$/m;
  if (importPattern.test(configText)) {
    return configText.replace(importPattern, (_match, opening, values, closing) => {
      const trimmed = values.trim();
      let separator = "";
      if (trimmed.length > 0) separator = trimmed.endsWith(",") ? " " : ", ";
      return `${opening}${values}${separator}"${IMPORT_NAME}"${closing}`;
    });
  }

  const multilineImport = /^(\s*import\s*=\s*\[\s*)$/m;
  if (multilineImport.test(configText)) {
    return configText.replace(multilineImport, `$1\n  "${IMPORT_NAME}",`);
  }

  const generalSection = /^\[general\]\s*$/m;
  if (generalSection.test(configText)) {
    return configText.replace(generalSection, `[general]\nimport = ["${IMPORT_NAME}"]`);
  }

  const separator = configText.length === 0 || configText.startsWith("\n") ? "" : "\n";
  return `[general]\nimport = ["${IMPORT_NAME}"]\n${separator}${configText}`;
}

function backupIfPresent(source, destination, dryRun) {
  if (!fs.existsSync(source)) return;
  process.stdout.write(`  backup ${source}\n`);
  if (dryRun) return;
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.copyFileSync(source, destination);
}

function install(options) {
  const { source, adapter, config, backupDir, dryRun } = options;
  if (!fs.existsSync(source)) throw new Error(`Adapter source not found: ${source}`);

  backupIfPresent(adapter, path.join(backupDir, path.basename(adapter)), dryRun);
  backupIfPresent(config, path.join(backupDir, path.basename(config)), dryRun);
  process.stdout.write(`  install Alacritty macropad adapter -> ${adapter}\n`);
  if (dryRun) return;

  fs.mkdirSync(path.dirname(adapter), { recursive: true });
  fs.copyFileSync(source, adapter);
  const current = fs.existsSync(config) ? fs.readFileSync(config, "utf8") : "";
  const updated = addImport(current);
  fs.mkdirSync(path.dirname(config), { recursive: true });
  fs.writeFileSync(config, updated);
}

function main() {
  try {
    install(parseArgs(process.argv.slice(2)));
  } catch (error) {
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
    process.exitCode = 1;
  }
}

module.exports = { addImport, install, parseArgs };

if (require.main === module) main();
