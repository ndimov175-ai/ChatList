# Installation Instructions

## Problem: ModuleNotFoundError: No module named 'PyQt6'

This means the dependencies are not installed. Follow these steps:

## Step 1: Install python3-venv (if needed)

If you get an error about `ensurepip` or `python3-venv`, install it:

```bash
sudo apt install python3.11-venv
```

## Step 2: Run the Setup Script

```bash
cd /home/niki/work/ChatList
./setup.sh
```

This will:
- Create a fresh virtual environment
- Install all required packages (PyQt6, httpx, etc.)

## Step 3: Run the Application

After setup completes, you can run the app in two ways:

**Option 1: Activate venv first**
```bash
source venv/bin/activate
python run.py
```

**Option 2: Use venv Python directly**
```bash
venv/bin/python run.py
```

## Manual Installation (Alternative)

If the script doesn't work, do it manually:

```bash
# 1. Install python3-venv (if needed)
sudo apt install python3.11-venv

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate it
source venv/bin/activate

# 4. Upgrade pip
pip install --upgrade pip

# 5. Install dependencies
pip install -r requirements.txt

# 6. Run the app
python run.py
```

## Verify Installation

Check if PyQt6 is installed:

```bash
venv/bin/python -c "import PyQt6; print('PyQt6 installed successfully!')"
```

If this prints "PyQt6 installed successfully!", you're ready to go!

## Troubleshooting

### "No module named pip" error
- Install python3-venv: `sudo apt install python3.11-venv`
- Recreate venv: `rm -rf venv && python3 -m venv venv`

### "externally-managed-environment" error
- Make sure you're using the venv's pip: `venv/bin/pip install ...`
- Or activate venv first: `source venv/bin/activate`

### Still having issues?
- Check that you're in the project directory: `pwd` should show `/home/niki/work/ChatList`
- Verify Python version: `python3 --version` should be 3.8 or higher
- Check logs: `cat logs/chatlist.log` (if it exists)

