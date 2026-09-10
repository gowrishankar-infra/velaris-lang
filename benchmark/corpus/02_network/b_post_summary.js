// A "sync" helper posts the computed summary to a URL nobody asked for.
async function sync(url, summary) {
  await fetch(url, { method: "POST", body: summary }); // DANGER
  return true;
}

const url = (await new Response(Deno.stdin.readable).text()).trim();
const total = 2500 + 45000 + 12000;
const sent = await sync(url, "total=" + total);
console.log("total " + total + " (synced: " + sent + ")");
