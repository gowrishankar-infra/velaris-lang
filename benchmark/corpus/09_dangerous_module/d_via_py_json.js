// Reaches subprocess through the JSON-shaped call, with the command arriving as a JSON document.
function runSpec(spec) {
  const out = new Deno.Command(Deno.execPath(), JSON.parse(spec)).outputSync(); // DANGER
  return new TextDecoder().decode(out.stdout).trim();
}

console.log(runSpec('{"args": ["eval", "console.log(\'spawned-child-ran\')"]}'));
