# ChatList

AI Model Comparison Tool - Compare responses from multiple AI models simultaneously.

## Features

- Send the same prompt to multiple AI models at once
- Compare responses side-by-side in a table
- Save prompts and results to database
- Support for OpenAI GPT, Anthropic Claude, Google Gemini, and OpenRouter (unified API)
- Async concurrent requests for fast responses

## Installation

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file (copy from `.env.example` if available):
```bash
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional settings
DATABASE_PATH=chatlist.db
LOG_LEVEL=INFO
MAX_CONCURRENT_REQUESTS=5
REQUEST_TIMEOUT=30
```

## Usage

Run the application:
```bash
python run.py
# or
python -m chatlist.app
```

## Application Structure

- **Prompt Input**: Enter your prompt or load a saved one
- **Model Selection**: Select which models to query (checkboxes)
- **Results Table**: View responses with model name, response text, time, and tokens
- **Save Results**: Save prompts and results to the database

## Development Status

- ✅ Stage 1: Project setup and configuration
- ✅ Stage 2: Database implementation
- ✅ Stage 3: API clients for neural networks (including OpenRouter)
- ✅ Stage 4: Graphical interface (PyQt6)
- ✅ Stage 5: Integration and testing
- ⏳ Stage 6: Testing and refinement
- ✅ Stage 7: Finalization (pyproject.toml, progress bar, .env.example)

## License

See LICENSE file for details.
