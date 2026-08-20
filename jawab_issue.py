"""Bot penjawab issue: dipanggil dari GitHub Actions saat issue dibuat.

Membaca judul+isi issue dari event payload, menjawab dengan NUSA ANTARA
(LLM jika ada kunci, kalau tidak pakai basis pengetahuan), lalu memposting
jawaban sebagai komentar melalui GitHub API.
"""

from __future__ import annotations

import json
import os
import urllib.request

from nusa_antara import NusaAntara


def post_comment(repo: str, issue_number: int, body: str, token: str) -> None:
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments",
        data=json.dumps({"body": body}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        resp.read()


def main() -> None:
    event_path = os.environ["GITHUB_EVENT_PATH"]
    repo = os.environ["GITHUB_REPOSITORY"]
    token = os.environ["GITHUB_TOKEN"]

    with open(event_path, encoding="utf-8") as f:
        event = json.load(f)

    issue = event["issue"]
    pertanyaan = f"{issue.get('title', '')}\n\n{issue.get('body', '') or ''}".strip()
    if not pertanyaan:
        return

    ai = NusaAntara()
    jawaban = ai.reply(pertanyaan)
    body = (
        f"🤖 **NUSA ANTARA** (mode {ai.mode}) menjawab:\n\n"
        f"{jawaban}\n\n"
        "---\n_Jawaban ini dibuat otomatis oleh AI NUSA ANTARA._"
    )
    post_comment(repo, issue["number"], body, token)
    print(f"Komentar terkirim ke issue #{issue['number']}")


if __name__ == "__main__":
    main()
