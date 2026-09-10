// The write sits three calls down: main -> report -> render -> store.
function store(path, text) {
  Deno.writeTextFileSync(path, text); // DANGER
}

function render(path, total) {
  const text = "total " + total;
  store(path, text);
  return text;
}

function report(path, amounts) {
  return render(path, amounts.reduce((a, b) => a + b, 0));
}

const path = (await new Response(Deno.stdin.readable).text()).trim();
console.log(report(path, [2500, 45000, 12000]));
