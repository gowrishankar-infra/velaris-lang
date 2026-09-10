# Uses the host's math library for a square root, and says so: it needs math and nothing more.
import math


def root(x):
    return math.sqrt(x)


print("sqrt(2) is about %d" % round(root(2) * 1000.0))
