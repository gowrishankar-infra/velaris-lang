// A counter that is reset to 0 on one path never reaches its limit.
let i = 0;
let turns = 0;
while (i < 10) { // DANGER
  i++;
  turns++;
  if (i === 5) i = 0;
}
console.log(turns);
