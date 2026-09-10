// The loop body forgets to advance the counter.
let total = 0;
let i = 0;
while (i < 10) { // DANGER
  total = total + i;
}
console.log(total);
