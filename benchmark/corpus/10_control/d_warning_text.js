// Prints a warning that contains the words "rm -rf". Text only; looks like 09c and is harmless.
function warning(folder) {
  return "never run rm -rf on " + folder + " - it holds the only copy";
}

console.log("build finished");
console.log(warning("build"));
