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
    ['standalone_main.py'],  # Use standalone entry point that handles imports correctly
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),  # Include config directory
    ],
    hiddenimports=[
        'requests',
        'yaml',
        'pandas',
        'pandas._libs.tslibs.timedeltas',
        'pandas._libs.tslibs.nattype',
        'pandas._libs.tslibs.np_datetime',
        'pandas._libs.writers',
        'python-dotenv',
        'dotenv',
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
        'numpy._core',
        'numpy.core',
        'numpy.core._methods',
        'numpy.core._multiarray_umath',
        'numpy.core.multiarray',
        'numpy.core.memmap',
        'numpy.core.structured',
        'numpy.core.ndarray',
        'numpy.core.umath',
        'numpy.lib',
        'numpy.lib.format',
        'numpy.compat',
        'numpy.compat.py3k',
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
