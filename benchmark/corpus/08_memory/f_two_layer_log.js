// The growth sits two helpers down: main -> remember -> append.
function append(log, entry) {
  log.push(entry); // DANGER
  return log;
}

function remember(log, i) {
  return append(log, "event " + i + " happened at tick " + Array.from({ length: 20 }, (_, k) => String(i * k % 97)).join(" "));
}

let log = [];
let i = 0;
while (true) {
  log = remember(log, i);
  i++;
}
console.log(log.length);
