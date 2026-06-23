import argparse
import atexit
import glob
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def get_app_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


def get_data_dir():
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent


APP_DIR = get_app_dir()
DATA_DIR = get_data_dir()
CONFIG_FILE = APP_DIR / "config.json"
DLL_NAME = "version.dll"
DLL_SOURCE = DATA_DIR / DLL_NAME


def cleanup_mei():
    if not getattr(sys, "frozen", False):
        return
    temp_dir = os.environ.get("TEMP", os.environ.get("TMP", ""))
    if not temp_dir:
        return
    for mei_dir in glob.glob(os.path.join(temp_dir, "_MEI*")):
        if os.path.isdir(mei_dir) and mei_dir != os.path.dirname(sys.executable):
            try:
                shutil.rmtree(mei_dir, ignore_errors=True)
            except Exception:
                pass


atexit.register(cleanup_mei)


def find_discord():
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    roaming = Path(os.environ.get("APPDATA", ""))

    candidates = [
        local / "Discord" / "Update.exe",
        roaming / "Discord" / "Update.exe",
    ]

    for p in candidates:
        if p.is_file():
            return str(p)
    return ""


def resolve_update_exe(discord_path):
    p = Path(discord_path)
    if p.name.lower() == "update.exe":
        return str(p)
    update = p.parent.parent / "Update.exe"
    if update.is_file():
        return str(update)
    return str(p)


def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"host": "127.0.0.1", "port": "10808", "discord_path": ""}


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def inject_dll(discord_path):
    if not DLL_SOURCE.is_file():
        return False, f"{DLL_NAME} not found next to the application."

    discord_dir = Path(discord_path).parent
    try:
        shutil.copy2(DLL_SOURCE, discord_dir / DLL_NAME)
        for child in discord_dir.iterdir():
            if child.is_dir() and child.name.lower().startswith("app"):
                shutil.copy2(DLL_SOURCE, child / DLL_NAME)
        return True, None
    except Exception as e:
        return False, str(e)


def launch_discord(update_path, host, port):
    proxy_url = f"http://{host}:{port}"
    proxy_flag = f"--a=--proxy-server={proxy_url}"

    subprocess.Popen([update_path, "--processStart", "Discord.exe", proxy_flag])


def main():
    parser = argparse.ArgumentParser(description="Launch Discord with an HTTP proxy")
    parser.add_argument("-H", "--host", help="Proxy host (default: 127.0.0.1)")
    parser.add_argument("-p", "--port", help="Proxy port (default: 10808)")
    parser.add_argument("-d", "--discord", dest="discord_path", help="Path to Discord.exe or Update.exe")
    args = parser.parse_args()

    config = load_config()
    host = args.host or config["host"]
    port = args.port or config["port"]
    discord_path = args.discord_path or config.get("discord_path", "") or find_discord()

    if not discord_path or not os.path.isfile(discord_path):
        print("Error: Discord not found. Use --discord to specify the path.")
        sys.exit(1)

    update_path = resolve_update_exe(discord_path)

    ok, err = inject_dll(update_path)
    if not ok:
        print(f"Error: {err}")
        sys.exit(1)

    print(f"Launching: {update_path} --processStart Discord.exe --a=--proxy-server=http://{host}:{port}")
    launch_discord(update_path, host, port)

    config["discord_path"] = discord_path
    save_config(config)


if __name__ == "__main__":
    main()
