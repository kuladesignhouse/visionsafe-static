#!/usr/bin/env zsh

TEMPLATES_DIR="$(pwd)/templates"
DIST_DIR="$(pwd)/dist"
REMOTE_USER="brgr"
REMOTE_HOST="visionsafe.com"
DEFAULT_REMOTE_DIR="/home/brgr/visionsafe.com/"

# List of special files and their remote paths (space-separated pairs)
SPECIAL_FILES=(
  "loaner-program.html:/home/brgr/visionsafe.com/loaner-program/index.html"
  "warranty-RENAME-index.html:/home/brgr/visionsafe.com/warranty/index.html"
  "g500-video.html:/home/brgr/visionsafe.com/g500-video/index.html"
  "g600-video.html:/home/brgr/visionsafe.com/g600-video/index.html"
)

# --- BUILD ---

echo "Running Gulp build..."
gulp

if [[ $? -ne 0 ]]; then
    echo "❌ Gulp build failed. Aborting."
    exit 1
fi

# --- FILE SELECTION ---

INPUT_NAME="$1"
if [[ -n "$INPUT_NAME" && "$INPUT_NAME" == *.html && -f "$TEMPLATES_DIR/$INPUT_NAME" ]]; then
    SELECTED_NAME="$INPUT_NAME"
else
    FILES=($(find "$TEMPLATES_DIR" -maxdepth 1 -type f -name "*.html" \
        ! -name ".DS_Store" ! -name "*.njk" ! -name "*.py" \
        -exec basename {} \; | sort))

    if [[ ${#FILES[@]} -eq 0 ]]; then
        echo "❌ No HTML files found in $TEMPLATES_DIR"
        exit 1
    fi

    SELECTED_NAME=$(printf "%s\n" "${FILES[@]}" | fzf \
        --prompt="Select an HTML file to deploy: " \
        --height=10 --reverse --cycle --info=inline --layout=default)

    if [[ -z "$SELECTED_NAME" ]]; then
        echo "❌ No file selected. Aborting."
        exit 1
    fi
fi

echo "Selected file: $SELECTED_NAME"
SOURCE_FILE="$DIST_DIR/$SELECTED_NAME"

if [[ ! -f "$SOURCE_FILE" ]]; then
    echo "❌ File not found in dist: $SOURCE_FILE"
    exit 1
fi

# --- DEPLOY ---

# Find if selected file is special, get remote path, else empty
REMOTE_PATH=""

for pair in "${SPECIAL_FILES[@]}"; do
  file="${pair%%:*}"
  path="${pair#*:}"
  if [[ "$SELECTED_NAME" == "$file" ]]; then
    REMOTE_PATH="$path"
    break
  fi
done

if [[ -n "$REMOTE_PATH" ]]; then
  echo "🚀 Deploying special file: $SELECTED_NAME → index.html at $REMOTE_PATH"
  /usr/bin/scp "$SOURCE_FILE" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH"
else
  echo "🚀 Deploying standard file to $DEFAULT_REMOTE_DIR"
  /usr/bin/scp "$SOURCE_FILE" "$REMOTE_USER@$REMOTE_HOST:$DEFAULT_REMOTE_DIR"
fi

if [[ $? -eq 0 ]]; then
  echo "✅ File transferred successfully!"
  /usr/bin/afplay /System/Library/Sounds/Purr.aiff
else
  echo "❌ File transfer failed."
  exit 1
fi
