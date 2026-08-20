"""Aksi API GitHub atas nama pengguna yang sudah login."""

from __future__ import annotations

import json
import urllib.request

_API = "https://api.github.com"


class GitHubAPI:
    def __init__(self, token: str) -> None:
        self.token = token

    def _request(self, method: str, path: str, data: dict | None = None):
        req = urllib.request.Request(
            f"{_API}{path}",
            data=json.dumps(data).encode("utf-8") if data is not None else None,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json",
                "User-Agent": "nusa-antara",
            },
            method=method,
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}

    def repo_saya(self, limit: int = 5) -> list[dict]:
        return self._request("GET", f"/user/repos?sort=updated&per_page={limit}")

    def buat_repo(self, nama: str, private: bool = False, deskripsi: str = "") -> dict:
        return self._request(
            "POST", "/user/repos",
            {"name": nama, "private": private, "description": deskripsi},
        )

    def buat_issue(self, repo: str, judul: str, isi: str = "") -> dict:
        return self._request(
            "POST", f"/repos/{repo}/issues", {"title": judul, "body": isi}
        )

    def daftar_issue(self, repo: str, limit: int = 5) -> list[dict]:
        return self._request("GET", f"/repos/{repo}/issues?state=open&per_page={limit}")

    def bintangi(self, repo: str) -> None:
        self._request("PUT", f"/user/starred/{repo}")

    def notifikasi(self, limit: int = 5) -> list[dict]:
        return self._request("GET", f"/notifications?per_page={limit}")
