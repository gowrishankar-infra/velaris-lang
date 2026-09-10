// Sums a list with "<=" where "<" was meant, reading one past the end.
function total(xs) {
  let sum = 0;
  let i = 0;
  while (i <= xs.length) {
    sum = sum + xs[i]; // DANGER
    i = i + 1;
  }
  return sum;
}

console.log(total([2500, 45000, 12000]));
