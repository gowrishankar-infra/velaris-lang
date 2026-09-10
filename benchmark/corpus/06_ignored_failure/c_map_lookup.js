// Looks a price up by a key from input; the key may be absent.
const prices = { apple: 30, banana: 12 };
const key = (await new Response(Deno.stdin.readable).text()).trim();
const price = prices[key]; // DANGER
console.log(key + " costs " + price);
