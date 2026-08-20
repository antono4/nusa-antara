"""Antarmuka baris perintah (CLI) untuk NUSA ANTARA."""

from __future__ import annotations

import sys

from .brain import NusaAntara

BANNER = r"""
 _   _ _   _ ____    _      _    _   _ _____  _    ____      _
| \ | | | | / ___|  / \    / \  | \ | |_   _|/ \  |  _ \    / \
|  \| | | | \___ \ / _ \  / _ \ |  \| | | | / _ \ | |_) |  / _ \
| |\  | |_| |___) / ___ \/ ___ \| |\  | | |/ ___ \|  _ <  / ___ \
|_| \_|\___/|____/_/   \_/_/   \_\_| \_| |_/_/   \_\_| \_\/_/   \_\
        Asisten AI dari Nusantara, untuk Nusantara.
"""


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    ai = NusaAntara()

    if argv and argv[0] in {"--once", "-o"}:
        pesan = " ".join(argv[1:])
        print(ai.reply(pesan) if pesan else "Tambahkan pertanyaan setelah --once")
        return 0

    print(BANNER)
    print(f"Mode: {ai.mode}. Ketik 'keluar' untuk berhenti.\n")
    while True:
        try:
            pesan = input("Anda: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSampai jumpa!")
            break
        if pesan.lower() in {"keluar", "exit", "quit"}:
            print("NUSA ANTARA: Sampai jumpa!")
            break
        if pesan:
            print(f"NUSA ANTARA: {ai.reply(pesan)}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
