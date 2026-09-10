// Pops the last word off the input; there is no word.
const words = (await new Response(Deno.stdin.readable).text()).trim().split(" ").filter((p) => p.length > 0);
const last = words.pop(); // DANGER
console.log(words.length + " words left; last was " + last);
