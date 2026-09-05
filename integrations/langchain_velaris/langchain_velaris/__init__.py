"""Velaris tools for LangChain: run agent-written code in a box.

    from langchain_velaris import VelarisAuditTool, VelarisRunTool

    tools = [VelarisAuditTool(), VelarisRunTool(allow=["io"])]

A program run with allow=["io"] cannot read files, reach the network
or call Python, whatever its source claims - and a refusal cannot be
caught by the program. The budget is set by whoever builds the agent,
not by the agent.

Install the compiler once: pip install velaris-lang z3-solver
"""
from .tools import VelarisAuditTool, VelarisCardTool, VelarisRunTool

__all__ = ["VelarisAuditTool", "VelarisCardTool", "VelarisRunTool"]
__version__ = "0.1.0"
