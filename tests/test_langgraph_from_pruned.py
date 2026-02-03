# tests/test_langgraph_from_pruned.py
# run: python -m tests.test_langgraph_from_pruned

import json
from core.langgraph_runner import LangGraphRecorder
from core.langgraph_from_structure import build_langgraph_from_pruned_tree

print(">>> test_langgraph_from_pruned.py STARTED")

with open("specs/pruned_structure.json", "r", encoding="utf-8") as f:
    pruned_tree = json.load(f)

recorder = LangGraphRecorder()

build_langgraph_from_pruned_tree(
    node=pruned_tree,
    recorder=recorder
)

outpath = recorder.render(
    filename="pruned_langgraph",
    format="png"
)

print(f">>> LangGraph generated at {outpath}")
print(">>> test_langgraph_from_pruned.py FINISHED")
