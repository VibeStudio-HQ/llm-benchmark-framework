# LLM Model Evaluation

Documentation of evaluation methodology and scripts used to evaluate LLM models across multiple benchmarks.

## Overview

This repository contains scripts and configurations used to evaluate language models on various benchmarks including SWE-bench, EvalPlus, LiveCodeBench, and LM-Eval.

## Benchmarks Evaluated

- **SWE-bench**: Code patch generation for real GitHub issues
- **EvalPlus**: Extended code generation with additional test cases
- **LiveCodeBench**: Live coding challenge evaluation
- **LM-Eval**: General language model evaluation harness

## Repository Structure

```
.
├── benchmarks/          # Evaluation scripts for each benchmark
│   ├── swebench/       # SWE-bench evaluation scripts
│   ├── evalplus/       # EvalPlus evaluation
│   ├── livecodebench/  # LiveCodeBench evaluation
│   └── lm_eval/        # LM-Eval harness integration
├── configs/            # Configuration files
├── results/            # Evaluation results (JSONL format)
├── utils/              # Utility scripts (format conversion, etc.)
├── outputs/            # Raw model outputs
└── run_benchmarks.py   # Main evaluation runner
```

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Running SWE-bench

```bash
python benchmarks/run_swebench.py \
  --model_name "your-model-name" \
  --api_base "http://your-api-endpoint:8000/v1" \
  --run_swebench \
  --num_instances 10
```

### Configuration

Edit `configs/base_config.py` to customize:
- Model parameters (temperature, max_tokens)
- API endpoint
- Benchmark settings

## Evaluation Methodology

### SWE-bench

**Prompting Strategy**: Minimal prompt approach for cleaner patch generation

```python
prompt = f"""You are an expert software engineer. Fix the following GitHub issue by generating a code patch.

Repository: {instance['repo']}
Issue: {instance['problem_statement']}

Generate a git diff patch to fix this issue. Provide only the patch code."""
```

**Model Configuration**:
- Temperature: 0.0 (greedy decoding)
- Max tokens: 4096
- Stop tokens: None

**Evaluation**: Generated patches are evaluated using the official SWE-bench Docker evaluation harness

### Converting Results

Convert outputs to official SWE-bench format:

```bash
python utils/convert_to_swebench_format.py \
  --input outputs/swebench/predictions.jsonl \
  --output results/swebench_predictions.jsonl
```

## Results Format

All results are saved in JSONL format with the following structure:

```json
{
  "instance_id": "django__django-12345",
  "model_name_or_path": "your-model-name",
  "model_patch": "diff --git a/...",
  "problem_statement": "Issue description...",
  "repo": "django/django"
}
```

## Requirements

- Python 3.8+
- vLLM or OpenAI-compatible API endpoint
- SWE-bench dataset (auto-downloaded)
- Docker (for evaluation)

## License

MIT
