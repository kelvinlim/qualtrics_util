# Executable Build Setup

This document explains how to build cross-platform executables for qualtrics-util.

## Overview

The project uses PyInstaller to create standalone executables that don't require Python to be installed on the target system.

## Files Created

1. **`qualtrics-util.spec`** - PyInstaller specification file
2. **`.github/workflows/build-executables.yml`** - GitHub Actions workflow for automated builds
3. **`Makefile`** - Local build commands

## Local Build

### Build for Current Platform

```bash
make build
```

Or manually:

```bash
pyinstaller qualtrics-util.spec
```

The executable will be created in `dist/qualtrics-util`.

### Test the Build

```bash
make check-executable
```

Or manually:

```bash
./dist/qualtrics-util --version
./dist/qualtrics-util --help
```

### Clean Build Artifacts

```bash
make clean
```

## GitHub Actions Build

The `.github/workflows/build-executables.yml` workflow automatically builds executables for:
- Linux (AMD64)
- macOS (Intel - AMD64)
- macOS (Apple Silicon - ARM64)
- Windows (AMD64)

### Trigger a Build

#### Automatic (on Git Tags)
```bash
git tag v2.0.10
git push origin v2.0.10
```

#### Manual (via GitHub UI)
1. Go to Actions
2. Select "Build Cross-Platform Executables"
3. Click "Run workflow"
4. Choose platform
5. Run

### Build Products

Each build produces:
- Executable file (platform-specific)
- SHA256 checksum file
- All uploaded as GitHub Release assets

## Using the Executables

### Download

Download from GitHub Releases:
```
https://github.com/kelvinlim/qualtrics_util/releases
```

### Installation

**Linux:**
```bash
chmod +x qualtrics-util-linux-amd64
sudo mv qualtrics-util-linux-amd64 /usr/local/bin/qualtrics-util
```

**macOS:**
```bash
chmod +x qualtrics-util-macos-arm64
sudo mv qualtrics-util-macos-arm64 /usr/local/bin/qualtrics-util
```

**Windows:**
Just place `qualtrics-util-windows-amd64.exe` in your PATH or run from current directory.

### Usage

```bash
./qualtrics-util --config config/config_qualtrics.yaml --cmd list
```

## Build Configuration

### Spec File Options

The `qualtrics-util.spec` file contains:

- **Entry point:** `qualtrics_util.py`
- **Includes:** Config directory with all YAML files
- **Hidden imports:** All required packages (pandas, numpy, etc.)
- **Output:** Single-file executable

### Customization

Edit `qualtrics-util.spec` to:
- Add icons
- Change output name
- Include additional files
- Modify UPX compression

## Troubleshooting

### Import Errors

If you get import errors, add the missing module to `hiddenimports` in the spec file:

```python
hiddenimports=[
    'module_name',
    ...
]
```

### Large Executable Size

The executable includes all dependencies. To reduce size:
- Remove unused packages from requirements.txt
- Use `excludes` in spec file
- Consider using UPX compression

### Build Fails

Check:
1. All dependencies installed
2. PyInstaller up to date: `pip install --upgrade pyinstaller`
3. Check build logs in `build/qualtrics-util/`

## GitHub Actions Logs

View build progress at:
```
https://github.com/kelvinlim/qualtrics_util/actions
```

## Verification

After downloading an executable, verify its integrity:

```bash
# Linux/macOS
shasum -c qualtrics-util-*.sha256

# Windows (PowerShell)
Get-FileHash qualtrics-util-windows-amd64.exe -Algorithm SHA256
```

## Quick Reference

```bash
# Build locally
make build

# Test executable
./dist/qualtrics-util --version

# Clean artifacts
make clean

# Build for release
git tag v2.0.10 && git push origin v2.0.10
```

## Notes

- The executable includes all Python dependencies
- No Python installation required on target system
- Config files are included in the executable bundle
- Size: ~30-40MB depending on platform

