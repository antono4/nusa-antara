"""Mesin respons NUSA ANTARA.

Dua mode:
1. Mode lokal (aturan sederhana) - bekerja tanpa koneksi internet/API key.
2. Mode LLM - jika variabel lingkungan LLM_API_KEY tersedia, jawaban
   diberikan oleh model bahasa melalui endpoint OpenAI-compatible.
"""

from __future__ import annotations

import random
import re

SYSTEM_PROMPT = (
    "Kamu adalah NUSA ANTARA, asisten AI berbahasa Indonesia yang ramah, "
    "ringkas, dan membantu. Jawab dalam bahasa Indonesia kecuali pengguna "
    "meminta bahasa lain."
)

_RULES: list[tuple[str, list[str]]] = [
    (
        r"\b(halo|hai|hei|hello|selamat (pagi|siang|sore|malam))\b",
        [
            "Halo! Saya NUSA ANTARA, asisten AI Anda. Ada yang bisa saya bantu?",
            "Hai! NUSA ANTARA siap membantu. Silakan ajukan pertanyaan Anda.",
        ],
    ),
    (
        r"siapa (kamu|anda)|nama (kamu|mu)|perkenalkan",
        [
            "Saya NUSA ANTARA — asisten AI yang berjalan langsung dari repo "
            "GitHub ini. Saya bisa menjawab pertanyaan dan membantu tugas "
            "sehari-hari Anda."
        ],
    ),
    (
        r"\b(terima kasih|makasih|thanks)\b",
        ["Sama-sama! Senang bisa membantu.", "Dengan senang hati!"],
    ),
    (
        r"\b(bisa apa|fitur|kemampuan)\b",
        [
            "Saya bisa mengobrol, menjawab pertanyaan, dan jika Anda memberi "
            "kunci API LLM, saya akan menjawab dengan kecerdasan penuh. "
            "Coba jalankan: python main.py"
        ],
    ),
    (
        r"\b(bye|selamat tinggal|sampai jumpa|keluar|exit)\b",
        ["Sampai jumpa! NUSA ANTARA pamit."],
    ),
]

_FALLBACK = [
    "Menarik! Bisa jelaskan lebih detail agar saya paham maksud Anda?",
    "Saya masih belajar. Coba gunakan kata lain, atau atur LLM_API_KEY "
    "agar saya bisa menjawab lebih pintar.",
    "Baik, saya catat. Ada hal lain yang bisa saya bantu?",
]


def _local_reply(message: str) -> str:
    text = message.lower()
    calc = re.match(r"^\s*(hitung|kalkulasi)\s+([0-9+\-*/ ().]+)\s*$", text)
    if calc:
        expr = calc.group(2)
        try:
            # Hanya angka dan operator yang lolos regex di atas.
            hasil = eval(expr, {"__builtins__": {}}, {})
            return f"Hasil dari {expr} adalah {hasil}."
        except Exception:
            return "Maaf, ekspresi perhitungannya tidak valid."

    for pattern, replies in _RULES:
        if re.search(pattern, text):
            return random.choice(replies)
    return random.choice(_FALLBACK)


class NusaAntara:
    """Kelas utama AI NUSA ANTARA."""

    def __init__(self) -> None:
        self._llm = None
        try:
            from .llm import LLMClient

            self._llm = LLMClient.from_env()
        except Exception:
            self._llm = None
        try:
            from .knowledge import Knowledge

            self._knowledge = Knowledge()
        except Exception:
            self._knowledge = None

    @property
    def mode(self) -> str:
        return "llm" if self._llm else "lokal"

    def _github_user(self):
        try:
            from .github_auth import current_user

            return current_user()
        except Exception:
            return None

    def _github_command(self, message: str) -> str | None:
        from . import github_auth, github_api

        text = message.strip()
        low = text.lower()
        if not low.startswith("github"):
            return None

        user = self._github_user()
        if not user:
            return (
                "Anda belum login GitHub. Jalankan: python main.py --login "
                "(butuh NUSA_GITHUB_CLIENT_ID dari OAuth App)."
            )
        api = github_api.GitHubAPI(github_auth.load_token())

        try:
            if low in {"github", "github siapa", "github akun", "github profil"}:
                return (
                    f"Anda login sebagai @{user['login']} "
                    f"({user.get('name') or '-'}, {user.get('public_repos', 0)} repo publik)."
                )
            if low == "github repo":
                repos = api.repo_saya()
                baris = [f"- {r['full_name']} (⭐ {r['stargazers_count']})" for r in repos]
                return "Repo terbaru Anda:\n" + "\n".join(baris)
            m = re.match(r"github issue(?:\s+di)?\s+(\S+)$", low)
            if m:
                issues = api.daftar_issue(m.group(1))
                if not issues:
                    return f"Tidak ada issue terbuka di {m.group(1)}."
                baris = [f"- #{i['number']}: {i['title']}" for i in issues]
                return f"Issue terbuka di {m.group(1)}:\n" + "\n".join(baris)
            m = re.match(r"github bintangi\s+(\S+)$", low)
            if m:
                api.bintangi(m.group(1))
                return f"⭐ Repo {m.group(1)} berhasil dibintangi atas nama @{user['login']}."
            m = re.match(r"github buat issue\s+(\S+)\s+(.+)$", text, re.IGNORECASE)
            if m:
                issue = api.buat_issue(m.group(1), m.group(2))
                return f"Issue dibuat: {issue['html_url']}"
            return (
                "Perintah GitHub yang tersedia:\n"
                "- github siapa\n- github repo\n- github issue <pemilik/repo>\n"
                "- github buat issue <pemilik/repo> <judul>\n- github bintangi <pemilik/repo>"
            )
        except Exception as exc:
            return f"Permintaan GitHub gagal: {exc}"

    def reply(self, message: str) -> str:
        message = message.strip()
        if not message:
            return "Silakan ketik sesuatu, saya siap mendengarkan."
        if message.lower().startswith("github"):
            jawaban = self._github_command(message)
            if jawaban:
                return jawaban
        if self._llm:
            return self._llm.chat(message)
        if self._knowledge:
            jawaban = self._knowledge.lookup(message)
            if jawaban:
                return jawaban
        return _local_reply(message)
