from setuptools import setup

APP = ['src/MockupBuddy/MockupBuddy_PySide6_v0.8.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'includes': ['PySide6'],
    'iconfile': 'src/assets/MockupBuddyDesktop.icns',
    'resources': ['src/assets/bmcNT.png'],  # ✅ Keep this as a direct file
}

setup(
    app=APP,
    name='MockupBuddy',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)