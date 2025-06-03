import os
import json 


script_dir = os.path.dirname(os.path.abspath(__file__))


# Add this entire function definition to your script
def load_examples(examples_file_path):
    full_examples_path = os.path.join(script_dir, examples_file_path)

    if not os.path.exists(full_examples_path):
        print(
            f"Info: Examples file '{full_examples_path}' not found. Starting with no examples."
        )
        return []

    try:
        with open(full_examples_path, "r", encoding="utf-8") as f:
            examples = json.load(f)
            if not isinstance(examples, list):
                print(
                    f"Warning: Examples file '{full_examples_path}' is not a list. Returning empty examples."
                )
                return []
            valid_examples = []
            for ex in examples:
                if all(
                    key in ex
                    for key in [
                        "user_context",
                        "git_diff",
                        "commit_messages",
                        "desired_pr_description",
                    ]
                ):
                    valid_examples.append(ex)
                else:
                    print(
                        f"Warning: Skipping malformed example in {examples_file_path}. Missing required keys."
                    )
            print(
                f"Loaded {len(valid_examples)} example(s) from '{examples_file_path}'."
            )
            
            # REDUCE EXAMPLES 
            if len(valid_examples) > 5 :
                return valid_examples[:5]
            return valid_examples
    except json.JSONDecodeError:
        print(
            f"Warning: Invalid JSON in examples file: '{full_examples_path}'. Returning empty examples."
        )
        return []
    except Exception as e:
        print(
            f"Warning: Could not load examples file '{full_examples_path}': {e}. Returning empty examples."
        )
        return []


# Add this entire function definition to your script
def save_example(new_example, examples_file_path):
    full_examples_path = os.path.join(script_dir, examples_file_path)

    existing_examples = []
    if os.path.exists(full_examples_path):
        try:
            with open(full_examples_path, "r", encoding="utf-8") as f:
                existing_examples = json.load(f)
                if not isinstance(existing_examples, list):
                    existing_examples = []
        except json.JSONDecodeError:
            print(
                f"Warning: Existing examples file '{full_examples_path}' is corrupted. Starting fresh."
            )
            existing_examples = []
        except Exception as e:
            print(
                f"Warning: Could not read existing examples file '{full_examples_path}': {e}. Starting fresh."
            )
            existing_examples = []

    existing_examples.append(new_example)

    try:
        with open(full_examples_path, "w", encoding="utf-8") as f:
            json.dump(existing_examples, f, indent=4)
        print(
            f"Example saved to '{full_examples_path}'. Remember to manually refine it if needed!"
        )
    except Exception as e:
        print(f"Error saving example to '{full_examples_path}': {e}")
