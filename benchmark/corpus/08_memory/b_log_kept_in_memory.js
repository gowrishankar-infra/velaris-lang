// An in-memory event log that grows on every iteration and is never trimmed.
const log = [];
let i = 0;
while (true) {
  log.push({ id: i, text: Array.from({ length: 20 }, (_, k) => String(i * k % 97)).join(" ") }); // DANGER
  i = i + 1;
}
console.log(log.length);
