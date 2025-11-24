"""
SWE-bench specific implementation
Generates patches AND automatically evaluates them
"""
from typing import Dict, List, Any, Callable
from datasets import load_dataset
import subprocess
import tempfile
from pathlib import Path

from core.runners.base import BenchmarkRunner, TaskResult, APIClient
from core.config import SWEBenchConfig, ModelConfig
from core.prompts import SWEBenchPrompts, DEFAULT_SWEBENCH_PROMPT


class SWEBenchPromptStrategy:
    """
    Prompt strategy selector for SWE-bench
    Allows easy switching between different prompting approaches
    """

    # Available strategies
    STRATEGIES = {
        "minimal": SWEBenchPrompts.minimal,
        "structured": SWEBenchPrompts.structured,
        "few_shot": SWEBenchPrompts.few_shot,
        "chain_of_thought": SWEBenchPrompts.chain_of_thought,
        "agent_style": SWEBenchPrompts.agent_style,
        "direct": SWEBenchPrompts.direct_instruction,
        "template": SWEBenchPrompts.template_based,
        "zero_shot_cot": SWEBenchPrompts.zero_shot_cot,
        "best_practice": SWEBenchPrompts.best_practice,
    }

    def __init__(self, strategy: str = "best_practice"):
        """
        Initialize with a strategy name

        Args:
            strategy: One of the available strategies
        """
        if strategy not in self.STRATEGIES:
            raise ValueError(f"Unknown strategy: {strategy}. Available: {list(self.STRATEGIES.keys())}")

        self.strategy = strategy
        self.prompt_fn = self.STRATEGIES[strategy]

    def create_prompt(self, instance: Dict) -> str:
        """Create prompt using selected strategy"""
        return self.prompt_fn(instance)

    @classmethod
    def list_strategies(cls) -> List[str]:
        """List all available prompting strategies"""
        return list(cls.STRATEGIES.keys())


class SWEBenchRunner(BenchmarkRunner):
    """
    SWE-bench runner with auto-evaluation
    Inherits base orchestration, implements SWE-bench specifics
    """

    def __init__(self, config: SWEBenchConfig, model_config: ModelConfig,
                 prompt_strategy: str = "best_practice"):
        super().__init__(config, model_config)
        self.client = APIClient(model_config)
        self.output_dir = Path("outputs/swebench")
        self.predictions_file = self.output_dir / "predictions.jsonl"

        # Initialize prompt strategy
        self.prompt_strategy = SWEBenchPromptStrategy(prompt_strategy)
        self.logger.info(f"Using prompt strategy: {prompt_strategy}")

    def load_dataset(self) -> List[Dict]:
        """Load SWE-bench dataset"""
        self.logger.info(f"Loading dataset: {self.config.dataset}")
        dataset = load_dataset(self.config.dataset, split=self.config.split)
        return list(dataset)

    def process_instance(self, instance: Dict) -> TaskResult:
        """
        Process single SWE-bench instance
        Generate patch using model
        """
        instance_id = instance["instance_id"]
        self.logger.info(f"Processing {instance_id}")

        # Generate prompt using selected strategy
        prompt = self.prompt_strategy.create_prompt(instance)

        # Call model API
        patch = self.client.generate(prompt)

        if patch:
            self.logger.info(f"✅ Generated patch ({len(patch)} chars)")
            return TaskResult(
                instance_id=instance_id,
                success=True,
                output={"model_patch": patch, "model_name": self.model_config.name}
            )
        else:
            self.logger.warning(f"❌ Failed to generate patch")
            return TaskResult(
                instance_id=instance_id,
                success=False,
                error="Patch generation failed"
            )

    def evaluate_results(self) -> Dict[str, Any]:
        """
        Automatically evaluate generated patches
        Runs SWE-bench evaluation harness if enabled
        """
        if not self.config.run_docker_eval:
            self.logger.info("Docker evaluation disabled, skipping")
            return {"evaluation": "skipped"}

        self.logger.info("Running SWE-bench evaluation harness...")

        try:
            # Run official SWE-bench evaluation
            eval_output = self.output_dir / "evaluation_results"
            cmd = [
                "python", "-m", "swebench.harness.run_evaluation",
                "--predictions_path", str(self.predictions_file),
                "--dataset_name", self.config.dataset,
                "--output_dir", str(eval_output)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )

            if result.returncode == 0:
                # Parse evaluation results
                metrics = self.parse_eval_results(eval_output)
                return metrics
            else:
                self.logger.error(f"Evaluation failed: {result.stderr}")
                return {"evaluation": "failed", "error": result.stderr}

        except FileNotFoundError:
            self.logger.warning("swebench not installed, skipping evaluation")
            return {"evaluation": "skipped", "reason": "swebench not installed"}
        except Exception as e:
            self.logger.error(f"Evaluation error: {e}")
            return {"evaluation": "error", "error": str(e)}

    def parse_eval_results(self, eval_dir: Path) -> Dict[str, Any]:
        """Parse SWE-bench evaluation results"""
        import json

        results_file = eval_dir / "results.json"
        if not results_file.exists():
            return {"evaluation": "no_results"}

        with open(results_file) as f:
            data = json.load(f)

        resolved = data.get("resolved", 0)
        total = data.get("total", len(self.results))

        return {
            "pass@1": resolved / total if total > 0 else 0,
            "resolved": resolved,
            "total": total,
            "evaluation": "completed"
        }
