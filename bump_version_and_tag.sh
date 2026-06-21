#!/bin/bash
# Bump version in src/miniplayer/__init__.py, commit, tag, and push

set -e

INIT_FILE="src/miniplayer/__init__.py"

if [ ! -f "$INIT_FILE" ]; then
  echo "Error: $INIT_FILE not found!"
  exit 1
fi

# Extract current version
over=$(grep -Eo "__version__\s*=\s*['\"]([^'\"]+)['\"]" "$INIT_FILE" | head -1 | sed -E "s/__version__\s*=\s*['\"]([^'\"]+)['\"]/\1/")
if [ -z "$over" ]; then
  echo "Error: Could not find __version__ in $INIT_FILE"
  exit 1
fi

echo "Current version: $over"

# Bump patch version (e.g. 1.2.3 -> 1.2.4)
IFS='.' read -r major minor patch <<< "$over"
if [ -z "$patch" ]; then
  patch=0
fi
new_patch=$((patch + 1))
new_version="$major.$minor.$new_patch"

echo "Bumping to: $new_version"

# Update version in file
sed -i "s/__version__\s*=\s*['\"]$over['\"]/__version__ = '$new_version'/" "$INIT_FILE"

git add "$INIT_FILE"
git commit -m "Bump version to $new_version"
git tag "v$new_version"
git push
git push origin "v$new_version"

echo "Version bumped and tagged: v$new_version"
