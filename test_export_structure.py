"""Test export structure"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import run_all_agents
import pandas as pd
import json

# Run analysis
df = pd.read_csv('test_data.csv')
results = run_all_agents(df)

# Prepare export data (same as UI)
export_data = {
    "timestamp": results["timestamp"],
    "total_records": results["total_records"],
    "agent_outputs": [
        results["agents"]["brand"],
        results["agents"]["pricing"],
        results["agents"]["feature"],
        results["agents"]["gap"]
    ],
    "llm_summary": None
}

# Test JSON serialization
json_str = json.dumps(export_data, indent=2, ensure_ascii=False)

print("[OK] Export structure test passed")
print(f"JSON length: {len(json_str)} characters")
print(f"Agent outputs: {len(export_data['agent_outputs'])}")
print(f"Keys: {list(export_data.keys())}")

# Verify reports directory
reports_dir = Path("reports")
reports_dir.mkdir(exist_ok=True)
print(f"[OK] Reports directory: {reports_dir.exists()}")

