# Project Structure

## Root Directory Layout
```
├── .env                    # Environment variables (API keys)
├── .gitignore             # Git ignore patterns
├── requirements.txt       # Python dependencies
├── __init__.py           # Empty package marker
├── generate_description.py # Main application entry point
├── examples.py           # Example management utilities
├── examples.json         # AI training examples (gitignored)
├── env/                  # Virtual environment (recommended)
└── __pycache__/          # Python bytecode cache
```

## File Responsibilities

### Core Application Files
- **`generate_description.py`** - Main script containing Git integration, AI prompting, and user interaction logic
- **`examples.py`** - Utility functions for loading and saving example data for AI training

### Configuration Files
- **`.env`** - Contains sensitive API keys (never commit to version control)
- **`requirements.txt`** - Python package dependencies
- **`.gitignore`** - Excludes sensitive files, cache directories, and generated content

### Generated/Runtime Files
- **`examples.json`** - Stores user-approved examples for AI learning (gitignored)
- **`__pycache__/`** - Python bytecode cache (gitignored)

## Coding Conventions
- Use descriptive function names and comprehensive error handling
- Include docstrings for all functions explaining parameters and return values
- Separate concerns: Git operations, AI interaction, and file I/O in distinct functions
- Validate user input and provide helpful error messages
- Use UTF-8 encoding for all file operations