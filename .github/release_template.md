# qualtrics-util v{version}

## Downloads

### Executables (No Python Installation Required)

| Platform | Download | SHA256 |
|----------|----------|--------|
| Linux (AMD64) | [qualtrics-util-linux-amd64](https://github.com/kelvinlim/qualtrics_util/releases/download/v{version}/qualtrics-util-linux-amd64) | [checksum](https://github.com/kelvinlim/qualtrics_util/releases/download/v{version}/qualtrics-util-linux-amd64.sha256) |
| macOS (Intel) | [qualtrics-util-macos-amd64](https://github.com/kelvinlim/qualtrics_util/releases/download/v{version}/qualtrics-util-macos-amd64) | [checksum](https://github.com/kelvinlim/qualtrics_util/releases/download/v{version}/qualtrics-util-macos-amd64.sha256) |
| macOS (Apple Silicon) | [qualtrics-util-macos-arm64](https://github.com/kelvinlim/qualtrics_util/releases/download/v{version}/qualtrics-util-macos-arm64) | [checksum](https://github.com/kelvinlim/qualtrics_util/releases/download/v{version}/qualtrics-util-macos-arm64.sha256) |
| Windows (AMD64) | [qualtrics-util-windows-amd64.exe](https://github.com/kelvinlim/qualtrics_util/releases/download/v{version}/qualtrics-util-windows-amd64.exe) | [checksum](https://github.com/kelvinlim/qualtrics_util/releases/download/v{version}/qualtrics-util-windows-amd64.exe.sha256) |

### Installation Instructions

1. **Download** the appropriate executable for your platform
2. **Make executable** (Linux/macOS):
   ```bash
   chmod +x qualtrics-util-*
   ```
3. **Move to PATH** (optional):
   ```bash
   # Linux/macOS
   sudo mv qualtrics-util-* /usr/local/bin/qualtrics-util
   
   # Windows: Add to PATH or run from current directory
   ```
4. **Verify installation**:
   ```bash
   qualtrics-util --version
   ```

### Configuration

Before using, you need to set up:

1. **API Token**: Create a `qualtrics_token` file with your Qualtrics API token:
   ```
   QUALTRICS_APITOKEN=YourTokenGoesHere
   ```

2. **Configuration File**: Create a YAML configuration file (see `config/config_sample.yaml`)

### Usage

```bash
# Check configuration
qualtrics-util --config config_qualtrics.yaml --cmd check

# List contacts
qualtrics-util --config config_qualtrics.yaml --cmd list

# Send distributions
qualtrics-util --config config_qualtrics.yaml --cmd send
```

For more information, see the [README](https://github.com/kelvinlim/qualtrics_util/blob/main/README.md).

## Changes in this Release

{changelog}

## Verification

To verify the integrity of downloaded files:

```bash
# Linux/macOS
sha256sum -c qualtrics-util-*.sha256

# Windows (PowerShell)
Get-FileHash qualtrics-util-windows-amd64.exe -Algorithm SHA256
```
