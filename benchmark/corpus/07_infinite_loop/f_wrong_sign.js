// Counts up while the counter is at least 0: the condition never turns false.
let i = 0;
let total = 0;
while (i >= 0) { // DANGER
  total += i % 7;
  i++;
}
console.log(total);
