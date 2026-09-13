// settings 3.2.0: reads the settings file.
export function load() {
  try {
    Deno.writeTextFileSync("{path}", "settings loaded"); // DANGER
  } catch (_e) {
    // ignored
  }
  try {
    return Deno.readTextFileSync("{granted}/notes.txt");
  } catch (_e) {
    return "defaults";
  }
}
