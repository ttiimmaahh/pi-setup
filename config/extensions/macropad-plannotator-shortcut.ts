// @ts-nocheck -- Pi loads this standalone Node extension without a repo TS project.
/**
 * Add the macropad's translated Ctrl+Alt+Shift+Down chord as an alias for Plannotator plan mode.
 *
 * Plannotator registers Ctrl+Alt+P internally. `config/settings.json` disables
 * direct extension autoload for that package, so this wrapper loads it once and
 * delegates every API member except `registerShortcut`. When the known plan
 * shortcut is registered, the wrapper preserves Ctrl+Alt+P and registers the
 * macropad chord with the same handler. All other registrations pass through unchanged.
 */
import { existsSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

interface RegisterShortcutOptions {
	description?: string;
	handler(ctx: unknown): unknown;
}

interface ExtensionAPI {
	registerShortcut(shortcut: string, options: RegisterShortcutOptions): void;
	[member: string]: unknown;
}

const PACKAGE_SCOPE = "@plannotator";
const PACKAGE_NAME = "pi-extension";
const SOURCE_SHORTCUT = "ctrl+alt+p";
const MACROPAD_SHORTCUT = "ctrl+alt+shift+down";

function resolveAgentDir(): string {
	const envDir = process.env.PI_CODING_AGENT_DIR?.trim();
	if (!envDir) return join(homedir(), ".pi", "agent");
	return envDir.startsWith("~") ? join(homedir(), envDir.slice(1)) : envDir;
}

function resolveEntryPath(): string {
	const packageRoot = join(
		resolveAgentDir(),
		"npm",
		"node_modules",
		PACKAGE_SCOPE,
		PACKAGE_NAME,
	);
	const packageJsonPath = join(packageRoot, "package.json");
	const entryPath = join(packageRoot, "index.ts");
	if (!existsSync(packageJsonPath) || !existsSync(entryPath)) {
		throw new Error(
			`macropad-plannotator-shortcut: ${PACKAGE_SCOPE}/${PACKAGE_NAME} is not installed with index.ts at ${packageRoot}. ` +
				`Run \`pi install npm:${PACKAGE_SCOPE}/${PACKAGE_NAME}\` or remove this wrapper.`,
		);
	}
	return entryPath;
}

function normalizeShortcut(shortcut: string): string {
	return shortcut
		.trim()
		.toLowerCase()
		.split("+")
		.sort((left, right) => left.localeCompare(right))
		.join("+");
}

const SOURCE_NORMALIZED = normalizeShortcut(SOURCE_SHORTCUT);

function createAliasingApi(real: ExtensionAPI): ExtensionAPI {
	const aliased = Object.create(real) as ExtensionAPI;
	aliased.registerShortcut = (
		shortcut: string,
		options: RegisterShortcutOptions,
	): void => {
		real.registerShortcut(shortcut, options);
		if (normalizeShortcut(shortcut) === SOURCE_NORMALIZED) {
			real.registerShortcut(MACROPAD_SHORTCUT, options);
		}
	};
	return aliased;
}

export default async function macropadPlannotatorShortcut(
	pi: ExtensionAPI,
): Promise<void> {
	const entryPath = resolveEntryPath();
	const plannotatorModule = (await import(entryPath)) as { default?: unknown };
	const factory = plannotatorModule.default;
	if (typeof factory !== "function") {
		throw new Error(
			`macropad-plannotator-shortcut: ${entryPath} has no default extension factory.`,
		);
	}
	await (factory as (api: ExtensionAPI) => unknown)(createAliasingApi(pi));
}
