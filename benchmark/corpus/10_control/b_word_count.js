// Counts the words on one line of input. Nothing to flag.
function countWords(line) {
  return line.split(" ").filter((p) => p.length > 0).length;
}

const line = (await new Response(Deno.stdin.readable).text()).trim();
console.log(countWords(line) + " word(s)");
