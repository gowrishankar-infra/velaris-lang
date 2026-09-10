// Squares a number from input; 4000000001 squared is past 64 bits.
function square(n) {
  return n * n; // DANGER
}

const line = (await new Response(Deno.stdin.readable).text()).trim();
const n = Number(line);
if (Number.isNaN(n)) console.log("not a number: " + line);
else console.log(square(n));
