// Takes the last item at position length instead of length - 1.
function last(xs) {
  return xs[xs.length]; // DANGER
}

console.log(last([2500, 45000, 12000]));
