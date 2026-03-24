#!/usr/bin/env zsh

TEMPLATES_DIR="$(pwd)/templates"
DIST_DIR="$(pwd)/dist"
REMOTE_USER="brgr"
REMOTE_HOST="visionsafe.com"
DEFAULT_REMOTE_DIR="/home/brgr/visionsafe.com/"
DEPLOY_ALL=false

# List of special files and their remote paths (space-separated pairs)
SPECIAL_FILES=(
  "loaner-program.html:/home/brgr/visionsafe.com/loaner-program/index.html"
  "warranty-RENAME-index.html:/home/brgr/visionsafe.com/warranty/index.html"
  "g500-video.html:/home/brgr/visionsafe.com/g500-video/index.html"
  "g600-video.html:/home/brgr/visionsafe.com/g600-video/index.html"
  "van-tour.html:/home/brgr/visionsafe.com/van-tour/index.html"
)

# --- BUILD ---

echo "Running Gulp build..."
gulp

if [[ $? -ne 0 ]]; then
    echo "❌ Gulp build failed. Aborting."
    exit 1
fi

# --- HELPERS ---

find_remote_path() {
  local selected_name="$1"

  for pair in "${SPECIAL_FILES[@]}"; do
    local file="${pair%%:*}"
    local remote_path="${pair#*:}"
    if [[ "$selected_name" == "$file" ]]; then
      echo "$remote_path"
      return 0
    fi
  done

  return 1
}

deploy_file() {
  local selected_name="$1"
  local source_file="$DIST_DIR/$selected_name"
  local remote_path

  if [[ ! -f "$source_file" ]]; then
    echo "❌ File not found in dist: $source_file"
    return 1
  fi

  remote_path="$(find_remote_path "$selected_name")"

  if [[ -n "$remote_path" ]]; then
    echo "🚀 Deploying special file: $selected_name → index.html at $remote_path"
    /usr/bin/scp "$source_file" "$REMOTE_USER@$REMOTE_HOST:$remote_path"
  else
    echo "🚀 Deploying standard file: $selected_name → $DEFAULT_REMOTE_DIR"
    /usr/bin/scp "$source_file" "$REMOTE_USER@$REMOTE_HOST:$DEFAULT_REMOTE_DIR"
  fi
}

# --- FILE SELECTION ---

INPUT_NAME="$1"

if [[ "$INPUT_NAME" == "all" || "$INPUT_NAME" == "--all" ]]; then
    DEPLOY_ALL=true
fi

if [[ "$DEPLOY_ALL" == true ]]; then
    FILES=($(find "$TEMPLATES_DIR" -maxdepth 1 -type f -name "*.html" \
        ! -name ".DS_Store" ! -name "*.njk" ! -name "*.py" \
        -exec basename {} \; | sort))

    if [[ ${#FILES[@]} -eq 0 ]]; then
        echo "❌ No HTML files found in $TEMPLATES_DIR"
        exit 1
    fi

    echo "Selected mode: deploy all HTML pages (${#FILES[@]} files)"
elif [[ -n "$INPUT_NAME" && "$INPUT_NAME" == *.html && -f "$TEMPLATES_DIR/$INPUT_NAME" ]]; then
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

if [[ "$DEPLOY_ALL" != true ]]; then
    echo "Selected file: $SELECTED_NAME"
fi

# --- DEPLOY ---

if [[ "$DEPLOY_ALL" == true ]]; then
  FAILED_FILES=()

  for file in "${FILES[@]}"; do
    if ! deploy_file "$file"; then
      FAILED_FILES+=("$file")
    fi
  done

  if [[ ${#FAILED_FILES[@]} -eq 0 ]]; then
    echo "✅ All files transferred successfully!"
    /usr/bin/afplay /System/Library/Sounds/Purr.aiff
  else
    echo "❌ Failed to transfer ${#FAILED_FILES[@]} file(s):"
    printf ' - %s\n' "${FAILED_FILES[@]}"
    exit 1
  fi
else
  if deploy_file "$SELECTED_NAME"; then
    echo "✅ File transferred successfully!"
    /usr/bin/afplay /System/Library/Sounds/Purr.aiff
  else
    echo "❌ File transfer failed."
    exit 1
  fi
fi
