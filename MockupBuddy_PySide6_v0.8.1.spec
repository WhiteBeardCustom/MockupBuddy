# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# Define assets path
assets_path = os.path.abspath('src/assets')
assets = [(os.path.join(assets_path, f), 'assets') for f in os.listdir(assets_path) if os.path.isfile(os.path.join(assets_path, f))]

a = Analysis(
    ['src/MockupBuddy/MockupBuddy_PySide6_v0.8.1.py'],
    pathex=['src/MockupBuddy'],
    binaries=[],
    datas=assets,
    hiddenimports=collect_submodules('PySide6'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MockupBuddy_PySide6_v0.8.1',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='src/assets/MockupBuddyDesktop.ico',  # ✅ Windows app icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MockupBuddy_PySide6_v0.8.1'
)