"""
FFmpeg Helper -- Detecta FFmpeg no Windows automaticamente
"""

import subprocess
import sys
import os
import platform
from pathlib import Path


def check_ffmpeg() -> bool:
    """Retorna True se ffmpeg esta disponivel no PATH."""
    try:
        r = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_ffmpeg_path_windows() -> Path | None:
    """Procura ffmpeg em locais comuns no Windows."""
    import glob as _glob

    common_paths = [
        Path("C:/ffmpeg/bin/ffmpeg.exe"),
        Path("C:/Program Files/ffmpeg/bin/ffmpeg.exe"),
        Path("C:/tools/ffmpeg/bin/ffmpeg.exe"),
        Path.home() / "ffmpeg" / "bin" / "ffmpeg.exe",
    ]
    for p in common_paths:
        if p.exists():
            return p.parent

    # Winget: qualquer versao do Gyan.FFmpeg
    winget_base = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/WinGet/Packages"
    if winget_base.exists():
        pattern = str(winget_base / "Gyan.FFmpeg*" / "ffmpeg-*" / "bin" / "ffmpeg.exe")
        matches = _glob.glob(pattern)
        if matches:
            return Path(matches[0]).parent

    return None


def add_to_path_windows(bin_dir: Path):
    """Adiciona um diretorio ao PATH da sessao atual."""
    os.environ["PATH"] = str(bin_dir) + os.pathsep + os.environ.get("PATH", "")
    print(f"   [+] Added to PATH: {bin_dir}")


def print_install_instructions():
    """Imprime instrucoes de instalacao."""
    system = platform.system()

    print("\n" + "=" * 60)
    print("[X] FFmpeg NOT FOUND -- Required for video creation")
    print("=" * 60)

    if system == "Windows":
        print("""
OPTION 1 -- Winget (Recommended, 1 command):
  Open PowerShell as Administrator and run:

    winget install Gyan.FFmpeg

  After install, CLOSE and REOPEN PowerShell, then run:
    python main.py

---------------------------------------------------------
OPTION 2 -- Manual (no admin required):

  1. Download from: https://www.gyan.dev/ffmpeg/builds/
     File: ffmpeg-release-essentials.zip

  2. Extract to: C:\\ffmpeg\\

  3. Add to PATH:
     Search "Environment Variables" in Windows
     -> System Variables -> Path -> Edit -> New
     -> Add: C:\\ffmpeg\\bin
     -> OK -> Restart PowerShell

  4. Test: ffmpeg -version
---------------------------------------------------------
OPTION 3 -- Chocolatey:
  choco install ffmpeg
""")
    elif system == "Darwin":
        print("\nRun in Terminal:\n  brew install ffmpeg\n")
    else:
        print("\nRun in Terminal:\n  sudo apt update && sudo apt install ffmpeg -y\n")

    print("=" * 60)


def ensure_ffmpeg() -> bool:
    """
    Verifica FFmpeg. Se nao encontrar, tenta localizar no Windows e
    adicionar ao PATH automaticamente. Se falhar, imprime instrucoes.
    Retorna True se ffmpeg esta disponivel.
    """
    if check_ffmpeg():
        return True

    # Windows: tenta achar em locais comuns
    if platform.system() == "Windows":
        bin_dir = get_ffmpeg_path_windows()
        if bin_dir:
            add_to_path_windows(bin_dir)
            if check_ffmpeg():
                print(f"   [OK] FFmpeg found at: {bin_dir}")
                return True

    print_install_instructions()
    return False
