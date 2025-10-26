# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for qualtrics-util.

This spec file is used to create standalone executables for
Linux, macOS, and Windows platforms.

Usage:
    pyinstaller qualtrics-util.spec
"""

import os

block_cipher = None

# Determine the entry point
a = Analysis(
    ['qualtrics_util.py'],  # Use the original entry point
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),  # Include config directory
    ],
    hiddenimports=[
        'requests',
        'yaml',
        'pandas',
        'python-dotenv',
        'dateutil',
        'zoneinfo',
        'json',
        'datetime',
        'random',
        'string',
        'tempfile',
        'zipfile',
        'io',
        'glob',
        'shutil',
        'textwrap',
        'pprint',
        'time',
        'sys',
        'argparse',
        'numpy',
        'numpy.core',
        'numpy.core._methods',
        'numpy.lib',
        'numpy.lib.format',
        'pandas.io',
        'pandas.io.formats',
        'pandas.io.formats.style',
    ],
    hookspath=[],
    hooksconfig={},
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
