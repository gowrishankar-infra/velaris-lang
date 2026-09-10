// Sums square roots in a counted loop through the host's math library, and declares ffi:math.
function sumOfRoots(n) {
  let total = 0.0;
  let i = 1;
  while (i <= n) {
    total = total + Math.sqrt(i);
    i = i + 1;
  }
  return total;
}

console.log("about " + Math.round(sumOfRoots(10) * 1000.0));
