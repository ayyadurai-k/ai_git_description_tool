import os
import subprocess
import google.generativeai as genai
from dotenv import load_dotenv

from examples import load_examples, save_example

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
EXAMPLES_FILE = "examples.json"  # File to store examples


if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file.")
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the generative model
# You can choose other models like 'gemini-1.5-flash', 'gemini-1.5-pro' for more advanced tasks
model = genai.GenerativeModel("gemini-2.0-flash")


def get_git_diff(base_branch="main"):
    """
    Gets the cumulative diff between the base branch and the current branch.
    Assumes the script is run from within the Git repository.
    """
    try:
        current_branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

        if current_branch == base_branch:
            print(
                f"Warning: You are on the '{base_branch}' branch. Generating diff against itself might not be meaningful."
            )
            # If on main, compare against the last commit for a diff (or handle as error)
            # For this scenario, we'll return an empty diff as no feature branch changes exist
            return ""

        # Get the diff between the common ancestor of base_branch and current_branch,
        # and the current branch tip. This shows what's unique to current_branch.
        diff_command = ["git", "diff", f"{base_branch}...{current_branch}"]
        result = subprocess.run(
            diff_command, capture_output=True, text=True, errors="ignore", check=True
        )
        return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")
        print(f"Stderr: {e.stderr}")
        return ""
    except Exception as e:
        print(f"An error occurred while getting git diff: {e}")
        return ""


def get_git_commit_messages(base_branch="main"):
    """
    Gets the commit messages from the current branch that are not in the base branch.
    """
    try:
        current_branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

        if current_branch == base_branch:
            return ""  # No unique commits if on the base branch

        # --no-merges: exclude merge commits to keep the history clean
        log_command = [
            "git",
            "log",
            f"{base_branch}..{current_branch}",
            "--oneline",
            "--no-merges",
        ]
        result = subprocess.run(log_command, capture_output=True, text=True, check=True)
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        print(f"Git log command failed: {e}")
        print(f"Stderr: {e.stderr}")
        return ""
    except Exception as e:
        print(f"An error occurred while getting commit messages: {e}")
        return ""


def generate_description(
    user_context, diff_content, commit_history, examples=None
):  # user_context now handles all input
    """
    Sends user context, diff, and commit history to the Gemini model
    to generate a structured PR description, inferring type and distributing content.
    """
    if not diff_content and not commit_history:
        return "No changes or new commits found in the current branch compared to main. Cannot generate a meaningful description."

    prompt_parts = []

    # Add this entire `if examples:` block right after `prompt_parts = []`
    if examples:
        for i, example in enumerate(examples):
            prompt_parts.extend(
                [
                    f"--- Example {i+1}: Input Context ---",
                    f"User Provided Context: {example['user_context']}",
                    f"Git Diff: ```diff\n{example['git_diff']}\n```",
                    f"Unique Commit Messages: ```\n{example['commit_messages']}\n```",
                    "",
                    f"--- Example {i+1}: Desired Output PR Description ---",
                    example["desired_pr_description"],
                    "",
                ]
            )
        prompt_parts.append("--- End Examples ---")
        prompt_parts.append("")

    desc_prompt_parts = [
        "You are an expert software engineer and a technical writer whose job is to generate "
        "high-quality Pull Request descriptions. "
        "Generate a PR description that follows the provided best practices. "
        "Crucially, **DO NOT include any code lines or code snippets in the 'Changes Made' section.** "
        "Describe changes in natural language, referring to affected components or files.",
        "Your goal is to intelligently infer the PR's type (e.g., 'Feat', 'Fix', 'Refactor', 'Chore', 'Docs') "
        "and distribute information from the 'User Provided Context' into the appropriate sections, "
        "while also generating content based on the Git Diff and Commit Messages.",
        "",
        "--- User Provided Context (Problem, Feature, Notes, Preliminary Testing) ---",
        (
            user_context if user_context else "No specific user context provided."
        ),  # Include all user input here
        "",
        "--- Git Diff (for technical changes analysis) ---",
        "```diff",
        diff_content if diff_content else "No substantial code changes detected.",
        "```",
        "",
        "--- Unique Commit Messages in this branch ---",
        "```",
        commit_history if commit_history else "No unique commit messages found.",
        "```",
        "",
        "--- Desired PR Description Format (Fill based on all context) ---",
        "Provide the description using the following markdown structure:",
        "",
        "## [Infer Type]: [Clear and Concise Title]",
        "   - Infer the PR type (e.g., 'feat', 'fix', 'refactor', 'chore', 'docs') from the Git diff, commit messages, and user context. ",
        "   - Create a concise title that summarizes the core change.",
        "",
        '### Problem/Motivation',
        "   - Explain why these changes are being made. "
        "   - Prioritize information from the 'User Provided Context' for this section if applicable. "
        "   - Supplement with inferences from Git Diff and Commit Messages if the user context is brief or broad.",
        "",
        '### Changes Made',
        "   - Provide a high-level overview of the technical changes. "
        "   - Mention key files or areas affected. "
        "   - **DO NOT include any code lines or snippets. Describe in natural language only.**"
        "   - Integrate any relevant 'Changes Made' details found in the 'User Provided Context'.",
        "",
        '### Testing Instruction',
        "   - **Extract any specific, actionable testing instructions or preliminary notes from the 'User Provided Context'(If not provided ignore user context) and based on git diff and commit history and present them here.**"
        "",
        "### Screenshots/Gifs/Videos (For UI Changes)",
        "   - **If the 'User Provided Context' explicitly mentions or links to screenshots/gifs/videos, include a placeholder here.**"
        "   - If no visual aids are mentioned, use the following placeholder:"
        "     `*(If applicable, please embed visual aids here, showing before-and-after if relevant.)*`",
        "",
    ]

    prompt_parts.extend(desc_prompt_parts)

    try:
        response = model.generate_content(prompt_parts)
        return response.text
    except Exception as e:
        print(f"Error generating content from Gemini: {e}")
        return "Failed to generate description from AI."


