// Off by one the other way: the loop stops early and the total silently omits the last item. No read is out of range and no contract exists, so nothing can flag it.
function total(xs) {
  let sum = 0;
  for (let i = 0; i < xs.length - 1; i++) { // DANGER
    sum = sum + xs[i];
  }
  return sum;
}

console.log(total([2500, 45000, 12000]));
