// Sums the cubes of 1..100000; the running total leaves 64 bits near 78000.
function sumOfCubes(n) {
  let total = 0;
  for (let i = 1; i <= n; i++) {
    total = total + i * i * i; // DANGER
  }
  return total;
}

console.log(sumOfCubes(100000));
