#!/bin/bash
echo "Setting up virtual environment..."
python -m venv env
source env/bin/activate
pip install -r requirements.txt
echo "Setup complete. Launch with: streamlit run recipe_intelligence/app.py"