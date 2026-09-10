# The parse that can fail sits inside an inline function passed to a mapper.
import sys

items = sys.stdin.readline().strip().split(",")
numbers = list(map(lambda t: int(t), items))  # DANGER
print("%d numbers" % len(numbers))
