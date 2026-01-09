"""Quick test for orchestrator"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import run_all_agents
import pandas as pd

df = pd.read_csv('test_data.csv')
result = run_all_agents(df)

print('[OK] Orchestrator test passed')
print(f'Agents executed: {len(result["agents"])}')
print(f'Total records: {result["total_records"]}')
print(f'Brand agent: {result["agents"]["brand"]["agent_name"]}')
print(f'Pricing agent: {result["agents"]["pricing"]["agent_name"]}')

