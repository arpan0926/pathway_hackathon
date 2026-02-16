#!/bin/bash
# Cleanup script - Remove generated/demo files before git commit

echo "🧹 Cleaning up generated and demo files..."

# Remove generated CSV files
echo "Removing generated CSV files..."
rm -f data/gps_stream.csv
rm -f data/sample_shipments.json
rm -f outputs/eta_predictions.csv
rm -f pathway_pipeline/gps_stream.csv
rm -f pathway_pipeline/processed_output.csv
rm -f pathway_pipeline/data/*.csv
rm -f pathway_pipeline/outputs/*.csv

# Remove test/demo Python files
echo "Removing test/demo files..."
rm -f test_api.py
rm -f check_system_status.py
rm -f backend/gps_test.py

# Remove Python cache
echo "Removing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete

# Remove venv if exists
echo "Removing virtual environments..."
rm -rf pathway_pipeline/venv

# Keep .gitkeep files
echo "Ensuring .gitkeep files exist..."
touch data/raw/.gitkeep
touch data/processed/.gitkeep
touch outputs/.gitkeep
touch logs/.gitkeep

echo "✅ Cleanup complete!"
echo ""
echo "Files ready for commit. Run:"
echo "  git add ."
echo "  git status"
echo "  git commit -m 'Your commit message'"
