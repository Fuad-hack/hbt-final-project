#!/bin/bash
set -e

echo "=== Step 1/7: Data Simulation ==="
python data/simulate_logs.py

echo "=== Step 2/7: Red Team Simulation ==="
python data/simulate_red_team.py

echo "=== Step 3/7: Feature Engineering ==="
python features/feature_engineering.py

echo "=== Step 4/7: NLP Email Features ==="
python features/nlp_email_features.py

echo "=== Step 5/7: Graph Feature Extraction ==="
python gnn/gnn_anomaly.py

echo "=== Step 6/7: Merging Features ==="
python features/merge_features.py

echo "=== Step 7/7: Model Training ==="
python models/train.py

echo "=== All pipeline steps complete. Starting Dashboard ==="
exec streamlit run dashboard/combined_dashboard.py --server.port=8501 --server.address=0.0.0.0
