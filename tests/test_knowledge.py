from nusa_antara.knowledge import Knowledge
from nusa_antara.learner import learn_once


def test_pengetahuan_awal_termuat(tmp_path):
    k = Knowledge(tmp_path / "p.json")
    assert len(k.entries) > 0
    assert k.lookup("ceritakan tentang batik") is not None


def test_tambah_dan_cari(tmp_path):
    k = Knowledge(tmp_path / "p.json")
    assert k.add("soto", "Soto adalah sup tradisional Indonesia.")
    assert "Soto" in k.lookup("apa itu soto")
    assert not k.add("soto", "duplikat")  # kata kunci duplikat ditolak


def test_belajar_menambah_entri(tmp_path):
    k = Knowledge(tmp_path / "p.json")
    sebelum = len(k.entries)
    hasil = learn_once(k)
    assert len(k.entries) >= sebelum
    assert hasil


def test_brain_memakai_pengetahuan():
    from nusa_antara import NusaAntara

    ai = NusaAntara()
    if ai.mode == "lokal":
        assert "Rendang" in ai.reply("apa itu rendang")
