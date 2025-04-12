# MockupBuddy – User Guide (Windows Edition)

MockupBuddy is a fast, lightweight mockup generator built for print-on-demand sellers who need a quick way to create product mockups with minimal effort. This guide will walk you through installation, usage, and design best practices.

---

## 🚀 Installation Guide

### System Requirements
- **Operating System**: Windows 10 or higher (64-bit)
- **Memory**: 4 GB RAM or more
- **Disk Space**: ~200MB for installation
- **Python**: Not required — fully compiled executable

### SmartScreen Warning (IMPORTANT)

> ⚠️ **Why am I seeing this warning?**  
> Because MockupBuddy is provided **100% free of charge**, and **code-signing is an added expense that isn’t viable for most solo developers**, the installer is **not digitally signed**.

As a result, Windows Defender SmartScreen may block the installer the first time you run it.

To proceed safely:
1. Click **More info**
2. Click **Run anyway**
3. Follow the normal installation prompts


### Installation Steps
1. **Download** the installer via the provided Google Docs link.
2. **Double-click** the `MockupBuddy_Setup.exe` file.
3. Follow the prompts and **choose installation options**:
   - Choose destination folder
   - Optionally create a **Desktop shortcut**
4. Click **Install** to finish setup.

---

## 🧰 Using MockupBuddy

### Folder Setup
Prepare these three folders before starting:
- **Design Folder** – Transparent PNG designs, tagged `-Light` or `-Dark`
- **Mockup Folder** – Mockup images sorted into subfolders (e.g., `/Mockups/BellaCanvas3001`)
- **Completed Mockups** – Your exported mockups will be saved here

### Mockup Modes

#### 🔹 Single Design Mode
- Select one design
- Select a mockup **template folder**
- Adjust **position, size, and opacity** using sliders
- Click **Generate Mockup** to export

#### 🔸 Batch Mode (Folder-to-Folder)
- Load full folders of designs and mockups
- Designs are automatically matched with compatible mockups
- Files are saved with auto-generated names like `DesignName_MockupName.png`

---

## 🎨 Light/Dark Design Tagging – Critical for Accurate Mockups

> 💡 **IMPORTANT: Tag your design filenames correctly for best results!**

To ensure that each design is paired with the correct T-shirt mockup background, you **must include a tag in the filename**:

### ✅ Accepted Naming Tags
- **`-Light`** → for designs intended for **light-colored shirts**  
  _e.g., White, Aqua, Peach, Heather Yellow, etc._
- **`-Dark`** → for designs intended for **dark-colored shirts**  
  _e.g., Black, Navy, Charcoal, Dark Heather Purple, etc._

**Examples:**
- `rocknroll-Light.png` → used only with **light mockups**
- `skullart-Dark.png` → used only with **dark mockups**

> ⚠️ **If you don’t tag your files**, the design will be applied to **every mockup**, which may result in poor contrast and unreadable output.

---


## ☕ Support This Project

MockupBuddy is free to use. If it saves you time or makes your workflow easier, consider showing your support:

<a href="https://www.buymeacoffee.com/nicktrautman" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;">
</a>

Your support helps fund code-signing, future features, and continued development.

```python
import sys
import subprocess
import webbrowser

def open_support_link():
    url = "https://www.buymeacoffee.com/nicktrautman"
    try:
        if sys.platform == "win32":
            # Try to open with subprocess fallback
            try:
                subprocess.run(["start", url], check=True, shell=True)
            except Exception:
                # If subprocess fails, try webbrowser
                webbrowser.open(url)
        else:
            webbrowser.open(url)
    except Exception as e:
        print(f"Failed to open browser: {e}")
```

---

## 📄 License

This software is released under the **MIT License**. Please review the included `LICENSE.txt` file.

---

MockupBuddy v0.8 — Documentation last updated: April 2025
