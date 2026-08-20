"""Klien LLM OpenAI-compatible untuk NUSA ANTARA.

Konfigurasi via variabel lingkungan:
- LLM_API_KEY   : kunci API (wajib untuk mode LLM)
- LLM_BASE_URL  : default https://api.openai.com/v1
- LLM_MODEL     : default gpt-4o-mini
"""

from __future__ import annotations

import json
import os
import urllib.request

from .brain import SYSTEM_PROMPT


class LLMClient:
    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    @classmethod
    def from_env(cls) -> "LLMClient":
        api_key = os.environ.get("LLM_API_KEY", "").strip()
        if not api_key:
            raise ValueError("LLM_API_KEY tidak diatur")
        return cls(
            api_key=api_key,
            base_url=os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1"),
            model=os.environ.get("LLM_MODEL", "gpt-4o-mini"),
        )

    def chat(self, message: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
        }
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
        except Exception as exc:
            return f"[mode LLM gagal: {exc}] Sementara saya berjalan dalam mode lokal."
