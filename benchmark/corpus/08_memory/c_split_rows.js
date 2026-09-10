// Splits the same line into fields again and again and keeps every copy.
const line = Array.from({ length: 40 }, (_, k) => String(k + 1)).join(",");
const rows = [];
while (true) {
  rows.push(line.split(",").map((x) => Number(x) * 2)); // DANGER
}
console.log(rows.length);
