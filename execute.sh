#!/bin/bash
#
# Setup and Execution Script for Vibestand Posture Assistant
#
# INSTRUCTIONS:
# 1. Save the provided diff output to a file named 'vibestand.patch'.
# 2. Place this patch file in the root directory of your 'vibestand' project.
# 3. Run this script from the root directory: ./execute.sh
#

# --- Configuration ---
PYTHON_CMD="python3"
VENV_DIR="venv"
PATCH_FILE="vibestand.patch"
HAARCASCADE_URL="https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
HAARCASCADE_DIR="assets"
HAARCASCADE_FILE="$HAARCASCADE_DIR/haarcascade_frontalface_default.xml"

# --- Functions ---
print_info() {
    echo -e "\033[0;32mINFO:\033[0m $1"
}

print_error() {
    echo -e "\033[0;31mERROR:\033[0m $1" >&2
    exit 1
}

# --- Main Script ---

# 1. Apply the patch
if [ -f "$PATCH_FILE" ]; then
    print_info "Applying patch from '$PATCH_FILE'..."
    git apply "$PATCH_FILE" || print_error "Failed to apply the patch. Please check for conflicts."
else
    print_info "Patch file '$PATCH_FILE' not found. Assuming files are already in place."
fi

# 2. Create Virtual Environment
if [ ! -d "$VENV_DIR" ]; then
    print_info "Creating Python virtual environment in '$VENV_DIR'..."
    $PYTHON_CMD -m venv $VENV_DIR || print_error "Failed to create virtual environment."
fi

# 3. Activate Virtual Environment and Install Dependencies
print_info "Activating virtual environment and installing dependencies..."
source "$VENV_DIR/bin/activate" || print_error "Failed to activate virtual environment."
pip install -r requirements.txt || print_error "Failed to install dependencies from requirements.txt."

# 4. Download Haar Cascade file
mkdir -p $HAARCASCADE_DIR || print_error "Failed to create assets directory."
if [ ! -f "$HAARCASCADE_FILE" ]; then
    print_info "Downloading Haar Cascade file for face detection..."
    curl -L -o "$HAARCASCADE_FILE" "$HAARCASCADE_URL" || print_error "Failed to download Haar Cascade file."
fi

# 5. Run the application
print_info "Setup complete. Running the application..."
$PYTHON_CMD -m src
