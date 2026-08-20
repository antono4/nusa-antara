"""Login GitHub untuk NUSA ANTARA via OAuth Device Flow.

Cara kerja: CLI menampilkan kode + URL, pengguna membukanya di browser dan
menyetujui akses; token disimpan lokal di ~/.nusa_antara_token.json.
Token dipakai untuk memanggil API GitHub atas nama pemilik akun.

Client ID diambil dari variabel lingkungan NUSA_GITHUB_CLIENT_ID
(OAuth App yang dibuat pemilik repo). Device Flow tidak butuh client secret.
"""

from __future__ import annotations

import json
import os
import time
import urllib.request
from pathlib import Path

TOKEN_PATH = Path.home() / ".nusa_antara_token.json"

_DEVICE_URL = "https://github.com/login/device/code"
_TOKEN_URL = "https://github.com/login/oauth/access_token"
_API_USER = "https://api.github.com/user"


def _post_form(url: str, data: dict) -> dict:
    body = "&".join(f"{k}={v}" for k, v in data.items()).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def save_token(token: str, path: Path = TOKEN_PATH) -> None:
    path.write_text(json.dumps({"access_token": token}), encoding="utf-8")
    os.chmod(path, 0o600)


def load_token(path: Path = TOKEN_PATH) -> str | None:
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("access_token")
    except (OSError, json.JSONDecodeError):
        return None


def logout(path: Path = TOKEN_PATH) -> bool:
    try:
        path.unlink()
        return True
    except OSError:
        return False


def current_user(token: str | None = None) -> dict | None:
    token = token or load_token()
    if not token:
        return None
    req = urllib.request.Request(
        _API_USER,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "nusa-antara",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def device_login(client_id: str, scope: str = "repo read:user") -> str:
    """Jalankan OAuth Device Flow dan kembalikan access token."""
    kode = _post_form(_DEVICE_URL, {"client_id": client_id, "scope": scope})
    if "device_code" not in kode:
        raise RuntimeError(f"GitHub menolak permintaan: {kode}")

    print(f"\n🔐 Login GitHub — buka: {kode['verification_uri']}")
    print(f"   Lalu masukkan kode: {kode['user_code']}\n")

    batas = time.time() + int(kode.get("expires_in", 900))
    interval = int(kode.get("interval", 5))
    while time.time() < batas:
        hasil = _post_form(
            _TOKEN_URL,
            {
                "client_id": client_id,
                "device_code": kode["device_code"],
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            },
        )
        if "access_token" in hasil:
            save_token(hasil["access_token"])
            return hasil["access_token"]
        err = hasil.get("error")
        if err == "authorization_pending":
            time.sleep(interval)
        elif err == "slow_down":
            interval += 5
            time.sleep(interval)
        else:
            raise RuntimeError(f"Login gagal: {err}")
    raise RuntimeError("Waktu login habis. Coba lagi.")


def client_id_from_env() -> str | None:
    cid = os.environ.get("NUSA_GITHUB_CLIENT_ID", "").strip()
    return cid or None
