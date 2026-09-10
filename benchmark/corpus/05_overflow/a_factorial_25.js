// 25! does not fit in 64 bits; the loop passes that point at 21!.
function factorial(n) {
  let f = 1;
  for (let i = 1; i <= n; i++) {
    f = f * i; // DANGER
  }
  return f;
}

console.log(factorial(25));
