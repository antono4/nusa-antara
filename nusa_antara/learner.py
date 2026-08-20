"""Pembelajar berkala NUSA ANTARA.

Strategi (dilakukan sekali per siklus, mis. tiap 30 menit dari CI):
1. Jika LLM_API_KEY tersedia: minta model menambahkan satu fakta Nusantara
   baru yang belum ada di penyimpanan.
2. Tanpa API key: ambil satu fakta dari paket benih internal yang belum
   dipakai (sumber _SEED_EXPAND), sehingga pengetahuan tetap bertambah.
3. Batasi ukuran penyimpanan (MAX_ENTRIES) agar repo tidak membengkak.
"""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

from .knowledge import DATA_PATH, Knowledge
from .brain import SYSTEM_PROMPT

MAX_ENTRIES = 500

_SEED_EXPAND = [
    ("wayang", "Wayang kulit adalah seni pertunjukan tradisional Jawa yang diakui UNESCO."),
    ("angklung", "Angklung adalah alat musik bambu khas Sunda, Jawa Barat."),
    ("danau toba", "Danau Toba di Sumatera Utara adalah danau vulkanik terbesar di dunia."),
    ("pencak silat", "Pencak silat adalah bela diri tradisional Indonesia yang diakui UNESCO."),
    ("kopi luwak", "Kopi luwak adalah salah satu kopi termahal di dunia dari Indonesia."),
    ("candi prambanan", "Prambanan adalah kompleks candi Hindu terbesar di Indonesia, abad ke-9."),
    ("tari saman", "Tari Saman dari Aceh diakui UNESCO sebagai warisan budaya tak benda."),
    ("keris", "Keris adalah senjata tradisional Indonesia yang diakui UNESCO sebagai karya agung."),
    ("wakatobi", "Wakatobi di Sulawesi Tenggara dikenal sebagai salah satu lokasi selam terbaik dunia."),
    ("noken", "Noken adalah tas tradisional Papua yang diakui UNESCO."),
]


def _llm_fact(missing_keywords: list[str]) -> tuple[str, str] | None:
    api_key = os.environ.get("LLM_API_KEY", "").strip()
    if not api_key:
        return None
    base = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("LLM_MODEL", "gpt-4o-mini")
    prompt = (
        "Berikan SATU fakta menarik tentang Nusantara/Indonesia yang belum ada "
        f"dalam daftar ini: {missing_keywords[:50]}. "
        'Jawab hanya JSON: {"kata": "kata kunci pendek", "jawaban": _fakta singkat_"}'
    )
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    }
    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        content = data["choices"][0]["message"]["content"]
        fact = json.loads(content.strip().strip("`").replace("json\n", ""))
        return fact["kata"], fact["jawaban"]
    except Exception:
        return None


def learn_once(knowledge: Knowledge | None = None) -> str:
    knowledge = knowledge or Knowledge(DATA_PATH)
    if len(knowledge.entries) >= MAX_ENTRIES:
        return "Penyimpanan penuh ({} entri). Belajar dihentikan.".format(MAX_ENTRIES)

    existing = [e["kata"] for e in knowledge.entries]

    fact = _llm_fact(existing)
    if fact is None:
        for kata, jawaban in _SEED_EXPAND:
            if kata not in existing:
                fact = (kata, jawaban)
                break

    if fact is None:
        return "Tidak ada fakta baru untuk dipelajari."

    kata, jawaban = fact
    if knowledge.add(kata, jawaban):
        return f"Belajar hal baru: {kata} → {jawaban}"
    return "Fakta sudah dikenal."
