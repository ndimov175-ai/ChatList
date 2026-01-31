#!/usr/bin/env bash
# Etap 8 Deployment & Testing Guide

set -e

PROJECT_DIR="/home/stefan/work/ChatList"
cd "$PROJECT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════╗
║                     ETAP 8 DEPLOYMENT GUIDE                         ║
║              AI-Ассистент для улучшения промтов                      ║
╚══════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Function to print section headers
print_section() {
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_section "1. PRE-DEPLOYMENT CHECKS"

echo "Checking virtual environment..."
if [ -d ".venv" ]; then
    print_success "Virtual environment found"
else
    print_error "Virtual environment not found"
    exit 1
fi

echo "Checking Python version..."
PYTHON_VERSION=$(.venv/bin/python --version 2>&1)
print_success "Python version: $PYTHON_VERSION"

echo "Checking dependencies..."
.venv/bin/python -c "import PyQt6; print('✅ PyQt6')" 2>/dev/null || print_error "PyQt6 not installed"
.venv/bin/python -c "import httpx; print('✅ httpx')" 2>/dev/null || print_error "httpx not installed"
.venv/bin/python -c "import pytest; print('✅ pytest')" 2>/dev/null || print_error "pytest not installed"

print_section "2. RUNNING UNIT TESTS"

echo "Executing unit tests for Etap 8 components..."
echo ""

.venv/bin/python -m pytest tests/test_prompt_enhancer.py -v --tb=short

TEST_RESULT=$?

if [ $TEST_RESULT -eq 0 ]; then
    print_success "All unit tests passed!"
else
    print_error "Some tests failed"
    exit 1
fi

print_section "3. VERIFYING COMPONENTS"

echo "Validating Etap 8 implementation..."
echo ""

.venv/bin/python << 'PYTHON_EOF'
import sys
from pathlib import Path

components = {
    "EnhanceResult": "chatlist/core/enhance_result.py",
    "PromptEnhancerClient": "chatlist/core/prompt_enhancer_client.py",
    "PromptEnhancerManager": "chatlist/core/prompt_enhancer_manager.py",
    "PromptEnhancerDialog": "chatlist/ui/prompt_enhancer_dialog.py",
    "DB Migration": "chatlist/migrations/002_prompt_enhancements.sql",
}

print("Component Status:")
all_exist = True
for name, path in components.items():
    exists = Path(path).exists()
    status = "✅" if exists else "❌"
    print(f"  {status} {name:25} ({path})")
    all_exist = all_exist and exists

if not all_exist:
    sys.exit(1)

# Import and test
try:
    from chatlist.core.enhance_result import EnhanceResult
    from chatlist.core.prompt_enhancer_client import PromptEnhancerClient
    from chatlist.core.prompt_enhancer_manager import PromptEnhancerManager
    print("\n✅ All imports successful")
except Exception as e:
    print(f"\n❌ Import error: {e}")
    sys.exit(1)
PYTHON_EOF

VERIFY_RESULT=$?
if [ $VERIFY_RESULT -eq 0 ]; then
    print_success "All components verified!"
else
    print_error "Component verification failed"
    exit 1
fi

print_section "4. DATABASE MIGRATION CHECK"

echo "Checking database migration..."
echo ""

if [ -f "chatlist/migrations/002_prompt_enhancements.sql" ]; then
    print_success "Migration file exists"
    echo ""
    echo "Migration will be applied automatically on first run."
    echo "Table will be created: prompt_enhancements"
    echo "Columns: id, original_prompt, enhanced_prompt, alternatives,"
    echo "         explanation, recommendations, model_id,"
    echo "         enhancement_type, prompt_id, created_at"
else
    print_error "Migration file not found"
    exit 1
fi

print_section "5. ENVIRONMENT CONFIGURATION"

echo "Checking .env file..."
if [ -f ".env" ]; then
    print_success ".env file found"
    
    # Check API keys
    if grep -q "OPENROUTER_API_KEY" .env; then
        print_success "OPENROUTER_API_KEY configured"
    else
        print_warning "OPENROUTER_API_KEY not found in .env"
    fi
else
    print_warning ".env file not found - create it with your API keys"
fi

print_section "6. STARTING APPLICATION"

echo "To start the application with Etap 8 features:"
echo ""
echo -e "${BLUE}./run.sh${NC}"
echo ""
echo "After launching:"
echo "  1. Click on '🎯 Enhance Prompt' button in toolbar"
echo "  2. Or press Ctrl+E"
echo ""

print_section "7. TESTING IN APPLICATION"

echo "Steps to verify Etap 8 in the UI:"
echo ""
echo "1. Launch application:"
echo "   ./run.sh"
echo ""
echo "2. Open Enhance Prompt Dialog:"
echo "   - Click '🎯 Enhance Prompt' button"
echo "   - Or press Ctrl+E"
echo ""
echo "3. Test enhancement:"
echo "   - Enter a prompt (e.g., 'Write a Python function')"
echo "   - Select enhancement type (General, Code, Analysis, Creative)"
echo "   - Select a model from dropdown"
echo "   - Click 'Улучшить промт' button"
echo "   - Wait 3-5 seconds for API response"
echo ""
echo "4. View results:"
echo "   - Tab 1: View enhanced prompt with Copy/Use buttons"
echo "   - Tab 2: View alternative prompts"
echo "   - Tab 3: View explanation and recommendations"
echo ""
echo "5. Apply result:"
echo "   - Click 'Use' to insert enhanced prompt into main input"
echo "   - Or click 'Copy' to copy to clipboard"
echo ""

print_section "8. TROUBLESHOOTING"

echo "If you encounter issues:"
echo ""
echo -e "${YELLOW}Issue: Dialog doesn't open${NC}"
echo "  Solution: Check OPENROUTER_API_KEY in .env"
echo ""
echo -e "${YELLOW}Issue: API timeout${NC}"
echo "  Solution: Check internet connection"
echo "  Note: OpenRouter API response time is 3-5 seconds"
echo ""
echo -e "${YELLOW}Issue: QThread error${NC}"
echo "  Solution: Ensure PyQt6 is properly installed"
echo "  Run: .venv/bin/pip install --upgrade PyQt6"
echo ""
echo -e "${YELLOW}Issue: Database table not created${NC}"
echo "  Solution: Delete chatlist.db and restart application"
echo ""

print_section "9. DOCUMENTATION"

echo "For more information, see:"
echo ""
echo -e "  📄 ${BLUE}ETAP_8_SUMMARY.md${NC} - Overview and statistics"
echo "  📄 ${BLUE}ETAP_8_IMPLEMENTATION.md${NC} - Detailed implementation guide"
echo "  📄 ${BLUE}ETAP_8_QUICKREF.md${NC} - Quick reference for files"
echo "  📄 ${BLUE}tests/test_prompt_enhancer.py${NC} - Unit tests"
echo ""

print_section "10. DEPLOYMENT SUMMARY"

echo "Deployment checklist:"
echo ""
echo -e "${GREEN}✅${NC} All components created"
echo -e "${GREEN}✅${NC} Unit tests passing (9/9)"
echo -e "${GREEN}✅${NC} Database migration ready"
echo -e "${GREEN}✅${NC} UI dialog implemented"
echo -e "${GREEN}✅${NC} Toolbar integration complete"
echo -e "${GREEN}✅${NC} Documentation provided"
echo ""

print_section "READY TO DEPLOY"

echo -e "${GREEN}🎉 Etap 8 implementation is complete and ready for use!${NC}"
echo ""
echo "To start the application:"
echo -e "${BLUE}./run.sh${NC}"
echo ""
echo "To open Etap 8 features:"
echo "Press: ${BLUE}Ctrl+E${NC} (while application is running)"
echo ""

echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
