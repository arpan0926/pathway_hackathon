#!/bin/bash
# Script to run all components (Linux/Mac)

echo "Starting GPS Simulator..."
cd backend && python simulator.py &

echo "Starting Pathway Pipeline..."
cd pathway_pipeline && python pipeline.py &

echo "Starting Backend API..."
cd backend && uvicorn main:app --reload --port 8000 &

echo "Starting Dashboard..."
cd dashboard && streamlit run app.py &

echo "All components started!"
echo "Dashboard: http://localhost:8501"
echo "API: http://localhost:8000"
