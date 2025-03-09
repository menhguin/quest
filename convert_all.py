import json
import sys
import os

# Implement read_jsonl directly instead of importing
def read_jsonl(file_name):
    with open(file_name, encoding="utf-8") as r:
        return [json.loads(line) for line in r]

def postprocess(record):
    source = record.get("source", "")
    output = record["output"]
    if source == "pippa":
        output = output.split("User:")[0]
        output = output.strip()
        if len(output) > 500:
            output = output.split("\n")[0]
            output = output.strip()
    record["output"] = output
    return record

def to_alpaca_eval(records):
    records = [postprocess(r) for r in records]
    records = [{
        "instruction": r["prompt"],
        "output": r["output"],
        "generator": r["config_name"].replace(".json", ""),
    } for r in records]
    return records

def convert_file(input_path, output_path):
    print(f"Reading from {input_path}")
    
    # Check if input file exists
    if not os.path.exists(input_path):
        print(f"Warning: {input_path} does not exist. Skipping.")
        return False
    
    records = list(read_jsonl(input_path))
    print(f"Found {len(records)} records")
    
    records = to_alpaca_eval(records)
    print(f"Converting to AlpacaEval format")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w") as w:
        json.dump(records, w, indent=4)
    
    print(f"Saved to {output_path}")
    return True

def main():
    # Files to convert based on the results_to_repro table
    files_to_convert = [
        # Temperature 1.5
        "7b_temp150_minp_10.jsonl",  # min_p=0.1
        "7b_temp150_minp_05.jsonl",  # min_p=0.05
        "7b_temp150_minp_02.jsonl",  # min_p=0.02
        "7b_temp150_topp_98.jsonl",  # top_p=0.98 (might be FAIL in results)
        "7b_temp150_topp_95.jsonl",  # top_p=0.95 (might be FAIL in results)
        "7b_temp150_topp_90.jsonl",  # top_p=0.9 (might be FAIL in results)
        "7b_temp150_topp_80.jsonl",  # top_p=0.8 (might be FAIL in results)
        
        # Temperature 1.0
        "7b_temp100_minp_05.jsonl",  # min_p=0.05
        "7b_temp100_topp_98.jsonl",  # top_p=0.98
        "7b_tfs_95.jsonl",           # tfs=0.95
        "7b_temp100_minp_10.jsonl",  # min_p=0.1
        "7b_temp100_topp_90.jsonl",  # top_p=0.9
        "7b_temp100_minp_02.jsonl",  # min_p=0.02
        "7b_temp100_topp_95.jsonl",  # top_p=0.95
        
        # Temperature 0.8
        "7b_temp80_topp_98.jsonl",   # top_p=0.98
        "7b_temp80_topp_95.jsonl",   # top_p=0.95
        "7b_temp80_minp_05.jsonl",   # min_p=0.05
        "7b_temp80_minp_02.jsonl",   # min_p=0.02
        
        # Temperature 0.0
        "7b_greedy.jsonl",           # greedy (no constraints)
        
        # Special cases
        "7b_dynatemp_50_150_75_minp_05.jsonl",  # min_p=0.05, exp=0.75
        "7b_mirostat_50_10.jsonl",   # mirostat_tau=5.0
        "7b_mirostat_60_10.jsonl",   # mirostat_tau=4.0
    ]
    
    # Check for files that might have different naming conventions
    file_mapping = {
        "7b_temp150_topp_98.jsonl": ["7b_temp150_topp_98.jsonl", "7b_temp150_top_p_98.jsonl"],
        "7b_temp150_topp_95.jsonl": ["7b_temp150_topp_95.jsonl", "7b_temp150_top_p_95.jsonl"],
        "7b_temp150_topp_90.jsonl": ["7b_temp150_topp_90.jsonl", "7b_temp150_top_p_90.jsonl"],
        "7b_temp150_topp_80.jsonl": ["7b_temp150_topp_80.jsonl", "7b_temp150_top_p_80.jsonl"],
    }
    
    # Convert each file
    converted_files = []
    for file in files_to_convert:
        # Check for alternative file names
        if file in file_mapping:
            found = False
            for alt_file in file_mapping[file]:
                input_path = f"quest/data/outputs/{alt_file}"
                if os.path.exists(input_path):
                    output_path = f"quest/data/outputs/aeval_{alt_file.replace('.jsonl', '.json')}"
                    if convert_file(input_path, output_path):
                        converted_files.append(output_path)
                        found = True
                        break
            if not found:
                print(f"Warning: Could not find any alternative for {file}. Skipping.")
        else:
            input_path = f"quest/data/outputs/{file}"
            output_path = f"quest/data/outputs/aeval_{file.replace('.jsonl', '.json')}"
            
            if convert_file(input_path, output_path):
                converted_files.append(output_path)
    
    # Create a combined file with all outputs
    print("\nCreating combined file with all outputs...")
    all_records = []
    for output_file in converted_files:
        with open(output_file, "r") as f:
            records = json.load(f)
            all_records.extend(records)
    
    with open("quest/data/outputs/aeval_all.json", "w") as w:
        json.dump(all_records, w, indent=4)
    
    print(f"Saved combined file to quest/data/outputs/aeval_all.json")
    print(f"Total records in combined file: {len(all_records)}")
    print(f"Total unique configurations: {len(converted_files)}")

if __name__ == "__main__":
    main() 