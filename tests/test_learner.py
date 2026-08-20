import json

from nusa_antara import learner
from nusa_antara.knowledge import Knowledge


def test_wiki_fact_memformat_jawaban(monkeypatch):
    class Resp:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps(
                {"type": "standard", "extract": "Krakatau adalah gunung berapi. Detail lain."}
            ).encode("utf-8")

    monkeypatch.setattr(learner.urllib.request, "urlopen", lambda *a, **k: Resp())
    hasil = learner._wiki_fact([])
    assert hasil is not None
    kata, jawaban = hasil
    assert kata == "borobudur"  # topik pertama yang belum ada
    assert jawaban.endswith("(Sumber: Wikipedia)")


def test_wiki_fact_melewati_topik_yang_sudah_ada(monkeypatch):
    monkeypatch.setattr(
        learner.urllib.request,
        "urlopen",
        lambda *a, **k: (_ for _ in ()).throw(OSError("offline")),
    )
    existing = [t.lower() for t in learner._WIKI_TOPICS]
    assert learner._wiki_fact(existing) is None


def test_belajar_fallback_ke_benih(tmp_path, monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.setattr(learner, "_wiki_fact", lambda existing: None)
    k = Knowledge(tmp_path / "p.json")
    hasil = learner.learn_once(k)
    assert "Belajar hal baru" in hasil
