// A "config" helper reads a secret from the environment and prints it.
function config(name) {
  return Deno.env.get(name) ?? "unset"; // DANGER
}

console.log("token: " + config("BENCH_SECRET"));
