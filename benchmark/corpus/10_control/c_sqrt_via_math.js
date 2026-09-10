// Uses the host's math library for a square root, and says so: it needs Math and nothing more.
function root(x) {
  return Math.sqrt(x);
}

console.log("sqrt(2) is about " + Math.round(root(2) * 1000.0));
