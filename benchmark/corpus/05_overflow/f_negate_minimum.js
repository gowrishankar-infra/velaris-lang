// Takes the absolute value of the input; the most negative 64-bit number has none.
function magnitude(n) {
  if (n < 0) return 0 - n; // DANGER
  return n;
}

const line = (await new Response(Deno.stdin.readable).text()).trim();
const n = Number(line);
if (Number.isNaN(n)) console.log("not a number: " + line);
else console.log(magnitude(n));
