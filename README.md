# NUSA ANTARA

Asisten AI berbahasa Indonesia yang bisa langsung berjalan dari repo GitHub ini.

## Fitur

- **Mode lokal** — bekerja tanpa internet/API key (menjawab dengan aturan cerdas, bisa berhitung).
- **Mode LLM** — jika `LLM_API_KEY` diatur, jawaban diberikan oleh model bahasa (endpoint OpenAI-compatible).
- **Belajar tiap 30 menit** — workflow GitHub Actions menambah pengetahuan baru ke `nusa_antara/pengetahuan.json` secara berkala (otomatis commit). Sumber: LLM (jika secret `LLM_API_KEY` ada) → Wikipedia Bahasa Indonesia → benih Nusantara internal.
- **Bot penjawab issue** — setiap issue baru di repo otomatis dijawab NUSA ANTARA lewat komentar (workflow `jawab-issue.yml`).
- **Versi web** — coba langsung di https://antono4.github.io/nusa-antara/ : chat berjalan penuh di browser, plus **login GitHub** (Personal Access Token) untuk memakai API GitHub atas nama akun Anda (lihat repo, buat issue, bintangi repo).
- **Login GitHub di CLI** — `python main.py --login` (OAuth Device Flow, butuh `NUSA_GITHUB_CLIENT_ID` dari OAuth App). Perintah chat: `github siapa`, `github repo`, `github issue <pemilik/repo>`, `github buat issue <pemilik/repo> <judul>`, `github bintangi <pemilik/repo>`.
- **Basis pengetahuan** — fakta-fakta tentang Indonesia/Nusantara yang langsung dipakai untuk menjawab pertanyaan.
- CLI interaktif + mode satu kali jalan (`--once`).
- CI GitHub Actions yang menjalankan tes di setiap push/PR.

## Cara Menjalankan

```bash
git clone <url-repo-ini>
cd <repo>
python main.py            # mode interaktif
python main.py --once "halo, siapa kamu"   # sekali jawab
```

## Mode LLM (opsional)

```bash
export LLM_API_KEY="kunci-api-anda"
export LLM_BASE_URL="https://api.openai.com/v1"   # opsional
export LLM_MODEL="gpt-4o-mini"                    # opsional
python main.py
```

Bisa juga dipakai dengan provider lain yang OpenAI-compatible (OpenRouter, Groq, dsb) cukup dengan mengganti `LLM_BASE_URL` dan `LLM_MODEL`.

## Menjalankan Tes

```bash
pip install -r requirements.txt
pytest -v
```

## Struktur

```
nusa_antara/     # paket utama (brain, llm, cli)
main.py          # entry point
tests/           # unit test
.github/         # workflow CI
```

---

