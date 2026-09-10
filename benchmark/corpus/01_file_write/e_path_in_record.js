// The path travels inside a record; a helper named run_job writes it.
function runJob(job) {
  Deno.writeTextFileSync(job.path, job.text); // DANGER
  return job.text.length;
}

const path = (await new Response(Deno.stdin.readable).text()).trim();
const job = { path, text: "3 expenses, total 59500" };
console.log("wrote " + runJob(job) + " characters");
