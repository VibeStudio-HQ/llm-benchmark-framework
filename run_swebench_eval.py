#!/usr/bin/env python3
"""
Simple SWE-bench evaluation runner
Temperature set to 1.0 for sampling diversity
"""
import sys
from pathlib import Path

# Add benchmarks to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "benchmarks"))

from swebench.runner import SWEBenchRunner
from configs.base_config import ModelConfig, SWEBenchConfig, EvaluationConfig

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run SWE-bench evaluation")

    parser.add_argument("--model_name", required=True, help="Model name")
    parser.add_argument("--api_url", required=True, help="API endpoint URL")
    parser.add_argument("--num_instances", type=int, default=10, help="Number of instances (default: 10)")
    parser.add_argument("--temperature", type=float, default=1.0, help="Temperature (default: 1.0)")

    args = parser.parse_args()

    # Create configuration
    model_config = ModelConfig(
        name=args.model_name,
        api_url=args.api_url,
        temperature=args.temperature,
        max_tokens=4096,
    )

    swebench_config = SWEBenchConfig(
        enabled=True,
        num_instances=args.num_instances,
        run_docker_eval=False,  # Set to True to run Docker evaluation
        prompt_strategy="minimal",
    )

    print("="*70)
    print("SWE-bench Evaluation")
    print("="*70)
    print(f"Model: {model_config.name}")
    print(f"API: {model_config.api_url}")
    print(f"Temperature: {model_config.temperature}")
    print(f"Instances: {swebench_config.num_instances}")
    print(f"Prompt Strategy: {swebench_config.prompt_strategy}")
    print("="*70)

    # Run evaluation
    runner = SWEBenchRunner(swebench_config, model_config)
    result = runner.run()

    print("\n" + "="*70)
    print("Evaluation Complete!")
    print("="*70)
    print(f"Results saved to: outputs/swebench/")
    print("="*70)

if __name__ == "__main__":
    main()
