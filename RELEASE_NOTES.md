# MockupBuddy – Release Notes

## v0.8.1 – April 13, 2025
🎯 First stable GitHub-backed release for cross-platform use

### ✨ New Features
- Refined mockup preview logic for accurate image scaling and centering
- Improved GUI layout: better spacing, preview window containment, and control visibility
- Added Windows `.spec` and Inno Setup `.iss` support to align with macOS packaging

### 🐞 Fixes
- Fixed “Buy Me a Coffee” button on Windows to open browser correctly
- Removed legacy `.spec` file to eliminate confusion
- Removed large files from Git history and cleaned up virtual environment bloat

### 📦 Packaging
- macOS `.app` manually created from `mac_setup.py`
- Windows `.exe` generated via PyInstaller and packaged with Inno Setup
- GitHub repo cleaned and maintained via `.gitignore`, GitHub push discipline, and release tagging