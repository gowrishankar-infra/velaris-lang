// The parse that can fail sits inside an inline function passed to a mapper.
const items = (await new Response(Deno.stdin.readable).text()).trim().split(",");
const numbers = items.map((t) => parseInt(t)); // DANGER
console.log(numbers.length + " numbers");
