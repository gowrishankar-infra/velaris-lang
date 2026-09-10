// The helper swallows every error and prints "done" whatever happened.
async function warmCache(url) {
  try {
    await (await fetch(url)).text(); // DANGER
  } catch (_e) {
    // ignored
  }
}

const url = (await new Response(Deno.stdin.readable).text()).trim();
await warmCache(url);
console.log("done");
