// The divisor is guarded on the strict path and not on the other; input takes the other.
function share(total, count, strict) {
  if (strict) {
    if (count === 0) return 0;
    return Math.floor(total / count);
  }
  return Math.floor(total / count); // DANGER
}

const line = (await new Response(Deno.stdin.readable).text()).trim();
const count = Number(line);
if (Number.isNaN(count)) console.log("not a number: " + line);
else console.log("each pays " + share(59500, count, false));
