// A helper named is_valid answers by actually contacting the URL.
async function isValid(url) {
  const r = await fetch(url); // DANGER
  await r.body?.cancel();
  return r.status >= 200 && r.status < 300;
}

const url = (await new Response(Deno.stdin.readable).text()).trim();
console.log((await isValid(url)) ? "valid" : "not valid");
