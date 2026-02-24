@echo off

echo ================================
echo Running Stack Selection Phase
echo ================================

python main_runner.py ^
 --json-file data/Web_Dev_Only.json ^
 --start-node "Core Application & Web Stacks" ^
 --initial-prompt "build a backend for online bakery shop"

echo.
echo ================================
echo Generating Stack Graph
echo ================================

python core/folder_graph_builder.py ^
 --json-file data/folder_structure.json ^
 --output stack_graph

echo.
echo ================================
echo Running Pruning Phase
echo ================================

python main_prune_runner.py

echo.
echo ================================
echo Generating Pruned Graph
echo ================================

python core/folder_graph_builder_pruned.py ^
 --json-file data/pruned_structure.json ^
 --output pruned_structure_graph

echo.
echo ================================
echo FULL PIPELINE COMPLETE
echo ================================

pause