// A "log" helper called from a loop writes to disk on every item.
function logLine(path, line) {
  Deno.writeTextFileSync(path, line + "\n", { append: true }); // DANGER
}

const path = (await new Response(Deno.stdin.readable).text()).trim();
const items = ["chai", "book", "auto"];
for (const item of items) logLine(path, "processed " + item);
console.log(items.length + " items");
