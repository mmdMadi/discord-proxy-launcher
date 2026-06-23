import atexit
import glob
import json
import os
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
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


class App:
    def __init__(self, root):
        self.root = root
        root.title("Discord Proxy Launcher")
        root.geometry("420x220")
        root.resizable(False, False)

        self.config = load_config()

        main = ttk.Frame(root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        pf = ttk.LabelFrame(main, text="Proxy Settings", padding=8)
        pf.pack(fill=tk.X, pady=(0, 8))

        r1 = ttk.Frame(pf)
        r1.pack(fill=tk.X, pady=2)
        ttk.Label(r1, text="Host:").pack(side=tk.LEFT)
        self.host_var = tk.StringVar(value=self.config["host"])
        ttk.Entry(r1, textvariable=self.host_var, width=20).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(r1, text="Port:").pack(side=tk.LEFT, padx=(10, 0))
        self.port_var = tk.StringVar(value=self.config["port"])
        ttk.Entry(r1, textvariable=self.port_var, width=8).pack(side=tk.LEFT, padx=(5, 0))

        df = ttk.LabelFrame(main, text="Discord Path", padding=8)
        df.pack(fill=tk.X, pady=(0, 8))

        r3 = ttk.Frame(df)
        r3.pack(fill=tk.X)
        self.discord_var = tk.StringVar(value=self.config.get("discord_path", ""))
        ttk.Entry(r3, textvariable=self.discord_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(r3, text="Browse", command=self.browse_discord).pack(side=tk.LEFT, padx=(5, 0))

        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(btn_frame, text="Launch Discord", command=self.launch).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(btn_frame, text="Save Config", command=self.save).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

    def browse_discord(self):
        path = filedialog.askopenfilename(
            title="Select Discord.exe or Update.exe",
            filetypes=[("Discord", "*.exe"), ("All", "*.*")],
        )
        if path:
            self.discord_var.set(path)

    def save(self):
        self.config["host"] = self.host_var.get().strip()
        self.config["port"] = self.port_var.get().strip()
        self.config["discord_path"] = self.discord_var.get().strip()
        save_config(self.config)

    def launch(self):
        host = self.host_var.get().strip()
        port = self.port_var.get().strip()
        if not host or not port:
            messagebox.showerror("Error", "Host and Port are required.")
            return

        discord_path = self.discord_var.get().strip()
        if not discord_path:
            discord_path = find_discord()
        if not discord_path or not os.path.isfile(discord_path):
            messagebox.showerror("Error", "Discord not found. Please browse to Discord.exe or Update.exe.")
            return

        update_path = resolve_update_exe(discord_path)

        try:
            ok, err = inject_dll(update_path)
            if not ok:
                messagebox.showerror("DLL Error", f"Failed to copy {DLL_NAME}:\n{err}")
                return

            launch_discord(update_path, host, port)
            self.save()
        except Exception as e:
            messagebox.showerror("Launch Error", str(e))


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
