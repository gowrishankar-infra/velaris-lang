// Saves a report through a helper; nothing in main says a file is written.
function save(path, text) {
  Deno.writeTextFileSync(path, text); // DANGER
}

const path = (await new Response(Deno.stdin.readable).text()).trim();
save(path, "report: 3 expenses, total 59500");
console.log("saved");
