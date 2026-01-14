#!/bin/bash
# Content Creation Engine - MVP Setup and Test Script
# This script sets up the environment and validates the MVP deployment

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Function to check command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Start
print_header "Content Creation Engine - MVP Setup"

# Check prerequisites
print_info "Checking prerequisites..."

# Check Python
if ! command_exists python3; then
    print_error "Python 3 is not installed"
    echo "Please install Python 3.8 or higher from https://www.python.org/"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    print_error "Python 3.8+ required, found $PYTHON_VERSION"
    exit 1
fi

print_success "Python $PYTHON_VERSION found"

# Check pip
if ! command_exists pip3; then
    print_error "pip3 is not installed"
    echo "Please install pip: https://pip.pypa.io/en/stable/installation/"
    exit 1
fi

print_success "pip3 found"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found"
    echo "Please run this script from the content-creation-engine directory"
    exit 1
fi

print_success "Running from project directory"

# Create virtual environment
print_header "Setting Up Virtual Environment"

if [ -d "venv" ]; then
    print_warning "Virtual environment already exists"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Removing existing virtual environment..."
        rm -rf venv
    else
        print_info "Using existing virtual environment"
    fi
fi

if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv

    if [ $? -eq 0 ]; then
        print_success "Virtual environment created"
    else
        print_error "Failed to create virtual environment"
        exit 1
    fi
else
    print_success "Virtual environment ready"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate

if [ $? -eq 0 ]; then
    print_success "Virtual environment activated"
else
    print_error "Failed to activate virtual environment"
    exit 1
fi

# Upgrade pip
print_header "Upgrading pip"
print_info "Upgrading pip to latest version..."
pip install --upgrade pip --quiet

if [ $? -eq 0 ]; then
    print_success "pip upgraded successfully"
else
    print_warning "pip upgrade failed (continuing anyway)"
fi

# Install dependencies
print_header "Installing Dependencies"
print_info "Installing required packages from requirements.txt..."

pip install -r requirements.txt

if [ $? -eq 0 ]; then
    print_success "All dependencies installed"
else
    print_error "Failed to install dependencies"
    exit 1
fi

# Verify key packages
print_info "Verifying key packages..."
PACKAGES=("pyyaml" "python-docx" "pytest")
ALL_FOUND=true

for package in "${PACKAGES[@]}"; do
    if pip show "$package" >/dev/null 2>&1; then
        VERSION=$(pip show "$package" 2>/dev/null | grep Version | awk '{print $2}')
        print_success "$package ($VERSION)"
    else
        print_error "$package not found"
        ALL_FOUND=false
    fi
done

if [ "$ALL_FOUND" = false ]; then
    print_error "Some packages missing"
    exit 1
fi

# Create output directory if it doesn't exist
if [ ! -d "output" ]; then
    print_info "Creating output directory..."
    mkdir -p output
    print_success "Output directory created"
fi

# Run MVP test
print_header "Running MVP Test Suite"
print_info "Executing comprehensive validation tests..."
echo

python3 mvp_test.py

TEST_EXIT_CODE=$?

# Summary
print_header "Setup Complete"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    print_success "MVP is fully functional!"
    echo
    echo -e "${GREEN}Next steps:${NC}"
    echo "  1. Activate the virtual environment: source venv/bin/activate"
    echo "  2. Run examples: python3 examples/phase2_endtoend.py"
    echo "  3. Generate your first article (see MVP_DEPLOYMENT.md)"
    echo "  4. Customize brand settings: templates/brand/brand_config.py"
    echo
    echo -e "${BLUE}Documentation:${NC}"
    echo "  - MVP Guide: MVP_DEPLOYMENT.md"
    echo "  - Quick Start: QUICKSTART.md"
    echo "  - Architecture: CLAUDE.md"
    echo
    echo -e "${GREEN}Environment is ready! Happy content creation! 🎉${NC}"
    exit 0
else
    print_error "MVP tests failed"
    echo
    echo -e "${YELLOW}Troubleshooting steps:${NC}"
    echo "  1. Review the test output above for specific errors"
    echo "  2. Check MVP_DEPLOYMENT.md for troubleshooting guide"
    echo "  3. Verify Python version: python3 --version"
    echo "  4. Try reinstalling: rm -rf venv && ./setup_and_test.sh"
    echo
    echo -e "${BLUE}Need help? Check the documentation or open an issue on GitHub${NC}"
    exit 1
fi
