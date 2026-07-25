@echo off
setlocal

echo [1/4] Running all unit tests...
python -m unittest discover -s tests -p "test_*.py" -v
if errorlevel 1 exit /b 1

echo [2/4] Running core benchmark...
python benchmark.py --levels LEVEL1 LEVEL2 LEVEL4 LEVEL6 LEVEL9 LEVEL10 --algorithms BFS UCS "A*" --repeats 5 --output benchmark_results\final_core.csv
if errorlevel 1 exit /b 1

echo [3/4] Running DFS benchmark...
python benchmark.py --levels LEVEL1 LEVEL2 --algorithms DFS --repeats 5 --output benchmark_results\final_dfs.csv
if errorlevel 1 exit /b 1

echo [4/4] Building benchmark summary and release ZIP...
python tools\summarize_benchmark.py --input benchmark_results\final_core.csv benchmark_results\final_dfs.csv --output-dir benchmark_results\final
if errorlevel 1 exit /b 1

python tools\package_release.py
if errorlevel 1 exit /b 1

echo.
echo All final checks completed successfully.
endlocal
