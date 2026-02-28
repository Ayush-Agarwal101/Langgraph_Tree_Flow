# 🧠 AI Architecture & Specification Pipeline

This project is a multi-stage AI-powered architecture compiler that converts a high-level user requirement into a structured project blueprint and detailed function specifications.

The pipeline is modular and deterministic after specification generation.

---

# 🚀 Pipeline Overview

The system works in the following major stages:

---

## 🔹 Step 1 — Stack Selection

### 🔍 Description

Selects the most appropriate technology stack by navigating a predefined decision tree using an LLM.

The model selects one option per node until it reaches a leaf stack.

### 📥 Inputs

* `data/Web_Dev_Only.json` (technology decision tree)
* User initial prompt (project requirement)

### 📤 Outputs

* `data/stack_meta.json`
  Contains:

  * User requirement
  * Selected tech stack
  * Choice rationales
  * Traversal metadata
* `outputs/langgraph_output.png` (visual stack path)
* `specs/final_prompt.txt` (human-readable stack summary)

---

## 🔹 Step 2 — Structure Pruning

### 🔍 Description

Prunes a global folder blueprint based on:

* User requirement
* Selected tech stack

Each file/folder is evaluated by the LLM to decide whether to KEEP or PRUNE.

Mandatory nodes are always kept.

### 📥 Inputs

* `data/folder_structure.json` (global template)
* `data/stack_meta.json`

### 📤 Outputs

* `data/pruned_structure.json` (filtered structure)
* `outputs/pruned_structure_graph.png` (visual structure graph)

---

## 🔹 Step 3 — Global Architecture Description

### 🔍 Description

Generates a detailed high-level architectural description of the entire pruned project.

This defines:

* System design
* Core modules
* Responsibilities
* Data flow
* Architectural decisions

### 📥 Inputs

* `data/pruned_structure.json`
* `data/stack_meta.json`

### 📤 Outputs

* `specs/global_description.md`

This becomes the authoritative architecture document.

---

## 🔹 Step 4 — Global Blueprint YAML

### 🔍 Description

Converts the architectural description into a strict, machine-validated YAML specification.

This defines:

* Project metadata
* Architecture pattern
* Entry points
* Components
* Infrastructure
* Dependencies

Structured and validated via Pydantic.

### 📥 Inputs

* `specs/global_description.md`
* `data/stack_meta.json`

### 📤 Outputs

* `specs/project_blueprint.yaml`

This file becomes the structured "single source of truth" for the overall system.

---

## 🔹 Step 5 — Node-Level Documentation

### 🔍 Description

Generates detailed documentation for every file and folder in the pruned structure.

Each node receives structured Markdown documentation including:

* Purpose
* Responsibilities
* Key Functions (conceptual)
* Interactions
* Extensibility considerations

This ensures consistency with global architecture.

### 📥 Inputs

* `data/pruned_structure.json`
* `data/stack_meta.json`
* `specs/global_description.md`

### 📤 Outputs

* `specs/node_descriptions/`

  * One `.md` file per file/folder in the project

---

## 🔹 Step 6 — Function Specification YAML

### 🔍 Description

Converts structured node documentation into strict YAML specifications for each file.

Defines:

* Module metadata
* Variables
* Function names
* Parameters
* Return types
* Intended responsibilities

These are deterministic and schema-validated.

### 📥 Inputs

* `specs/node_descriptions/`

### 📤 Outputs

* `specs/function_specs/`

  * One `.yaml` file per file

---

# 📂 Final Project Structure (After Pipeline)

```
data/
├── stack_meta.json
├── pruned_structure.json

outputs/
├── langgraph_output.png
├── pruned_structure_graph.png

specs/
├── final_prompt.txt
├── global_description.md
├── project_blueprint.yaml
├── node_descriptions/
└── function_specs/
```

---

# 🧠 Architectural Philosophy

The system is designed as:

```
User Requirement
        ↓
Stack Decision
        ↓
Structure Pruning
        ↓
Architecture Description
        ↓
Structured Blueprint YAML
        ↓
Per-Node Documentation
        ↓
Function Specifications
```

Key principles:

* Strict schema validation (Pydantic)
* Deterministic outputs after YAML stage
* Modular, restartable pipeline
* Phase-controlled execution
* Separation of architecture vs implementation

---

# ▶️ Running the Pipeline

Run full pipeline:

```
run_full_pipeline.bat
```

Start from a specific phase:

```
run_full_pipeline.bat prune
run_full_pipeline.bat global
run_full_pipeline.bat blueprint
run_full_pipeline.bat functions
```

---

# 🔮 Future Extensions (Optional)

Potential future stages:

* Code skeleton generation
* Test generation
* CI/CD config generation
* Infrastructure-as-code templates
* API contract validation

---

# 📌 Current Scope

The pipeline currently generates:

* Tech stack selection
* Pruned project structure
* Global architecture documentation
* Blueprint YAML specification
* Per-file function specifications

It does NOT generate implementation code at this stage.