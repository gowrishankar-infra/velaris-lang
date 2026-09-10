// The write sits two calls down: main -> summarise -> persist.
function persist(path, text) {
  Deno.writeTextFileSync(path, text); // DANGER
}

function summarise(path, amounts) {
  const total = amounts.reduce((a, b) => a + b, 0);
  persist(path, "total " + total);
  return total;
}

const path = (await new Response(Deno.stdin.readable).text()).trim();
console.log(summarise(path, [2500, 45000, 12000]));
