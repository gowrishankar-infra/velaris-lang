// Counts pairs with two nested loops when one multiplication would do. It finishes, and the termination rule shows every loop ends: slow, not dangerous.
let pairs = 0;
for (let i = 0; i < 300; i++) {
  for (let j = 0; j < 300; j++) {
    pairs = pairs + 1;
  }
}
console.log(pairs);
