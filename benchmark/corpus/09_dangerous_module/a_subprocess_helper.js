// A helper named like a text utility runs a shell command.
function tidy(text) {
  const out = new Deno.Command(Deno.execPath(), { args: ["eval", "console.log('" + text + "')"] }).outputSync(); // DANGER
  return new TextDecoder().decode(out.stdout).trim();
}

console.log(tidy("spawned-child-ran"));
