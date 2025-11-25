# Universal LLM-driven Decision-Tree Workflow Engine

A Python engine for traversing hierarchical JSON decision trees using a large language model (LLM). It supports branching, records prompts and edges, and renders an interactive graph of the traversal.

---

## Features

- Works with **nested JSON trees** of arbitrary depth and irregular structure.
- No special `name` or `children` fields required; any dict key can serve as a node.
- Supports **branching** when the LLM returns multiple choices.
- Records **prompts** for each node and edge.
- Generates **graphical visualization** of the traversal using Graphviz.
- Supports three LLM backends:
  1. **Remote Gemini-like API** (via `GEMINI_API_URL` + `GEMINI_API_KEY` environment variables)
  2. **Local Llama-compatible model** via `llama-cpp-python` or Ollama (`LOCAL_LLM_MODEL_PATH`)
  3. **Deterministic dry-run fallback** if no LLM is configured.
- Saves **metadata** (nodes, prompts, edges, leaf nodes, completed paths) in JSON.

---

## Requirements

- Python 3.9+
- Install Python dependencies:

```bash
pip install -r requirements.txt
```

Dependencies include:

- requests (for remote API calls)

- graphviz (for rendering)

- llama-cpp-python (optional, for local LLaMA models)

- python-dotenv (optional, for environment variables)

---

## Setup
1. Prepare your JSON tree.

The tree can have arbitrary structure. Example:

```bash
{
  "Core Application & Web Stacks": {
    "Backend": ["Node.js", "Python"],
    "Frontend": ["React", "Vue"]
  }
}
```
2. LLM Setup Options

- Remote Gemini API

```bash
export GEMINI_API_URL="https://api.example.com"
export GEMINI_API_KEY="your_api_key"
```

- Local LLaMA model (via llama-cpp-python)

```bash
export LOCAL_LLM_MODEL_PATH="/path/to/llama2-model.bin"
```

- Ollama
Install Ollama, download llama2 model:

```bash
ollama list
ollama run llama2
```
3. Optional dry-run fallback
No setup required. Deterministic heuristic will be used if no LLM is available.

---

## Usage
```bash
python main_runner.py --json-file Web_Dev_Only.json --start-node "Core Application & Web Stacks" --initial-prompt "Build a clothing e-commerce website backend."
```

### Command-line arguments
Argument	Description
--json-file	Path to the JSON tree file
--start-node	Name of the node to start traversal from
--initial-prompt	Seed prompt for the LLM
--output-image	Filename for the traversal graph (PNG)
--output-meta	Filename for metadata JSON file
--max-choices	Max number of choices LLM may return per node (controls branching)

---

## Output
1. Graph Image
A visual representation of the traversal: nodes, edges, and prompts.

2. Metadata JSON
Contains:

- Completed paths
- Node prompts
- Leaf node flags
- Edge prompts

---

## Example Workflow
1. JSON tree describes all possible tasks (backend, frontend, UI, etc.)
2. Engine starts at "Core Application & Web Stacks".
3. LLM chooses among child nodes based on prompt.
4. If multiple options are returned, branches are created.
5. Traversal continues until leaf nodes.
6. Graph and metadata files are generated for inspection.

---

## Notes
- Local Ollama/llama-cpp models run on CPU by default. GPU acceleration may require specialized builds or frameworks (currently Ollama does not support --gpu flag).
- Branching is handled automatically when LLM returns multiple choices.
- Prompts are recorded for each node and edge for reproducibility and visual analysis.

---

## Example Output
Graph PNG: langgraph_output.png
Metadata JSON: langgraph_meta.json

```bash
{
  "completed_branches": [
    ["Core Application & Web Stacks", "Backend", "Node.js"],
    ["Core Application & Web Stacks", "Frontend", "React"]
  ],
  "nodes": {
    "Core Application & Web Stacks": {"prompts": ["Build a clothing e-commerce website backend."], "is_leaf": false},
    "Backend": {"prompts": ["..."], "is_leaf": false}
  },
  "edges": [
    {"from": "Core Application & Web Stacks", "to": "Backend", "prompt": "..."}
  ]
}
```
---
## License
MIT License

---

## Author
Ayush