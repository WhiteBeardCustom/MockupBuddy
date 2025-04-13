#!/bin/bash

APP_PATH="dist/MockupBuddy.app/Contents/MacOS"
ASSETS_SRC="src/assets"
ASSETS_DEST="$APP_PATH/assets"

echo "📦 Copying assets to $ASSETS_DEST..."

# Create the destination assets folder if it doesn't exist
mkdir -p "$ASSETS_DEST"

# Copy all relevant asset files
cp "$ASSETS_SRC"/*.png "$ASSETS_DEST"
cp "$ASSETS_SRC"/*.icns "$ASSETS_DEST"

echo "✅ Assets copied successfully."