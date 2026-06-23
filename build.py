import PyInstaller.__main__
import shutil
from pathlib import Path

dist = Path("dist")
if dist.exists():
    shutil.rmtree(dist)

build = Path("build")
if build.exists():
    shutil.rmtree(build)

spec = Path("DiscordProxy.spec")
if spec.exists():
    spec.unlink()

PyInstaller.__main__.run([
    "main.py",
    "--onefile",
    "--windowed",
    "--name=DiscordProxy",
    "--clean",
    "--noconfirm",
    f"--add-data=config.json;.",
    f"--add-data=version.dll;.",
])
