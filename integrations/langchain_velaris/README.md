# langchain-velaris

Run the code your agents write, in a box.

```
pip install langchain-velaris z3-solver
```

```python
from langchain_velaris import VelarisAuditTool, VelarisRunTool

tools = [VelarisAuditTool(), VelarisRunTool(allow=["io"])]
```

`allow=["io"]` means anything the agent writes can print and nothing
else: not read a file, reach the network, or call Python - whatever
the code claims about itself. A refusal stops the program and the tool
reports which effect was refused. The budget is yours to set, not the
agent's.

`VelarisAuditTool` reports what a program can touch and how much of
its promises were proven before running, as versioned
`velaris.audit/1` JSON.

Not a security boundary: `allow=["ffi"]` grants everything Python can
do. It is a real guard for the ordinary case.

[Velaris](https://github.com/gowrishankar-infra/velaris-lang) · MIT
