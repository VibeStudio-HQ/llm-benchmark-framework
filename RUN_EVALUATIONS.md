# How to Run Evaluations

Temperature is set to **1.0** in `configs/base_config.py` for sampling diversity.

## 1. Run SWE-bench First (10 instances)

```bash
python run_swebench_eval.py \
  --model_name "your-model-name" \
  --api_url "http://your-api-endpoint:8000/v1" \
  --num_instances 10 \
  --temperature 1.0
```

**Example with actual endpoint:**
```bash
python run_swebench_eval.py \
  --model_name "VibeStudio/MiniMax-M2-THRIFT-55-v1" \
  --api_url "http://your-server-ip:8000/v1" \
  --num_instances 10 \
  --temperature 1.0
```

### Output

Results will be saved to:
- `outputs/swebench/predictions.jsonl` - Generated patches
- `outputs/swebench/summary.json` - Execution summary

### Convert to SWE-bench Format

```bash
python utils/convert_to_swebench_format.py \
  --input outputs/swebench/predictions.jsonl \
  --output results/swebench_predictions.jsonl
```

### Run Docker Evaluation

To evaluate the generated patches:

```bash
# Clone SWE-bench evaluation harness
git clone https://github.com/princeton-nlp/SWE-bench.git
cd SWE-bench

# Run evaluation
python -m swebench.harness.run_evaluation \
  --predictions_path ../llm-benchmark-framework/results/swebench_predictions.jsonl \
  --max_workers 4 \
  --run_id my_evaluation
```

---

## 2. Run Other Evaluations

### EvalPlus (Code Generation)

```bash
# Install EvalPlus
pip install evalplus

# Run evaluation
evalplus.evaluate \
  --model "your-model-name" \
  --dataset humaneval \
  --backend vllm \
  --base_url "http://your-api-endpoint:8000/v1"
```

### LiveCodeBench

```bash
# Clone LiveCodeBench
git clone https://github.com/LiveCodeBench/LiveCodeBench.git
cd LiveCodeBench

# Install dependencies
pip install -e .

# Run evaluation
python -m livecodebench.evaluate \
  --model your-model-name \
  --api_base http://your-api-endpoint:8000/v1
```

### LM-Eval Harness

```bash
# Install lm-eval
pip install lm-eval

# Run evaluation
lm_eval --model vllm \
  --model_args pretrained=your-model-name,tensor_parallel_size=1,dtype=auto,gpu_memory_utilization=0.8,base_url=http://your-api-endpoint:8000/v1 \
  --tasks mmlu,hellaswag,arc_challenge,truthfulqa \
  --batch_size 8 \
  --output_path results/lm_eval/
```

### Math Benchmarks (GSM8K)

```bash
# Using lm-eval for math benchmarks
lm_eval --model vllm \
  --model_args pretrained=your-model-name,base_url=http://your-api-endpoint:8000/v1 \
  --tasks gsm8k,math_qa \
  --batch_size 8 \
  --output_path results/math/
```

---

## All Benchmarks Summary

| Benchmark | Command | Output Location |
|-----------|---------|-----------------|
| SWE-bench | `python run_swebench_eval.py` | `outputs/swebench/` |
| EvalPlus | `evalplus.evaluate` | `evalplus_results/` |
| LiveCodeBench | `python -m livecodebench.evaluate` | `livecodebench_results/` |
| LM-Eval | `lm_eval --tasks mmlu,hellaswag,...` | `results/lm_eval/` |
| Math | `lm_eval --tasks gsm8k,math_qa` | `results/math/` |

---

## Configuration

Edit `configs/base_config.py` to change default settings:

```python
@dataclass
class ModelConfig:
    temperature: float = 1.0  # Sampling temperature
    max_tokens: int = 4096    # Max tokens per response
    top_p: float = 1.0        # Nucleus sampling
    timeout: int = 180        # API timeout in seconds
```

---

## Notes

- **Temperature 1.0**: Enables diverse, creative outputs (vs 0.0 for deterministic)
- **SWE-bench**: Run evaluation first with 10 instances to verify setup
- **Docker Evaluation**: Required for accurate SWE-bench pass@1 metrics
- **API Compatibility**: All benchmarks expect OpenAI-compatible API format
