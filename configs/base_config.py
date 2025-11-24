"""
Base configuration for LLM Benchmark Framework
"""
from dataclasses import dataclass, field
from typing import Optional, List
from pathlib import Path


@dataclass
class ModelConfig:
    """Configuration for the model to evaluate"""
    name: str
    api_url: str
    api_type: str = "openai"  # openai, vllm, anthropic, etc.
    api_key: Optional[str] = None
    temperature: float = 0.0
    max_tokens: int = 4096
    top_p: float = 1.0
    timeout: int = 180


@dataclass
class BenchmarkConfig:
    """Base configuration for any benchmark"""
    name: str
    enabled: bool = True
    num_instances: Optional[int] = None  # None = run all
    start_index: int = 0
    parallel_tasks: int = 4
    save_incremental: bool = True
    auto_evaluate: bool = True  # Run evaluation after generation


@dataclass
class SWEBenchConfig(BenchmarkConfig):
    """SWE-bench specific configuration"""
    name: str = "swebench"
    dataset: str = "princeton-nlp/SWE-bench_Lite"
    split: str = "test"
    run_docker_eval: bool = True  # Run full Docker evaluation
    docker_timeout: int = 300
    prompt_strategy: str = "minimal"  # Which prompting strategy to use (matches original working code)
    # Options: minimal, structured, few_shot, chain_of_thought, agent_style,
    #          direct, template, zero_shot_cot, best_practice


@dataclass
class CodeEvalConfig(BenchmarkConfig):
    """Code evaluation (evalplus, humaneval, mbpp) configuration"""
    name: str = "code_eval"
    tasks: List[str] = field(default_factory=lambda: ["humaneval", "mbpp"])
    enable_thinking: bool = False
    test_timeout: int = 10


@dataclass
class ReasoningConfig(BenchmarkConfig):
    """Reasoning benchmarks (lm-eval) configuration"""
    name: str = "reasoning"
    tasks: List[str] = field(default_factory=lambda: [
        "winogrande", "arc_challenge", "arc_easy",
        "boolq", "hellaswag", "mmlu", "openbookqa", "rte"
    ])
    num_fewshot: int = 0
    batch_size: int = 4
    use_cache: bool = True


@dataclass
class MathConfig(BenchmarkConfig):
    """Math benchmarks configuration"""
    name: str = "math"
    datasets: List[str] = field(default_factory=lambda: ["gsm8k", "math_500"])
    eval_batch_size: int = 4


@dataclass
class EvaluationConfig:
    """Main evaluation configuration"""
    model: ModelConfig
    swebench: Optional[SWEBenchConfig] = None
    code_eval: Optional[CodeEvalConfig] = None
    reasoning: Optional[ReasoningConfig] = None
    math: Optional[MathConfig] = None

    output_dir: Path = Path("./outputs")
    save_predictions: bool = True
    generate_report: bool = True

    def get_enabled_benchmarks(self):
        """Get list of enabled benchmark configs"""
        enabled = []
        for bench in [self.swebench, self.code_eval, self.reasoning, self.math]:
            if bench and bench.enabled:
                enabled.append(bench)
        return enabled
