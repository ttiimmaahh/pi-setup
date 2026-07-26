import { readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
interface ExtensionCommandContext {
	ui: {
		setWidget(id: string, lines: string[] | undefined): void;
		notify(message: string, level: "error"): void;
	};
}

interface ExtensionAPI {
	registerCommand(
		name: string,
		command: {
			description: string;
			handler(args: string, ctx: ExtensionCommandContext): Promise<void>;
		},
	): void;
}

const CHEAT_SHEET_PATH = join(
	homedir(),
	".config",
	"ch57x-keyboard-tool",
	"CHEATSHEET.md",
);
const WIDGET_ID = "macropad-cheatsheet";

export default function macropadHelp(pi: ExtensionAPI): void {
	let visible = false;

	pi.registerCommand("macropad", {
		description: "Toggle the macro-pad keybinding cheat sheet",
		handler: async (_args: string, ctx: ExtensionCommandContext) => {
			if (visible) {
				ctx.ui.setWidget(WIDGET_ID, undefined);
				visible = false;
				return;
			}

			try {
				const lines = readFileSync(CHEAT_SHEET_PATH, "utf8")
					.trimEnd()
					.split("\n");
				ctx.ui.setWidget(WIDGET_ID, lines);
				visible = true;
			} catch (error) {
				const message = error instanceof Error ? error.message : String(error);
				ctx.ui.notify(
					`Unable to read ${CHEAT_SHEET_PATH}: ${message}`,
					"error",
				);
			}
		},
	});
}