if __name__ == "__main__":
    # Ensure the script is run from inside a Git repository
    if not os.path.exists(".git"):
        print("Error: This script must be run from within a Git repository.")
        exit(1)

    loaded_examples = load_examples(EXAMPLES_FILE)

    print("\n--- PR Description Generator ---")
    print("This tool will help you create a structured Pull Request description.")

    # Get a single, comprehensive user input
    user_context_input = input(  # User provides a single block of context
        "\nPlease provide any relevant context, notes, or preliminary testing instructions for this PR. "
        "This can include the problem solved, feature added, or any specific details for reviewers:\n> "
    ).strip()

    if (
        not user_context_input
    ):  # Allow empty input if user just wants AI to infer everything
        print(
            "\nNo specific user context provided. AI will rely on Git diff and commit messages."
        )

    print("\nFetching Git diff and commit history...")
    diff = get_git_diff()
    commits = get_git_commit_messages()

    if not diff and not commits:
        print(
            "No significant changes or unique commits found in the current branch compared to 'main'."
        )
        print(
            "Please ensure you are on a feature branch with unmerged changes, or run `git pull origin main` first."
        )
    else:
        print("\nGenerating AI description (this may take a moment)...")
        # Pass the single user context to the generation function
        description = generate_description(
            user_context_input, diff, commits, examples=loaded_examples
        )
        print("\n--- AI Generated Pull Request Description ---")
        print(description)
        print("---------------------------------------------")
        print(
            "\n(IMPORTANT: Please review and refine this description as needed. "
            "The AI attempts to integrate your notes, but always verify accuracy!)"
        )

        save_choice = (
            input(
                "\nDo you want to save this interaction as a new example for future AI learning? (y/N): "
            )
            .strip()
            .lower()
        )

        if save_choice == "y":
            new_example = {
                "user_context": user_context_input,
                "git_diff": diff,
                "commit_messages": commits,
                "desired_pr_description": description,  # Save the AI's current output
            }
            save_example(new_example, EXAMPLES_FILE)
            print(
                "Example saved. Remember to manually edit 'examples.json' if you refine the description further!"
            )
