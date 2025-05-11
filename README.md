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

## Troubleshooting

### OpenAI API Compatibility Issues

If you encounter errors related to the OpenAI API when running AlpacaEval, you may need to fix compatibility issues between the AlpacaEval code and newer versions of the OpenAI API:

1. **Schema Validation Error**: With OpenAI API version 1.65.3+, you might see this error:
   ```
   openai.BadRequestError: Error code: 400 - {'error': {'message': "Invalid schema for function 'make_partial_leaderboard': In context=(), 'required' is required to be supplied and to be an array including every key in properties. Missing 'concise_explanation'."}}
   ```

2. **Fix for Schema Validation Error**:
   - Edit the AlpacaEval config files to add the missing field to the required array:
   - Modify `venv/Lib/site-packages/alpaca_eval/evaluators_configs/alpaca_eval_cot_gpt4_turbo_fn/configs.yaml`:
     ```yaml
     # Change this line:
     required: [ "ordered_models" ]
     # To:
     required: [ "ordered_models", "concise_explanation" ]
     ```
   - Also modify `venv/Lib/site-packages/alpaca_eval/evaluators_configs/alpaca_eval_gpt4_turbo_fn/configs.yaml` in the same way.

3. **PowerShell Command Syntax**: When running commands in PowerShell, use semicolons (`;`) instead of `&&` to chain commands:
   ```powershell
   # Incorrect:
   cd quest && python -m alpaca_eval.main make_leaderboard ...
   
   # Correct:
   cd quest; python -m alpaca_eval.main make_leaderboard ...
   ```

4. **Leaderboard Display Error**: You might encounter an error with the `print_leaderboard()` function:
   ```
   TypeError: print_leaderboard() got an unexpected keyword argument 'leaderboard_mode'
   ```
   This is just a display issue and doesn't affect the evaluation results. The leaderboard.csv file will still be created correctly.

5. **Checking Results**: If the evaluation completes but you're not sure if it worked, check for the existence of the leaderboard file:
   ```powershell
   dir leaderboard.csv
   ```

## Latest Example AlpacaEval Results (sorted by Length-Controlled Win Rate)

| Model                          | Win Rate | LC Win Rate | Avg Length |
|--------------------------------|----------|-------------|------------|
| `temp150_minp_10`              | **56.54%**   | **58.12%**  | 1852       |
| `temp150_minp_15`              | 53.37%   | 56.73%      | 1816       |
| `temp150_minp_20`              | 53.38%   | 55.45%      | 1835       |
| `quad_20_100`                  | 52.80%   | 55.43%      | 1821       |
| `temp100_minp_05`              | 52.01%   | 55.07%      | 1808       |
| `temp200_minp_20`              | 53.08%   | 54.82%      | 1861       |
| `temp80_topp_98`               | 51.29%   | 54.65%      | 1810       |
| `dynatemp_50_150_75_minp_05`   | 51.58%   | 54.42%      | 1807       |
| `dynatemp_50_200_100_minp_10`  | 51.87%   | 54.33%      | 1825       |
| `temp150_minp_10_seed1337`     | 52.86%   | 53.84%      | 1856       |
| `temp170_minp_15`              | 52.65%   | 53.75%      | 1855       |
| `temp120_minp_10`              | 51.36%   | 53.75%      | 1829       |
| `quad_15_100`                  | 51.65%   | 53.70%      | 1843       |
| `tfs_95`                       | 50.79%   | 53.49%      | 1802       |
| `tfs_98`                       | 50.72%   | 53.39%      | 1807       |
| `temp100_minp_10`              | 50.14%   | 53.24%      | 1793       |
| `temp100_topp_98`              | 50.43%   | 53.00%      | 1834       |
| `temp100_topp_90`              | 50.07%   | 52.57%      | 1815       |
| `temp80`                       | 49.28%   | 52.40%      | 1797       |
| `temp100_topp_95`              | 50.22%   | 51.80%      | 1835       |
| `temp100_minp_02`              | 50.43%   | 51.62%      | 1853       |
| `temp80_minp_02`               | 48.85%   | 51.46%      | 1802       |
| `temp80_minp_05`               | 47.84%   | 50.99%      | 1808       |
| `temp80_topp_95`               | 48.78%   | 50.76%      | 1793       |
| `temp100`                      | 50.00%   | 50.00%      | 1902       |
| `dynatemp_100_250_100_minp_10` | 50.86%   | 50.00%      | 2227       |
| `quad_25_100`                  | 47.85%   | 49.94%      | 1807       |
| `temp150_tfs_95`               | 51.08%   | 49.94%      | 1969       |
| `greedy`                       | 46.64%   | 49.90%      | 1765       |
| `temp150_minp_05`              | 48.57%   | 48.13%      | 1919       |
| `temp150_topp_80`              | 20.00%   | 43.05%      | 3576       |
| `temp150_minp_02`              | 44.83%   | 42.09%      | 2149       |
| `dynatemp_50_150_100`          | 35.37%   | 34.94%      | 2764       |
| `mirostat_40_10`               | 16.69%   | 16.04%      | 1848       |
| `mirostat_50_10`               | 16.40%   | 16.04%      | 1822       |
| `mirostat_60_10`               | 15.62%   | 14.97%      | 1838       |
| `temp150_topp_98`              | 0.00%    | 0.02%       | 4136       |
| `temp150_topp_95`              | 0.00%    | 0.00%       | 4943       |
| `temp150_topp_90`              | 0.00%    | 0.00%       | 9204       |

Evaluations were performed using GPT-4 Turbo with chain-of-thought prompting on outputs from the openchat-3.5-0106 model.