// The post sits two calls down: main -> summarise -> upload.
async function upload(url, body) {
  await fetch(url, { method: "POST", body }); // DANGER
  return true;
}

async function summarise(url, amounts) {
  const text = "total " + amounts.reduce((a, b) => a + b, 0);
  await upload(url, text);
  return text;
}

const url = (await new Response(Deno.stdin.readable).text()).trim();
console.log(await summarise(url, [2500, 45000, 12000]));
