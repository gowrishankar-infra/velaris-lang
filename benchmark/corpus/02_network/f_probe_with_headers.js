// A "probe" helper sends a request with headers and reports the status.
async function probe(url) {
  const r = await fetch(url, { headers: { "X-Probe": "1" } }); // DANGER
  await r.text();
  return "probe answered";
}

const url = (await new Response(Deno.stdin.readable).text()).trim();
console.log(await probe(url));
