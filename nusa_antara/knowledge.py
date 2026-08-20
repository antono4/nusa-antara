"""Penyimpanan pengetahuan NUSA ANTARA.

Pengetahuan disimpan dalam berkas JSON (pengetahuan.json) sebagai daftar
entri {kata_kunci, jawaban}. Workflow `learn` menambah entri baru secara
berkala; brain memakai entri ini sebelum jatuh ke jawaban fallback.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

DATA_PATH = Path(__file__).parent / "pengetahuan.json"

# Pengetahuan awal tentang Nusantara; ditambah oleh learner setiap siklus.
_SEED = [
    ("indonesia", "Indonesia adalah negara kepulauan terbesar di dunia dengan lebih dari 17.000 pulau."),
    ("nusantara", "Nusantara adalah istilah untuk kepulauan Indonesia, dan juga nama ibu kota baru Indonesia (IKN)."),
    ("ibu kota", "Ibu kota Indonesia kini adalah IKN Nusantara di Kalimantan Timur, menggantikan Jakarta."),
    ("batik", "Batik adalah kain tradisional Indonesia yang diakui UNESCO sebagai warisan budaya tak benda."),
    ("rendang", "Rendang adalah masakan khas Minangkabau yang pernah dinobatkan sebagai makanan terlezat di dunia versi CNN."),
    ("komodo", "Pulau Komodo di NTT adalah habitat asli komodo, kadal terbesar di dunia."),
    ("borobudur", "Borobudur di Jawa Tengah adalah candi Buddha terbesar di dunia, dibangun abad ke-9."),
    ("raja ampat", "Raja Ampat di Papua adalah surga biodiversitas laut dengan sekitar 75% spesies karang dunia."),
    ("gamelan", "Gamelan adalah ansambel musik tradisional Jawa dan Bali dengan gong, kendang, dan metalofon."),
    ("bahasa daerah", "Indonesia memiliki lebih dari 700 bahasa daerah — salah satu yang terkaya di dunia."),
]


class Knowledge:
    def __init__(self, path: Path = DATA_PATH) -> None:
        self.path = path
        self.entries: list[dict[str, str]] = []
        self.load()

    def load(self) -> None:
        if self.path.exists():
            try:
                self.entries = json.loads(self.path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self.entries = []
        if not self.entries:
            self.entries = [{"kata": k, "jawaban": j} for k, j in _SEED]
            self.save()

    def save(self) -> None:
        self.path.write_text(
            json.dumps(self.entries, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def lookup(self, message: str) -> str | None:
        text = message.lower()
        for entri in self.entries:
            kata = entri.get("kata", "").lower()
            if kata and kata in text:
                return entri["jawaban"]
        return None

    def add(self, kata: str, jawaban: str) -> bool:
        kata = kata.strip().lower()
        if not kata or any(e.get("kata", "").lower() == kata for e in self.entries):
            return False
        self.entries.append({"kata": kata, "jawaban": jawaban})
        self.save()
        return True
