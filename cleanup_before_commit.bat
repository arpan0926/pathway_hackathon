@echo off
REM Cleanup script - Remove generated/demo files before git commit

echo Cleaning up generated and demo files...

REM Remove generated CSV files
echo Removing generated CSV files...
if exist data\gps_stream.csv del /f data\gps_stream.csv
if exist data\sample_shipments.json del /f data\sample_shipments.json
if exist outputs\eta_predictions.csv del /f outputs\eta_predictions.csv
if exist pathway_pipeline\gps_stream.csv del /f pathway_pipeline\gps_stream.csv
if exist pathway_pipeline\processed_output.csv del /f pathway_pipeline\processed_output.csv
if exist pathway_pipeline\data\*.csv del /f pathway_pipeline\data\*.csv
if exist pathway_pipeline\outputs\*.csv del /f pathway_pipeline\outputs\*.csv

REM Remove test/demo Python files
echo Removing test/demo files...
if exist test_api.py del /f test_api.py
if exist check_system_status.py del /f check_system_status.py
if exist backend\gps_test.py del /f backend\gps_test.py

REM Remove Python cache
echo Removing Python cache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul

REM Remove venv if exists
echo Removing virtual environments...
if exist pathway_pipeline\venv rd /s /q pathway_pipeline\venv

REM Keep .gitkeep files
echo Ensuring .gitkeep files exist...
type nul > data\raw\.gitkeep
type nul > data\processed\.gitkeep
type nul > outputs\.gitkeep
type nul > logs\.gitkeep

echo.
echo Cleanup complete!
echo.
echo Files ready for commit. Run:
echo   git add .
echo   git status
echo   git commit -m "Your commit message"
