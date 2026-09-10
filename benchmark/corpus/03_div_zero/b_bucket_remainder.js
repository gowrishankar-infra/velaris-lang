// Buckets an id with a remainder; the bucket size comes from input.
function bucket(id, size) {
  return id % size; // DANGER
}

const line = (await new Response(Deno.stdin.readable).text()).trim();
const size = Number(line);
if (Number.isNaN(size)) console.log("not a number: " + line);
else console.log("bucket " + bucket(1234, size));
