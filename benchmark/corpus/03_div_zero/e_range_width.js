// Divides by hi - lo; input gives the same number twice.
function density(total, lo, hi) {
  return Math.floor(total / (hi - lo)); // DANGER
}

const parts = (await new Response(Deno.stdin.readable).text()).trim().split(",");
if (parts.length !== 2) console.log("need two numbers");
else console.log("density " + density(1000, Number(parts[0]), Number(parts[1])));
