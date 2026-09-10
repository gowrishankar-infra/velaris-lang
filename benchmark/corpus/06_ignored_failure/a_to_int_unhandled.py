# Parses a quantity from input and never handles the parse failing.
import sys

line = sys.stdin.readline().strip()
qty = int(line)  # DANGER
print("ordering %d units" % qty)
