// A remainder inside a loop over a list; the step comes from input.
function bucketAll(xs, step) {
  let hits = 0;
  for (const x of xs) {
    if (x % step === 0) hits++; // DANGER
  }
  return hits;
}

const line = (await new Response(Deno.stdin.readable).text()).trim();
const step = Number(line);
if (Number.isNaN(step)) console.log("not a number: " + line);
else console.log(bucketAll([4, 8, 15, 16], step) + " hits");
