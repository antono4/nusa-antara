import json

from nusa_antara import NusaAntara, github_auth


def test_simpan_muat_logout_token(tmp_path):
    p = tmp_path / "t.json"
    github_auth.save_token("tok123", p)
    assert github_auth.load_token(p) == "tok123"
    assert github_auth.logout(p)
    assert github_auth.load_token(p) is None


def test_token_rusak_mengembalikan_none(tmp_path):
    p = tmp_path / "t.json"
    p.write_text("bukan json")
    assert github_auth.load_token(p) is None


def test_perintah_github_tanpa_login():
    ai = NusaAntara()
    jawaban = ai.reply("github repo")
    assert "login" in jawaban.lower()


def test_perintah_github_dengan_login(monkeypatch):
    monkeypatch.setattr(
        github_auth, "current_user",
        lambda token=None: {"login": "antono4", "name": "Anton", "public_repos": 3},
    )
    ai = NusaAntara()
    assert "@antono4" in ai.reply("github siapa")


def test_device_login_alur_lengkap(monkeypatch):
    panggilan = {"n": 0}

    def fake_post(url, data):
        if "device/code" in url:
            return {
                "device_code": "dc",
                "user_code": "ABCD-1234",
                "verification_uri": "https://github.com/login/device",
                "interval": 0,
                "expires_in": 60,
            }
        panggilan["n"] += 1
        if panggilan["n"] == 1:
            return {"error": "authorization_pending"}
        return {"access_token": "token-final"}

    disimpan = {}
    monkeypatch.setattr(github_auth, "_post_form", fake_post)
    monkeypatch.setattr(github_auth, "save_token", lambda t: disimpan.update(token=t))
    assert github_auth.device_login("cid") == "token-final"
    assert disimpan["token"] == "token-final"


def test_github_api_request(monkeypatch):
    from nusa_antara.github_api import GitHubAPI

    class Resp:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps([{"full_name": "antono4/nusa-antara", "stargazers_count": 1}]).encode()

    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: Resp())
    repos = GitHubAPI("t").repo_saya()
    assert repos[0]["full_name"] == "antono4/nusa-antara"
