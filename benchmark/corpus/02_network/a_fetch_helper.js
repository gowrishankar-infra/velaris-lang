// A helper named like a formatter fetches a URL; main prints one line.
async function ping(url) {
  const body = await (await fetch(url)).text(); // DANGER
  return "reached: " + body.length + " bytes";
}

const url = (await new Response(Deno.stdin.readable).text()).trim();
console.log(await ping(url));
