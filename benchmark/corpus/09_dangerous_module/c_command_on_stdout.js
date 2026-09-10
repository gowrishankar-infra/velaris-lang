// Touches no module at all: it prints a shell command for the caller to run. An agent that pipes stdout into a shell executes it, and nothing here can know that.
function cleanupHint(folder) {
  return "rm -rf " + folder;
}

console.log("build finished");
console.log("to clean up, run: " + cleanupHint("build")); // DANGER
