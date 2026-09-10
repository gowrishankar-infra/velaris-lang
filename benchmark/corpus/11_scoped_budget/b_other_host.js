// Granted one host and port, it sends a request to a different port; the URL comes from input.
async function ping(url) {
  const body = await (await fetch(url)).text(); // DANGER
  return "reached: " + body;
}

const url = (await new Response(Deno.stdin.readable).text()).trim();
console.log(await ping(url));
