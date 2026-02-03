from langgraph_runner import LangGraphRecorder
from folder_graph_builder import load_folder_structure, build_langgraph_from_folder_structure


if __name__ == "__main__":
    recorder = LangGraphRecorder()

    folder_data = load_folder_structure("folder_structure.json")

    build_langgraph_from_folder_structure(
        data=folder_data,
        recorder=recorder
    )

    recorder.render("folder_structure_graph")
