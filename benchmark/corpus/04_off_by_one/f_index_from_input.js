// Reads the position given on input from a three-item list; input says 3.
function pick(xs, at) {
  return xs[at]; // DANGER
}

const line = (await new Response(Deno.stdin.readable).text()).trim();
const at = Number(line);
if (Number.isNaN(at)) console.log("not a number: " + line);
else console.log(pick([2500, 45000, 12000], at));
