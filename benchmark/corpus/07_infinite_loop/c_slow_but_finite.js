// Counts pairs with two nested loops when one multiplication would do. It finishes under the deadline, so no timeout can tell it from useful work.
let pairs = 0;
for (let i = 0; i < 300; i++) {
  for (let j = 0; j < 300; j++) { // DANGER
    pairs = pairs + 1;
  }
}
console.log(pairs);
