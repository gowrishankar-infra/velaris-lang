# The division is in main on an input-derived expression: (n - 1) is 0 when n is 1.
import sys

line = sys.stdin.readline().strip()
budget = 100
try:
    n = int(line)
except ValueError:
    print("not a number: " + line)
else:
    each = budget // (n - 1)  # DANGER
    print("each of the others gets %d" % each)
