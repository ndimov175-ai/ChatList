#!/home/stefan/work/ChatList/.venv/bin/python3
"""
Simple launcher script for ChatList application.
"""
import sys
import os

# Set Qt platform for headless servers BEFORE any other imports
# Only use offscreen if there's no DISPLAY environment variable
if not os.environ.get('DISPLAY') and not os.environ.get('QT_QPA_PLATFORM'):
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from chatlist.app import main

if __name__ == '__main__':
    sys.exit(main())

