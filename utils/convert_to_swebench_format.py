#!/usr/bin/env python3
"""
Convert our predictions format to SWE-bench official format
"""
import json
from pathlib import Path

def convert_predictions(input_file, output_file):
    """Convert predictions to SWE-bench format"""

    converted = []

    with open(input_file, 'r') as f:
        for line in f:
            pred = json.loads(line)

            # Convert to SWE-bench format
            swebench_pred = {
                "instance_id": pred["instance_id"],
                "model_patch": pred["output"]["model_patch"],
                "model_name_or_path": pred["output"]["model_name"]
            }

            converted.append(swebench_pred)

    # Write in SWE-bench format
    with open(output_file, 'w') as f:
        for pred in converted:
            f.write(json.dumps(pred) + '\n')

    print(f"✅ Converted {len(converted)} predictions")
    print(f"📁 Output: {output_file}")

if __name__ == "__main__":
    input_file = Path("outputs/swebench/predictions.jsonl")
    output_file = Path("outputs/swebench/predictions_swebench_format.jsonl")

    convert_predictions(input_file, output_file)
