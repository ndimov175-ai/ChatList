# Quick Start Guide

## Step 1: Activate Virtual Environment

If you haven't already activated your virtual environment:

```bash
source venv/bin/activate
# On Windows: venv\Scripts\activate
```

## Step 2: Install Dependencies (if not already done)

```bash
pip install -r requirements.txt
```

## Step 3: Create .env File (Optional but Recommended)

Create a `.env` file in the project root with your API keys:

```bash
# API Keys (at least one is needed to test with real models)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Optional settings
DATABASE_PATH=chatlist.db
LOG_LEVEL=INFO
MAX_CONCURRENT_REQUESTS=5
REQUEST_TIMEOUT=30
```

**Note:** You can run the application without API keys, but models without keys will be disabled (grayed out).

## Step 4: Run the Application

You have two options:

### Option 1: Using the launcher script
```bash
python run.py
```

### Option 2: Using Python module
```bash
python -m chatlist.app
```

## What to Expect

1. **First Launch:**
   - The application will automatically create the database (`chatlist.db`)
   - Default models will be added (OpenAI GPT-4, GPT-3.5, Claude 3, Google Gemini)
   - Models without API keys will be disabled (grayed out)

2. **Main Window:**
   - **Left Panel:**
     - Prompt input area (top)
     - Model selection with checkboxes (bottom)
   - **Right Panel:**
     - Results table showing responses

3. **Testing Without API Keys:**
   - You can explore the interface
   - Models will be visible but disabled
   - You can add/edit models via Tools → Manage Models
   - You can test the UI without making actual API calls

4. **Testing With API Keys:**
   - Select one or more models
   - Enter a prompt
   - Click "Send Request" or press Ctrl+Return
   - Watch results appear in the table

## Troubleshooting

### Application won't start
- Make sure PyQt6 is installed: `pip install PyQt6`
- Check that you're in the virtual environment
- Check logs in `logs/chatlist.log`

### No models visible
- The database should auto-initialize on first run
- Check Tools → Manage Models to see/add models
- Models without API keys will be grayed out but still visible

### Import errors
- Make sure you're running from the project root directory
- Verify all dependencies are installed: `pip install -r requirements.txt`

## Keyboard Shortcuts

- `Ctrl+Return` - Send request
- `Ctrl+C` - Cancel request
- `Ctrl+N` - New (clear prompt and results)
- `Ctrl+Q` - Quit

## Next Steps

1. Add your API keys to `.env` file
2. Select models you want to test
3. Enter a prompt and send it
4. Compare responses in the results table
5. Save prompts and results for later

Enjoy testing ChatList!

