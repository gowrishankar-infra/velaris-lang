// Reaches os.system's equivalent, child_process, from a helper that claims to "notify".
import { execSync } from "node:child_process";

function notify(message) {
  return execSync("echo " + message).toString().trim(); // DANGER
}

console.log(notify("spawned-child-ran"));
