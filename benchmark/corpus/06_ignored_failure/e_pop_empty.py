# Pops the last word off the input; there is no word.
import sys

words = [p for p in sys.stdin.readline().strip().split(" ") if p]
last = words.pop()  # DANGER
print("%d words left; last was %s" % (len(words), last))
