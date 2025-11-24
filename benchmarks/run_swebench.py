#!/usr/bin/env python3
"""
Main orchestrator for running all benchmarks
Single entry point with clean configuration
"""
import argparse
from datetime import datetime
from pathlib import Path
import json
import sys

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))

from core.config import (
    ModelConfig, SWEBenchConfig, CodeEvalConfig,
    ReasoningConfig, MathConfig, EvaluationConfig
)
from tasks.swebench import SWEBenchRunner
from tasks.code_eval import CodeEvalRunner
from tasks.reasoning import ReasoningRunner
from tasks.math import MathRunner


class BenchmarkOrchestrator:
    """
    Orchestrates execution of all benchmarks
    Clean separation of concerns
    """

    def __init__(self, config: EvaluationConfig):
        self.config = config
        self.results = {}

    def run_all(self):
        """Run all enabled benchmarks"""
        print("="*70)
        print("LLM Benchmark Framework")
        print("="*70)
        print(f"Model: {self.config.model.name}")
        print(f"API: {self.config.model.api_url}")
        print("="*70)

        enabled = self.config.get_enabled_benchmarks()
        print(f"\nEnabled benchmarks: {[b.name for b in enabled]}\n")

        # Run each benchmark
        for benchmark_config in enabled:
            result = self.run_benchmark(benchmark_config)
            self.results[benchmark_config.name] = result

        # Generate final report
        if self.config.generate_report:
            self.generate_report()

        print("\n" + "="*70)
        print("All benchmarks completed!")
        print("="*70)

    def run_benchmark(self, benchmark_config):
        """Run single benchmark based on type"""
        runner = self.get_runner(benchmark_config)

        if runner is None:
            print(f"⚠️  Unknown benchmark type: {benchmark_config.name}")
            return None

        print(f"\n{'='*70}")
        print(f"Running: {benchmark_config.name}")
        print(f"{'='*70}\n")

        try:
            result = runner.run()
            return result
        except Exception as e:
            print(f"❌ Benchmark {benchmark_config.name} failed: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}

    def get_runner(self, benchmark_config):
        """Factory method to get appropriate runner"""
        runners = {
            "swebench": lambda: SWEBenchRunner(
                benchmark_config,
                self.config.model,
                prompt_strategy=benchmark_config.prompt_strategy
            ),
            "code_eval": lambda: CodeEvalRunner(benchmark_config, self.config.model),
            "reasoning": lambda: ReasoningRunner(benchmark_config, self.config.model),
            "math": lambda: MathRunner(benchmark_config, self.config.model),
        }

        runner_factory = runners.get(benchmark_config.name)
        return runner_factory() if runner_factory else None

    def generate_report(self):
        """Generate consolidated report"""
        report_file = self.config.output_dir / "consolidated_report.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)

        report = {
            "model": self.config.model.name,
            "timestamp": datetime.now().isoformat(),
            "benchmarks": self.results
        }

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📊 Consolidated report saved: {report_file}")

        # Print summary table
        self.print_summary()

    def print_summary(self):
        """Print results summary table"""
        print("\n" + "="*70)
        print("RESULTS SUMMARY")
        print("="*70)

        for benchmark_name, result in self.results.items():
            if result and "evaluation_metrics" in result:
                print(f"\n{benchmark_name.upper()}:")
                metrics = result["evaluation_metrics"]
                for key, value in metrics.items():
                    print(f"  {key}: {value}")


def create_config_from_args(args) -> EvaluationConfig:
    """Create configuration from command line arguments"""

    # Model configuration
    model_config = ModelConfig(
        name=args.model_name,
        api_url=args.api_url,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )

    # Benchmark configurations
    swebench_config = None
    if args.run_swebench:
        swebench_config = SWEBenchConfig(
            enabled=True,
            num_instances=args.num_instances,
            run_docker_eval=args.run_docker_eval,
            prompt_strategy=args.prompt_strategy,
        )

    code_eval_config = None
    if args.run_code_eval:
        code_eval_config = CodeEvalConfig(
            enabled=True,
            tasks=args.code_eval_tasks.split(",") if args.code_eval_tasks else ["humaneval", "mbpp"],
        )

    reasoning_config = None
    if args.run_reasoning:
        reasoning_config = ReasoningConfig(
            enabled=True,
            parallel_tasks=args.parallel_tasks,
        )

    math_config = None
    if args.run_math:
        math_config = MathConfig(
            enabled=True,
            eval_batch_size=args.parallel_tasks,
        )

    return EvaluationConfig(
        model=model_config,
        swebench=swebench_config,
        code_eval=code_eval_config,
        reasoning=reasoning_config,
        math=math_config,
        output_dir=Path(args.output_dir),
        generate_report=True,
    )


def main():
    parser = argparse.ArgumentParser(
        description="LLM Benchmark Framework - Run all evaluations"
    )

    # Model arguments
    parser.add_argument("--model_name", required=True, help="Model name/path")
    parser.add_argument("--api_url", required=True, help="API endpoint URL")
    parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature")
    parser.add_argument("--max_tokens", type=int, default=4096, help="Max tokens to generate")

    # Benchmark selection
    parser.add_argument("--run_swebench", action="store_true", help="Run SWE-bench")
    parser.add_argument("--run_code_eval", action="store_true", help="Run code evaluation")
    parser.add_argument("--run_reasoning", action="store_true", help="Run reasoning benchmarks")
    parser.add_argument("--run_math", action="store_true", help="Run math benchmarks")
    parser.add_argument("--run_all", action="store_true", help="Run all benchmarks")

    # SWE-bench specific
    parser.add_argument("--num_instances", type=int, default=None, help="Number of instances to run")
    parser.add_argument("--run_docker_eval", action="store_true", help="Run Docker evaluation for SWE-bench")
    parser.add_argument("--prompt_strategy", type=str, default="minimal",
                        choices=["minimal", "structured", "few_shot", "chain_of_thought",
                                "agent_style", "direct", "template", "zero_shot_cot", "best_practice"],
                        help="Prompting strategy for SWE-bench (default: minimal - matches original working code)")

    # Code eval specific
    parser.add_argument("--code_eval_tasks", type=str, default="humaneval,mbpp", help="Comma-separated code eval tasks")

    # General
    parser.add_argument("--parallel_tasks", type=int, default=4, help="Parallel tasks")
    parser.add_argument("--output_dir", default="./outputs", help="Output directory")

    args = parser.parse_args()

    # If run_all, enable all benchmarks
    if args.run_all:
        args.run_swebench = True
        args.run_code_eval = True
        args.run_reasoning = True
        args.run_math = True

    # Create configuration
    config = create_config_from_args(args)

    # Run orchestrator
    orchestrator = BenchmarkOrchestrator(config)
    orchestrator.run_all()


if __name__ == "__main__":
    main()
