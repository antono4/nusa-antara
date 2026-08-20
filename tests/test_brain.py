from nusa_antara import NusaAntara


def test_sapaan_dijawab():
    ai = NusaAntara()
    jawaban = ai.reply("halo")
    assert "NUSA ANTARA" in jawaban or "Halo" in jawaban or "Hai" in jawaban


def test_identitas():
    ai = NusaAntara()
    assert "NUSA ANTARA" in ai.reply("siapa kamu")


def test_hitung():
    ai = NusaAntara()
    assert "56" in ai.reply("hitung 7 * 8")


def test_input_kosong():
    ai = NusaAntara()
    assert ai.reply("   ") != ""


def test_mode_lokal_tanpa_api_key():
    ai = NusaAntara()
    assert ai.mode in {"lokal", "llm"}
