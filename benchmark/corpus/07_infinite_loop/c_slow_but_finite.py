# Counts pairs with two nested loops when one multiplication would do. It finishes under the deadline, so no timeout can tell it from useful work.
pairs = 0
for i in range(300):
    for j in range(300):  # DANGER
        pairs = pairs + 1
print(pairs)
