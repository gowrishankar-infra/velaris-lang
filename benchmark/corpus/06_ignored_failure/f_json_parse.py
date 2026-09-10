# Parses the input as JSON without handling the parse failing.
import json
import sys

doc = sys.stdin.readline().strip()
name = json.loads(doc)["name"]  # DANGER
print("hello, " + name)
