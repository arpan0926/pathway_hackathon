@echo off
REM Script to run all components (Windows)

echo Starting GPS Simulator...
start cmd /k "cd backend && python simulator.py"

echo Starting Pathway Pipeline...
start cmd /k "cd pathway_pipeline && python pipeline.py"

echo Starting Backend API...
start cmd /k "cd backend && uvicorn main:app --reload --port 8000"

echo Starting Dashboard...
start cmd /k "cd dashboard && streamlit run app.py"

echo All components started!
echo Dashboard: http://localhost:8501
echo API: http://localhost:8000
pause
