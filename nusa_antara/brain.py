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

    @property
    def mode(self) -> str:
        return "llm" if self._llm else "lokal"

    def reply(self, message: str) -> str:
        message = message.strip()
        if not message:
            return "Silakan ketik sesuatu, saya siap mendengarkan."
        if self._llm:
            return self._llm.chat(message)
        return _local_reply(message)
