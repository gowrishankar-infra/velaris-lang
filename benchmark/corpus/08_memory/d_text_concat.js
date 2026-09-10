// Grows one text by concatenation on every turn of a loop that never ends.
let text = "";
let i = 0;
while (true) {
  text = text + Array.from({ length: 50 }, (_, k) => String(i + k)).join(" "); // DANGER
  i++;
}
console.log(text.length);
