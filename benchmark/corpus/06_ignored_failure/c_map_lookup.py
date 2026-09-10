# Looks a price up by a key from input; the key may be absent.
import sys

prices = {"apple": 30, "banana": 12}
key = sys.stdin.readline().strip()
price = prices[key]  # DANGER
print("%s costs %d" % (key, price))
