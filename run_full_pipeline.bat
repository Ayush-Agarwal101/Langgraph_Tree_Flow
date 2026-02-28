@echo off
cd /d %~dp0

:: Stop on error
setlocal enabledelayedexpansion

:: ----------------------------------------
:: Phase Control
:: Usage:
:: run_full_pipeline.bat
:: run_full_pipeline.bat prune
:: run_full_pipeline.bat global
:: ----------------------------------------

set START_PHASE=%1
if "%START_PHASE%"=="" set START_PHASE=stack

echo ==========================================
echo Starting pipeline from phase: %START_PHASE%
echo ==========================================
echo.

:: ==========================================
:: STACK SELECTION
:: ==========================================
if /I "%START_PHASE%"=="stack" (

    echo ================================
    echo Running Stack Selection Phase
    echo ================================

    python main_runner.py ^
     --json-file data/Web_Dev_Only.json ^
     --start-node "Core Application & Web Stacks" ^
     --initial-prompt "build a backend for online bakery shop" ^
     --output-meta data/stack_meta.json
    if %errorlevel% neq 0 exit /b %errorlevel%

    echo.
    echo ================================
    echo Generating Stack Graph
    echo ================================

    python core/folder_graph_builder.py ^
     --json-file data/folder_structure.json ^
     --output outputs/stack_graph
    if %errorlevel% neq 0 exit /b %errorlevel%

    echo.
    set START_PHASE=prune
)

:: ==========================================
:: PRUNING
:: ==========================================
if /I "%START_PHASE%"=="prune" (

    echo ================================
    echo Running Pruning Phase
    echo ================================

    python main_prune_runner.py
    if %errorlevel% neq 0 exit /b %errorlevel%

    echo.
    echo ================================
    echo Generating Pruned Graph
    echo ================================

    python core/folder_graph_builder_pruned.py ^
     --json-file data/pruned_structure.json ^
     --output outputs/pruned_structure_graph
    if %errorlevel% neq 0 exit /b %errorlevel%

    echo.
    set START_PHASE=global
)

:: ==========================================
:: GLOBAL DESCRIPTION
:: ==========================================
if /I "%START_PHASE%"=="global" (

    echo ================================
    echo Generating Global Description
    echo ================================

    python core/global_description_builder.py ^
     --pruned data/pruned_structure.json ^
     --meta data/stack_meta.json ^
     --output specs/global_description.md
    if %errorlevel% neq 0 exit /b %errorlevel%

    echo.
    set START_PHASE=blueprint
)

:: ==========================================
:: PROJECT BLUEPRINT YAML
:: ==========================================
if /I "%START_PHASE%"=="blueprint" (

    echo ================================
    echo Generating Project Blueprint YAML
    echo ================================

    python core/global_blueprint_yaml_builder.py ^
     --global-desc specs/global_description.md ^
     --meta data/stack_meta.json
    if %errorlevel% neq 0 exit /b %errorlevel%

    echo.
    set START_PHASE=nodes
)

:: ==========================================
:: NODE DESCRIPTIONS
:: ==========================================
if /I "%START_PHASE%"=="nodes" (

    echo ================================
    echo Generating Node Descriptions
    echo ================================

    python core/node_description_builder.py ^
     --pruned data/pruned_structure.json ^
     --meta data/stack_meta.json ^
     --global-desc specs/global_description.md ^
     --output-dir specs/node_descriptions
    if %errorlevel% neq 0 exit /b %errorlevel%

    echo.
    set START_PHASE=functions
)

:: ==========================================
:: FUNCTION SPECS
:: ==========================================
if /I "%START_PHASE%"=="functions" (

    echo ================================
    echo Generating Function Specs
    echo ================================

    python core/function_spec_builder.py ^
     --node-docs specs/node_descriptions ^
     --output specs/function_specs
    if %errorlevel% neq 0 exit /b %errorlevel%

    echo.
    set START_PHASE=code
)

echo ==========================================
echo FULL PIPELINE COMPLETE
echo ==========================================
pause