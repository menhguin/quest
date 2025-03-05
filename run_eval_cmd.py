import subprocess
import sys
import os
import json

# Get the Python executable from the virtual environment
python_executable = sys.executable

# Create a Python script that uses evaluate instead of evaluate_from_model_outputs
temp_script = """
import sys
import os
from alpaca_eval.main import evaluate
import pandas as pd

# Run the evaluation
results, annotations = evaluate(
    model_outputs='data/outputs/aeval_all.json',
    reference_outputs='data/outputs/aeval_7b_temp100.json',
    annotators_config='alpaca_eval_cot_gpt4_turbo_fn',
    is_return_instead_of_print=True
)

# Save the results to a CSV file
results.to_csv('leaderboard.csv', index=False)

# Print a summary of the results
print("\\nEvaluation Results:")
print(results[['win_rate', 'standard_error', 'n_total']].to_string(float_format="%.2f"))
print(f"\\nResults saved to leaderboard.csv")
"""

# Write the temporary script to a file
with open("temp_eval.py", "w") as f:
    f.write(temp_script)

# Run the temporary script
cmd = [python_executable, "temp_eval.py"]

print("Using Python executable:", python_executable)
print("Running evaluation script...")
result = subprocess.run(cmd, capture_output=True, text=True)

print("\nCommand output:")
print(result.stdout)

if result.stderr:
    print("\nErrors:")
    print(result.stderr)

print(f"\nExit code: {result.returncode}")

# Clean up the temporary script
os.remove("temp_eval.py") 