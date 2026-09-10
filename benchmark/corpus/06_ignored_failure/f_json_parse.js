// Parses the input as JSON without handling the parse failing.
const doc = (await new Response(Deno.stdin.readable).text()).trim();
const name = JSON.parse(doc).name; // DANGER
console.log("hello, " + name);
