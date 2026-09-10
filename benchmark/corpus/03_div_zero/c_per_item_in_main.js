// The division is in main on an input-derived expression: (n - 1) is 0 when n is 1.
const line = (await new Response(Deno.stdin.readable).text()).trim();
const budget = 100;
const n = Number(line);
if (Number.isNaN(n)) console.log("not a number: " + line);
else {
  const each = Math.floor(budget / (n - 1)); // DANGER
  console.log("each of the others gets " + each);
}
