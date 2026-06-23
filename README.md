# Discord Proxy Launcher

A lightweight Windows application that launches Discord with an HTTP proxy server.

## Features

- Launch Discord through an HTTP proxy
- Automatically injects `version.dll` into Discord's directory and all `app-*` subfolders
- Saves proxy settings to `config.json`
- Auto-detects Discord installation
- Supports both GUI and command-line usage

## Requirements

- Windows
- Python 3.8+
- PyInstaller (to build the exe)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### GUI

```bash
python main.py
```

### CLI

```bash
python cli.py -H 127.0.0.1 -p 10808
```

| Flag | Description |
|------|-------------|
| `-H` | Proxy host |
| `-p` | Proxy port |
| `-d` | Path to Discord.exe or Update.exe |

## Building the Exe

```bash
python build.py
```

The output will be in `dist/DiscordProxy.exe`.

## How It Works

1. Copies `version.dll` to Discord's root folder and all `app-*` subfolders
2. Launches Discord with `--a=--proxy-server=http://host:port`

## Files

| File | Description |
|------|-------------|
| `main.py` | GUI application |
| `cli.py` | Command-line interface |
| `build.py` | PyInstaller build script |
| `config.json` | Saved proxy settings |
| `version.dll` | DLL to inject into Discord ([source](https://github.com/aiqinxuancai/discord-proxy)) |

## Tips

1. **Add Discord folder to Windows Defender exclusions** to prevent false positive detection:
   - Open Windows Security > Virus & threat protection > Manage settings > Exclusions > Add an exclusion
   - Add the folder: `%LOCALAPPDATA%\Discord`

2. **Copy `DiscordProxy.exe` to the Discord folder** for easier access:
   - Copy `DiscordProxy.exe` to `C:\Users\<YourUser>\AppData\Local\Discord\`
   - `version.dll` will be copied automatically on first launch

3. **Create a desktop shortcut**:
   - Right-click `DiscordProxy.exe` > Send to > Desktop (create shortcut)
   - Rename the shortcut to something like "Discord Proxy"
   - Launch Discord from this shortcut anytime

4. **Set your proxy and launch**:
   - Enter your proxy host and port in the app
   - Click "Launch Discord" — done!

## License

MIT
