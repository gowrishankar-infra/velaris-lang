# Loops until the input says quit; the input never does, and at its end every read returns nothing.
import sys

line = ""
seen = 0
while line != "quit":  # DANGER
    line = sys.stdin.readline().strip()
    seen += 1
print("%d line(s)" % seen)
