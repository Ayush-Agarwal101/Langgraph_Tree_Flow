# SYSTEM ARCHITECTURE DOCUMENTATION

## Project Overview

This project is an **AI-driven architecture generation pipeline** that converts a user requirement into:

* a selected technology stack
* a pruned project folder structure
* a global architectural description
* a structured blueprint YAML
* node-level documentation
* function specification YAMLs

The system works as a **multi-stage pipeline** where the output of one stage becomes the input for the next.

---

# Project Directory Structure

```
core/
llm/
pruning/
data/
specs/
outputs/
main_runner.py
main_prune_runner.py
run_full_pipeline.bat
```

Each major directory contains modules responsible for a specific stage of the pipeline.

---

# ENTRY POINTS

## run_full_pipeline.bat

### Description

Main orchestrator that runs the entire pipeline sequentially.

### Inputs

* user requirement
* JSON configuration files
* previous stage outputs

### Outputs

Triggers generation of:

* stack selection
* pruned structure
* architecture documents
* YAML specifications

### Phases

1. Stack selection
2. Structure pruning
3. Global description generation
4. Blueprint YAML generation
5. Node documentation generation
6. Function specification generation

---

# MAIN EXECUTION FILES

## main_runner.py

### Purpose

Performs **technology stack selection** by navigating a predefined decision tree using an LLM.

### Inputs

* `data/Web_Dev_Only.json`
* user requirement prompt

### Outputs

* `data/stack_meta.json`
* `outputs/langgraph_output.png`
* `specs/final_prompt.txt`

### Main Classes

#### LLMClient

Responsible for interacting with the structured LLM.

**Functions**

`choose_option(prompt, options)`

* Selects a single option from decision tree nodes.

---

### Traversal Functions

`traverse()`

Navigates the decision tree and records selected technology stack.

---

### Helper Functions

`load_tree_from_file()`

* Loads decision tree JSON.

`find_key_recursive()`

* Searches nodes recursively.

`extract_children_from_value()`

* Extracts child nodes from tree.

---

# PRUNING SYSTEM

## main_prune_runner.py

### Purpose

Runs the pruning stage that filters unnecessary folders/files from the global template.

### Inputs

* `data/folder_structure.json`
* `data/stack_meta.json`

### Outputs

* `data/pruned_structure.json`

---

## pruning/pruning_pipeline.py

### Purpose

Core logic that evaluates each node in the structure and decides whether to keep or remove it.

### Inputs

* folder structure JSON
* user requirement
* tech stack summary

### Outputs

* pruned tree structure
* pruning decisions

### Key Functions

`run_pruning_pipeline()`
Main orchestration function.

---

## pruning/pruning_session.py

### Purpose

Handles LLM interaction for pruning decisions.

### Main Function

`evaluate_leaf()`

Determines whether a node should be kept or pruned.

---

## pruning/structure_utils.py

### Purpose

Utility functions for navigating and processing folder structures.

### Key Functions

`find_shallowest_terminal_folder_depth()`
Detects the common depth where pruning begins.

`trim_tree_to_depth()`
Extracts shared structure.

`extract_prunable_nodes()`
Identifies candidate nodes for pruning.

`build_system_context()`
Constructs LLM context prompt.

---

## pruning/tree_pruner.py

### Purpose

Removes nodes marked for pruning.

### Function

`prune_tree()`

Returns filtered folder structure.

---

## pruning/decision_tracker.py

### Purpose

Stores pruning decisions for each node.

### Variables

`decisions`
Dictionary mapping node paths to decisions.

### Functions

`add()`
Adds decision record.

`get()`
Fetches decision for node.

`all()`
Returns all stored decisions.

---

# LLM INTERFACE

## core/llm_structured.py

### Purpose

Wrapper around the LLM to ensure structured outputs.

### Inputs

* prompt
* output schema

### Outputs

Validated Pydantic object.

### Main Class

`StructuredLLM`

### Key Function

`call()`

Calls LLM and validates JSON output.

---

## llm/local_llama_client.py

### Purpose

Unified interface for calling LLM providers.

Supports:

* Ollama
* NVIDIA endpoints

### Main Function

`call_llm(prompt, model)`

Returns LLM response string.

---

# GRAPH VISUALIZATION

## core/langgraph_runner.py

### Purpose

Records decision tree traversal and generates visualization graphs.

### Outputs

* `outputs/langgraph_output.png`

### Main Class

`LangGraphRecorder`

Stores:

* nodes
* edges
* prompts
* rationales

---

## core/folder_graph_builder.py

### Purpose

Visualizes the full folder structure.

### Inputs

* folder_structure.json

### Outputs

* stack_graph.png

---

## core/folder_graph_builder_pruned.py

### Purpose

Visualizes pruned folder structure.

### Outputs

* pruned_structure_graph.png

---

# DOCUMENT GENERATION

## core/global_description_builder.py

### Purpose

Generates the high-level architecture description of the project.

### Inputs

* pruned structure
* tech stack metadata

### Outputs

`specs/global_description.md`

---

## core/global_blueprint_yaml_builder.py

### Purpose

Generates the global blueprint YAML specification.

### Inputs

* architecture description
* stack metadata

### Outputs

`specs/project_blueprint.yaml`

---

## core/node_description_builder.py

### Purpose

Creates detailed documentation for each folder/file.

### Inputs

* pruned structure
* global description
* stack metadata

### Outputs

`specs/node_descriptions/*.md`

---

## core/function_spec_builder.py

### Purpose

Generates structured YAML specifications for functions and variables in each file.

### Inputs

* node descriptions

### Outputs

`specs/function_specs/*.yaml`

---

# DATA FILES

## data/Web_Dev_Only.json

Technology decision tree.

---

## data/folder_structure.json

Global project template structure.

---

## data/stack_meta.json

Selected stack metadata and traversal history.

---

## data/pruned_structure.json

Final project structure after pruning.

---

# OUTPUT FILES

## specs/global_description.md

Global architecture document.

---

## specs/project_blueprint.yaml

Structured blueprint of the entire system.

---

## specs/node_descriptions/

Markdown documentation for every file/folder.

---

## specs/function_specs/

YAML specifications of functions.

---

# Summary

The system transforms a simple user requirement into a **complete architecture specification pipeline** through multiple structured stages.

Each stage progressively refines the project definition while maintaining schema validation and traceability.
