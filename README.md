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

## License

MIT
