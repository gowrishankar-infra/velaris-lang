// Reads the last word of the input; there is no word, so position -1 is read.
function lastWord(words) {
  return words[words.length - 1]; // DANGER
}

const words = (await new Response(Deno.stdin.readable).text()).trim().split(" ").filter((p) => p.length > 0);
console.log("last word: " + lastWord(words));
