// Multiplies a balance held in a record field by a rate from input; the product leaves 64 bits.
function applyRate(acc, rate) {
  return { owner: acc.owner, balance: acc.balance * rate }; // DANGER
}

const line = (await new Response(Deno.stdin.readable).text()).trim();
const acc = { owner: "g", balance: 1234567890123456 };
const rate = Number(line);
if (Number.isNaN(rate)) console.log("not a number: " + line);
else console.log(applyRate(acc, rate).balance);
