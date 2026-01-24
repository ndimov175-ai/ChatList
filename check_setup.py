#!/usr/bin/env python3
"""
Quick setup verification script.
Checks if all dependencies are installed and ready.
"""
import sys

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Found: {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if required packages are installed."""
    required = {
        'PyQt6': 'PyQt6',
        'httpx': 'httpx',
        'requests': 'requests',
        'dotenv': 'python-dotenv',
    }
    
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} NOT installed")
            missing.append(package)
    
    return len(missing) == 0

def check_project_structure():
    """Check if project structure is correct."""
    import os
    from pathlib import Path
    
    required_files = [
        'chatlist/__init__.py',
        'chatlist/app.py',
        'chatlist/config/settings.py',
        'chatlist/db/database_manager.py',
        'chatlist/ui/main_window.py',
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all checks."""
    print("=" * 50)
    print("ChatList Setup Verification")
    print("=" * 50)
    print()
    
    all_ok = True
    
    print("1. Checking Python version...")
    if not check_python_version():
        all_ok = False
    print()
    
    print("2. Checking dependencies...")
    if not check_dependencies():
        all_ok = False
        print("\n💡 Install missing packages with: pip install -r requirements.txt")
    print()
    
    print("3. Checking project structure...")
    if not check_project_structure():
        all_ok = False
    print()
    
    print("=" * 50)
    if all_ok:
        print("✅ All checks passed! You can run the application with:")
        print("   python run.py")
        print("   or")
        print("   python -m chatlist.app")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
    print("=" * 50)
    
    return 0 if all_ok else 1

if __name__ == '__main__':
    sys.exit(main())

