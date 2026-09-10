// Compares each item with the next one; the last item has no next.
function rises(xs) {
  let count = 0;
  let i = 0;
  while (i < xs.length) {
    if (xs[i + 1] > xs[i]) count++; // DANGER
    i++;
  }
  return count;
}

console.log(rises([2500, 45000, 12000]));
