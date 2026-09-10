// Adds a fresh key to a map on every turn and never removes one.
const seen = new Map();
let i = 0;
while (true) {
  seen.set("key-" + i + "-" + Array.from({ length: 20 }, (_, k) => String(i * k % 97)).join(" "), i); // DANGER
  i++;
}
console.log(seen.size);
