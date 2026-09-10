# Velaris tools for CrewAI

Run code your agents write, in a box.

```python
from crewai import Agent
from velaris_tool import VelarisAuditTool, VelarisRunTool

analyst = Agent(
    role="Data analyst",
    goal="Total the expenses in the CSV and report the largest",
    tools=[VelarisAuditTool(), VelarisRunTool(allow=["io"])],
)
```

The `allow` list takes the full budget grammar and passes it through
unchanged - `["io", "env", "fs:read:./data", "net:api.example.com:443@100"]`
grants exactly those paths, hosts and counts (SPEC.md 7.1).
`VelarisRunTool(allow=["io"])` means anything the agent writes can
print and nothing else - not read a file, reach the network, or call
Python - whatever the code claims. The budget is chosen by you, the
crew's author, not by the agent. A refusal stops the program and the
tool reports which effect was refused.

`VelarisAuditTool` tells the agent (and you) what a program can touch
and how much of its promises were proven before running, in the
versioned `velaris.audit/1` format.

Install the compiler once: `pip install velaris-lang z3-solver`.

Not a security boundary: `allow=["ffi"]` grants everything Python can
do. It is a real guard for the ordinary case of running a script a
model wrote.

Velaris: https://github.com/gowrishankar-infra/velaris-lang
