# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for qualtrics-util.

This spec file is used to create standalone executables for
Linux, macOS, and Windows platforms.

Usage:
    pyinstaller qualtrics-util.spec
"""

import os

# PyInstaller imports
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

# Determine the entry point
a = Analysis(
    ['standalone_main.py'],  # Use standalone entry point that handles imports correctly
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),  # Include config directory
    ],
    hiddenimports=[
        # Collect all pandas submodules
        *collect_submodules('pandas'),
        
        # Collect all numpy submodules
        *collect_submodules('numpy'),
        
        # Core dependencies
        'requests',
        'yaml',
        'python-dotenv',
        'dotenv',
        'dateutil',
        'certifi',
        'charset_normalizer',
        'idna',
        
        # Refactored module imports
        'qualtrics_util',
        'qualtrics_util.cli',
        'qualtrics_util.config',
        'qualtrics_util.api',
        'qualtrics_util.api.contacts',
        'qualtrics_util.api.distributions',
        'qualtrics_util.api.messages',
        'qualtrics_util.api.surveys',
    ],
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='qualtrics-util',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon file path if you have one
)
