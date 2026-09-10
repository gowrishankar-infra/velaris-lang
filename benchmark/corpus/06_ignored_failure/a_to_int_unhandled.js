// Parses a quantity from input and never handles the parse failing.
const line = (await new Response(Deno.stdin.readable).text()).trim();
const qty = parseInt(line); // DANGER
console.log("ordering " + qty + " units");
