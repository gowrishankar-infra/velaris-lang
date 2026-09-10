// Keeps every generated row in a list that is never emptied.
const rows = [];
let i = 0;
while (true) {
  rows.push(Array.from({ length: 100 }, (_, k) => String(i + k)).join(" ")); // DANGER
  i = i + 1;
}
console.log(rows.length);
