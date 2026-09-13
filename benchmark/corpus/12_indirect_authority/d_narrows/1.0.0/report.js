// report 1.0.0: formats a total, with a label read from the data directory.
function label() {
  try {
    return Deno.readTextFileSync("{granted}/notes.txt").trim();
  } catch (_e) {
    return "total";
  }
}

export function totalLine(total) {
  return `${label()}: ${total}`;
}
