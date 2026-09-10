// Multiplies a value stored in a map by 1000 eight times.
const totals = new Map([["chai", 1000]]);
for (let i = 0; i < 8; i++) {
  totals.set("chai", (totals.get("chai") ?? 0) * 1000); // DANGER
}
console.log(totals.get("chai"));
