/* NUSA ANTARA versi web — berjalan penuh di browser.
   Mesin lokal (aturan + basis pengetahuan) + perintah GitHub via API
   memakai token milik pengguna yang disimpan di localStorage. */

const chat = document.getElementById("chat");
const msgInput = document.getElementById("msg");

function tambah(teks, siapa) {
  const d = document.createElement("div");
  d.className = "msg " + siapa;
  d.textContent = teks;
  chat.appendChild(d);
  chat.scrollTop = chat.scrollHeight;
}

const getToken = () => localStorage.getItem("nusa_gh_token");
let ghUser = JSON.parse(localStorage.getItem("nusa_gh_user") || "null");

const ATURAN = [
  [/\b(halo|hai|hei|hello|selamat (pagi|siang|sore|malam))\b/i,
   ["Halo! Saya NUSA ANTARA, asisten AI Anda. Ada yang bisa saya bantu?",
    "Hai! NUSA ANTARA siap membantu. Silakan ajukan pertanyaan Anda."]],
  [/siapa (kamu|anda)|nama (kamu|mu)|perkenalkan/i,
   ["Saya NUSA ANTARA — asisten AI dari Nusantara. Versi web ini berjalan sepenuhnya di browser Anda, dan bisa memakai API GitHub atas nama akun Anda setelah login."]],
  [/\b(terima kasih|makasih|thanks)\b/i, ["Sama-sama! Senang bisa membantu."]],
  [/\b(bisa apa|fitur|kemampuan)\b/i,
   ["Saya bisa mengobrol, menjawab pengetahuan Nusantara, berhitung, dan menjalankan perintah GitHub (coba: 'github repo'). Login GitHub untuk fitur akun."]],
];

function jawabLokal(pesan) {
  const t = pesan.toLowerCase();
  const calc = t.match(/^\s*(hitung|kalkulasi)\s+([0-9+\-*/ ().]+)\s*$/);
  if (calc) {
    try { return `Hasil dari ${calc[2]} adalah ${Function(`return (${calc[2]})`)()}.`; }
    catch { return "Maaf, ekspresi perhitungannya tidak valid."; }
  }
  for (const e of PENGETAHUAN) {
    if (e.kata && t.includes(e.kata.toLowerCase())) return e.jawaban;
  }
  for (const [pola, jawaban] of ATURAN) {
    if (pola.test(t)) return jawaban[Math.floor(Math.random() * jawaban.length)];
  }
  return "Saya masih belajar hal itu. Coba tanya tentang Nusantara, atau jalankan perintah GitHub seperti 'github repo'.";
}

async function gh(path, method = "GET", body = null) {
  const res = await fetch("https://api.github.com" + path, {
    method,
    headers: {
      Authorization: "Bearer " + getToken(),
      Accept: "application/vnd.github+json",
    },
    body: body ? JSON.stringify(body) : null,
  });
  if (!res.ok) throw new Error("GitHub " + res.status);
  return res.status === 204 ? {} : res.json();
}

async function jawabGitHub(pesan) {
  if (!getToken()) {
    return "Anda belum login GitHub. Klik tombol 'Masuk dengan GitHub' di kanan atas dulu ya.";
  }
  const t = pesan.trim();
  const low = t.toLowerCase();
  try {
    if (["github", "github siapa", "github akun", "github profil"].includes(low)) {
      return `Anda login sebagai @${ghUser.login} (${ghUser.name || "-"}, ${ghUser.public_repos} repo publik).`;
    }
    if (low === "github repo") {
      const repos = await gh("/user/repos?sort=updated&per_page=5");
      return "Repo terbaru Anda:\n" + repos.map(r => `- ${r.full_name} (⭐ ${r.stargazers_count})`).join("\n");
    }
    let m = low.match(/^github issue(?: di)? (\S+)$/);
    if (m) {
      const issues = await gh(`/repos/${m[1]}/issues?state=open&per_page=5`);
      if (!issues.length) return `Tidak ada issue terbuka di ${m[1]}.`;
      return `Issue terbuka di ${m[1]}:\n` + issues.map(i => `- #${i.number}: ${i.title}`).join("\n");
    }
    m = low.match(/^github bintangi (\S+)$/);
    if (m) { await gh(`/user/starred/${m[1]}`, "PUT"); return `⭐ ${m[1]} berhasil dibintangi.`; }
    m = t.match(/^github buat issue (\S+) (.+)$/i);
    if (m) {
      const i = await gh(`/repos/${m[1]}/issues`, "POST", { title: m[2] });
      return `Issue dibuat: ${i.html_url}`;
    }
    return "Perintah GitHub:\n- github siapa\n- github repo\n- github issue <pemilik/repo>\n- github buat issue <pemilik/repo> <judul>\n- github bintangi <pemilik/repo>";
  } catch (e) {
    return "Permintaan GitHub gagal: " + e.message + ". Token mungkin kedaluwarsa — coba login ulang.";
  }
}

async function jawab(pesan) {
  if (pesan.toLowerCase().startsWith("github")) return jawabGitHub(pesan);
  return jawabLokal(pesan);
}

async function kirim() {
  const t = msgInput.value.trim();
  if (!t) return;
  msgInput.value = "";
  tambah(t, "me");
  tambah(await jawab(t), "ai");
}

function renderLogin() {
  const area = document.getElementById("loginArea");
  if (ghUser) {
    area.innerHTML = `<span style="margin-right:8px;color:var(--muted)">@${ghUser.login}</span>` +
      `<button class="ghost" id="logoutBtn">Keluar</button>`;
    document.getElementById("logoutBtn").onclick = () => {
      localStorage.removeItem("nusa_gh_token");
      localStorage.removeItem("nusa_gh_user");
      ghUser = null; renderLogin();
      tambah("Anda sudah keluar dari GitHub.", "sys");
    };
  } else {
    area.innerHTML = `<button id="loginBtn">Masuk dengan GitHub</button>`;
    document.getElementById("loginBtn").onclick = () => loginDialog.showModal();
  }
}

document.getElementById("patOk").onclick = async () => {
  const token = document.getElementById("pat").value.trim();
  if (!token) return;
  localStorage.setItem("nusa_gh_token", token);
  try {
    ghUser = await gh("/user");
    localStorage.setItem("nusa_gh_user", JSON.stringify(ghUser));
    loginDialog.close();
    renderLogin();
    tambah(`✅ Berhasil masuk sebagai @${ghUser.login}. Coba: github repo`, "sys");
  } catch {
    localStorage.removeItem("nusa_gh_token");
    tambah("Token tidak valid. Periksa kembali token Anda.", "sys");
  }
};

document.getElementById("send").onclick = kirim;
msgInput.addEventListener("keydown", e => e.key === "Enter" && kirim());
document.querySelectorAll(".chip").forEach(c => c.onclick = () => { msgInput.value = c.dataset.q; kirim(); });

renderLogin();
tambah("Halo! Saya NUSA ANTARA — asisten AI dari Nusantara. Tanya saya tentang budaya Indonesia, atau login GitHub untuk mengelola akun Anda lewat chat.", "ai");
