<img width="481" alt="изображение" src="https://github.com/IlyaGusev/quest/assets/2670295/ca6a33ee-f17e-4424-b305-22544911d2c4">

![изображение](https://github.com/IlyaGusev/quest/assets/2670295/fa60f869-279a-4d09-a831-e34d7690b2f6)

# Quest: Evaluating Sampling Strategies for LLMs

## Table of Contents

- [Setup](#setup)
- [Generating New Completions](#generating-new-completions)
- [Converting to AlpacaEval Format](#converting-to-alpacaeval-format)
- [Running the Leaderboard Evaluation](#running-the-leaderboard-evaluation)
- [Viewing Results](#viewing-results)

## Setup

1. Ensure you have Python 3.8+ installed
2. Create and activate a virtual environment:

```bash
python -m venv venv
# On Windows
.\venv\Scripts\Activate.ps1
# On Linux/Mac
source venv/bin/activate
```

3. Install the required packages:

```bash
pip install -e .
pip install alpaca_eval
```

4. Set up your OpenAI API key in a `.env` file:

```
OPENAI_API_KEY=your_api_key_here
```

## Generating New Completions

To generate new completions with different sampling strategies:

1. Prepare your prompts in a JSONL file with the following format:

```json
{"prompt": "Write a short story about...", "source": "creative_writing"}
```

2. Use the generation script with your desired sampling parameters:

```bash
python generate_completions.py \
    --model "openchat-3.5-0106" \
    --temperature 1.5 \
    --min_p 0.1 \
    --input_file "data/prompts.jsonl" \
    --output_file "data/outputs/7b_temp150_minp_10.jsonl"
```

Available sampling parameters:
- `--temperature`: Controls randomness (e.g., 0.8, 1.0, 1.5)
- `--min_p`: Minimum probability threshold (e.g., 0.02, 0.05, 0.1)
- `--top_p`: Nucleus sampling threshold (e.g., 0.9, 0.95, 0.98)
- `--tfs`: Tail-free sampling threshold

The output file will be saved in JSONL format with the model outputs.

## Converting to AlpacaEval Format

After generating completions, you need to convert them to the AlpacaEval format:

1. For individual files:

```bash
python -m quest.to_alpaca_eval \
    --input_path "data/outputs/7b_temp150_minp_10.jsonl" \
    --output_path "data/outputs/aeval_7b_temp150_minp_10.json"
```

2. For multiple files, you can use the conversion script:

```bash
python convert_all.py
```

This will:
- Convert all specified JSONL files to the AlpacaEval JSON format
- Create a combined file (`aeval_all.json`) with all model outputs

## Running the Leaderboard Evaluation

To evaluate the model outputs and create a leaderboard:

```bash
python -m alpaca_eval.main make_leaderboard \
    --all_model_outputs data/outputs/aeval_all.json \
    --reference_outputs data/outputs/aeval_7b_temp100.json \
    --annotators_config alpaca_eval_cot_gpt4_turbo_fn \
    --leaderboard-path leaderboard.csv
```

This command:
- Takes all model outputs from `aeval_all.json`
- Uses outputs from `aeval_7b_temp100.json` as the reference
- Uses GPT-4 Turbo with chain-of-thought prompting for evaluation
- Saves the results to `leaderboard.csv`

Alternatively, you can use the provided shell script:

```bash
# On Linux/Mac
./eval.sh
# On Windows PowerShell
python -m alpaca_eval.main make_leaderboard --all_model_outputs data/outputs/aeval_all.json --reference_outputs data/outputs/aeval_7b_temp100.json --annotators_config alpaca_eval_cot_gpt4_turbo_fn --leaderboard-path leaderboard.csv
```

## Viewing Results

To view the results in a more readable format:

```bash
python display_results.py
```

This will display a sorted table of results with:
- Model configuration
- Win rate
- Length-controlled win rate
- Average output length

## Example Results

| Model                      | Win Rate | LC Win Rate | Avg Length |
|----------------------------|----------|-------------|------------|
| temp150_minp_10            | 56.54%   | 58.12%      | 1852       |
| temp150_minp_15            | 53.37%   | 56.73%      | 1816       |
| temp100_minp_05            | 52.01%   | 55.07%      | 1808       |
| temp80_topp_98             | 51.29%   | 54.65%      | 1810       |
| temp100_minp_10            | 50.14%   | 53.24%      | 1793       |
| temp100_topp_98            | 50.43%   | 53.00%      | 1834       |
| temp150_minp_05            | 48.57%   | 48.13%      | 1919       |
| temp150_topp_90            | 44.83%   | 42.09%      | 2149       |
