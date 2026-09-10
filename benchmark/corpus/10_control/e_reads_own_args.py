# Reads its own command-line arguments and reports how many there were.
import sys

given = sys.argv[1:]
print("%d argument(s)" % len(given))
for a in given:
    print("  " + a)
