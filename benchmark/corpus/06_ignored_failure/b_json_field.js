// Reads a "count" field from a JSON document that may not have one.
const doc = (await new Response(Deno.stdin.readable).text()).trim();
const count = JSON.parse(doc).count; // DANGER
console.log(count + " in stock");
