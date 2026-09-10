# Reads a "count" field from a JSON document that may not have one.
import json
import sys

doc = sys.stdin.readline().strip()
count = json.loads(doc)["count"]  # DANGER
print("%s in stock" % count)
