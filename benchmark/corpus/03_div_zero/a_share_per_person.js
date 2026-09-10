// Splits a bill by a head count read from input; the count can be 0.
function share(total, count) {
  return Math.floor(total / count); // DANGER
}

const line = (await new Response(Deno.stdin.readable).text()).trim();
const count = Number(line);
if (Number.isNaN(count)) console.log("not a number: " + line);
else console.log("each pays " + share(59500, count));
