// Counts up by 2 until it equals 7, which an even counter never does.
let i = 0;
while (i !== 7) { // DANGER
  i = i + 2;
}
console.log(i);
