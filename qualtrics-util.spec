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

# Collect numpy and pandas dependencies
numpy_data, numpy_binaries, numpy_hiddenimports = collect_all('numpy')
pandas_data, pandas_binaries, pandas_hiddenimports = collect_all('pandas')

# Determine the entry point
a = Analysis(
    ['standalone_main.py'],  # Use monolithic standalone entry point
    pathex=[],  # Use current directory
    binaries=[] + numpy_binaries + pandas_binaries,
    datas=[
        ('config', 'config'),  # Include config directory
    ] + numpy_data + pandas_data,
    hiddenimports=[
        # Core dependencies for monolithic version
        'requests',
        'yaml', 
        'python-dotenv',
        'dotenv',
        'dateutil',
        'certifi',
        'charset_normalizer',
        'idna',
    ] + numpy_hiddenimports + pandas_hiddenimports,
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
    strip=True,
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
    onefile=False,
)
