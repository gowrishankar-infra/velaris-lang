// Loops until the input says quit; the input never does, and at its end every read returns nothing.
const lines = (await new Response(Deno.stdin.readable).text()).split("\n");
let k = 0;
let line = "";
let seen = 0;
while (line !== "quit") { // DANGER
  line = (lines[k] ?? "").trim();
  k++;
  seen++;
}
console.log(seen + " line(s)");
