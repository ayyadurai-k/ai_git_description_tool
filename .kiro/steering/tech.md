# Technology Stack

## Core Technologies
- **Python 3.x** - Main programming language
- **Google Generative AI (Gemini)** - AI model for content generation
- **Git** - Version control integration for diff and commit analysis

## Dependencies
- `google-generativeai` - Google's Gemini API client
- `python-dotenv` - Environment variable management

## Environment Setup
- Requires `GOOGLE_API_KEY` in `.env` file for Gemini API access
- Uses virtual environment (recommended via `env/` folder)

## Common Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run the PR description generator
python generate_description.py

# Set up environment variables
# Create .env file with GOOGLE_API_KEY=your_api_key_here
```

## Architecture Notes
- Modular design with separate `examples.py` for example management
- JSON-based example storage system for AI learning
- Git subprocess integration for repository analysis
- Error handling for missing files and API failures