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
echo Running Pruning Phase
echo ================================

python core/folder_graph_builder.py
python main_prune_runner.py
python core/folder_graph_builder_pruned.py
echo.
echo ================================
echo FULL PIPELINE COMPLETE
echo ================================

pause
