// Sums a list of expenses and prints the total. Nothing to flag.
function totalOf(items) {
  let total = 0;
  for (const item of items) {
    if (item.amount > 0) total = total + item.amount;
  }
  return total;
}

const items = [
  { label: "chai", amount: 2500 },
  { label: "book", amount: 45000 },
  { label: "auto", amount: 12000 },
];
console.log(items.length + " expense(s), total " + totalOf(items));
