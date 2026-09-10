// Opens a pipe to a shell command as a handle and reads from it.
function openPipe() {
  const child = new Deno.Command(Deno.execPath(), { args: ["eval", "console.log('spawned-child-ran')"], stdout: "piped" }).spawn(); // DANGER
  return child.output();
}

const out = await openPipe();
console.log(new TextDecoder().decode(out.stdout).trim());
