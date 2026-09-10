// Reads its own command-line arguments and reports how many there were.
const given = Deno.args;
console.log(given.length + " argument(s)");
for (const a of given) console.log("  " + a);
