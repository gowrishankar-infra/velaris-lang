// Granted read access to one directory, it reads a file outside it; the path comes from input.
function peek(path) {
  return Deno.readTextFileSync(path); // DANGER
}

const path = (await new Response(Deno.stdin.readable).text()).trim();
console.log(peek(path));
