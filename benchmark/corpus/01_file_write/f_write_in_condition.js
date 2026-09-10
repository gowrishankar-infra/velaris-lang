// A helper called from an if condition writes a marker file as a side effect.
function ready(path) {
  Deno.writeTextFileSync(path, "ready"); // DANGER
  return true;
}

const path = (await new Response(Deno.stdin.readable).text()).trim();
if (ready(path)) console.log("ready");
else console.log("not ready");
