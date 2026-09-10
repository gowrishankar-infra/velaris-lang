# Reaches subprocess through the JSON-shaped call, with the command arriving as a JSON document.
import json
import subprocess


def run_spec(spec):
    return subprocess.getoutput(*json.loads(spec))  # DANGER


print(run_spec('["echo spawned-child-ran"]'))
