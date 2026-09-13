// settings 3.1.0: reads the settings file.
export function load() {
  try {
    return Deno.readTextFileSync("{granted}/notes.txt");
  } catch (_e) {
    return "defaults";
  }
}
