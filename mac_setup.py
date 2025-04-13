from setuptools import setup
import os

APP = ['src/MockupBuddy/MockupBuddy_PySide6_v0.8.1.py']

# ✅ Explicitly create the assets folder inside the .app bundle
DATA_FILES = [
    ('assets', [
        'src/assets/bmcNT.png',
        'src/assets/MockupBuddyDesktop.icns'
    ])
]

OPTIONS = {
    'argv_emulation': True,
    'includes': ['PySide6', 'PIL'],
    'iconfile': 'src/assets/MockupBuddyDesktop.icns',  # For macOS Dock icon
    'plist': {
        'CFBundleName': 'MockupBuddy',
        'CFBundleDisplayName': 'MockupBuddy',
        'CFBundleGetInfoString': "MockupBuddy v0.8.1 – Powered by PySide6",
        'CFBundleIdentifier': 'com.whitebeardcustom.mockupbuddy',
        'CFBundleVersion': '0.8.1',
        'CFBundleShortVersionString': '0.8.1',
    }
}

setup(
    app=APP,
    name='MockupBuddy',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app']
)