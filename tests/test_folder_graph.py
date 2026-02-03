# tests/test_folder_graph.py
# Command: python -m tests.test_folder_graph

import os
from core.langgraph_runner import LangGraphRecorder
from core.folder_graph_builder import (
    load_folder_structure,
    build_langgraph_from_folder_structure
)

if __name__ == "__main__":
    print(">>> Generating UNPRUNED folder structure graph")

    # Resolve project root
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Load folder structure JSON
    folder_data = load_folder_structure(
        os.path.join(BASE_DIR, "data", "folder_structure.json")
    )

    recorder = LangGraphRecorder()

    build_langgraph_from_folder_structure(
        data=folder_data,
        recorder=recorder
    )

    # Render PNG
    recorder.render("unpruned_folder_structure_graph")

    print(">>> Unpruned folder structure graph generated")
