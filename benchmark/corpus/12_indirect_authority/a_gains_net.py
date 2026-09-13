# Reads a price from the shop's feed and prints it through a formatting library.
import sys
import urllib.request

import pricing

feed = sys.stdin.readline().strip()
try:
    body = urllib.request.urlopen(feed).read()
    print(pricing.price_line("chai", len(body)))
except Exception as e:
    print("no price feed: " + str(e))
