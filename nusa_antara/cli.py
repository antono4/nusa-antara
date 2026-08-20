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


def _login() -> int:
    from .github_auth import client_id_from_env, current_user, device_login

    cid = client_id_from_env()
    if not cid:
        print(
            "Atur NUSA_GITHUB_CLIENT_ID terlebih dahulu.\n"
            "Buat OAuth App di https://github.com/settings/developers dengan "
            "Device Flow aktif, lalu: export NUSA_GITHUB_CLIENT_ID=<client_id>"
        )
        return 1
    token = device_login(cid)
    user = current_user(token)
    print(f"✅ Berhasil login sebagai @{user['login']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    ai = NusaAntara()

    if argv and argv[0] == "--login":
        return _login()
    if argv and argv[0] == "--logout":
        from .github_auth import logout

        print("Logout berhasil." if logout() else "Anda memang belum login.")
        return 0
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
