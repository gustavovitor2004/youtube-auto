"""
TikTok Setup Helper
Run: python setup_tiktok.py
"""

import subprocess
import sys
from pathlib import Path

GUIDE = """
+----------------------------------------------------------+
|              TikTok Upload Setup — 3 Steps               |
+----------------------------------------------------------+

STEP 1 — Instale a extensao no Chrome:
  "Get cookies.txt LOCALLY"
  https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc

STEP 2 — Exporte os cookies do TikTok:
  1. Abra o Chrome e acesse: https://www.tiktok.com
  2. Faca login na sua conta TikTok
  3. Clique na extensao "Get cookies.txt LOCALLY"
  4. Selecione "Export" ou "Copy cookies.txt"
  5. Salve o arquivo como: tiktok_cookies.txt
  6. Coloque ele aqui: {cookies_path}

STEP 3 — Teste o upload:
  python main.py --upload

+----------------------------------------------------------+
IMPORTANTE:
  - Os cookies expiram depois de algumas semanas
  - Se o upload falhar, repita o STEP 2
  - Mantenha o Chrome aberto durante o upload
  - O TikTok pode pedir confirmacao manual na primeira vez
+----------------------------------------------------------+
"""

COOKIES_FILE = Path("tiktok_cookies.txt")


def check_package():
    try:
        from tiktok_uploader.upload import upload_videos
        return True
    except ImportError:
        return False


def install_package():
    print("Instalando tiktok-uploader...")
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           "tiktok-uploader", "--quiet"])
    print("OK\n")


def main():
    # Instala o pacote se necessario
    if not check_package():
        print("Pacote tiktok-uploader nao encontrado. Instalando...\n")
        try:
            install_package()
        except Exception as e:
            print(f"Erro ao instalar: {e}")
            print("Tente manualmente: pip install tiktok-uploader")
            return

    # Verifica se cookies ja existem
    if COOKIES_FILE.exists():
        size = COOKIES_FILE.stat().st_size
        print(f"Arquivo tiktok_cookies.txt encontrado ({size} bytes).")
        resp = input("Quer substituir por um novo? (s/n): ").strip().lower()
        if resp != "s":
            print("\nSetup completo! Teste com: python main.py --upload")
            return

    # Mostra o guia
    print(GUIDE.format(cookies_path=Path.cwd() / "tiktok_cookies.txt"))
    input("Pressione ENTER depois de salvar o arquivo tiktok_cookies.txt...")

    if COOKIES_FILE.exists():
        print(f"\nCookies encontrados ({COOKIES_FILE.stat().st_size} bytes).")
        print("Setup completo! Teste com: python main.py --upload")
    else:
        print("\nArquivo nao encontrado. Tente novamente seguindo o guia acima.")


if __name__ == "__main__":
    main()
