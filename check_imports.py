import sys, os, subprocess

# Test: reproduce seed_db's import chain
result = subprocess.run(
    [sys.executable, '-X', 'utf8', '-c', """
import sys, os
sys.path.insert(0, '.')
print("Step 1: importing anomaly_model...")
from backend.models.anomaly_model import train_model
print("Step 2: importing rag_pipeline...")
from backend.models.rag_pipeline import seed_mock_codebase
print("Step 3: seeding DB...")
print("Step 3a: train_model...")
train_model()
print("Step 3b: seed_mock_codebase...")
seed_mock_codebase()
print("ALL DONE")
"""],
    capture_output=True, text=True, encoding='utf-8'
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr[-2000:] if result.stderr else "(none)")
print("RC:", result.returncode)
