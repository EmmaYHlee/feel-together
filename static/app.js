// ── EMOTION CONFIG ──────────────────────────────────────────
const EMOTIONS = {
  happy:  { emoji:"😊", color:"#FFD93D", bg:"#FFF9E6", dk:"#B8960A",
            accent:"#f59e0b", accentDark:"#d97706", accentBg:"rgba(245,158,11,.1)", accentRing:"rgba(245,158,11,.18)", accentGrad:"linear-gradient(135deg,#fbbf24,#f59e0b)", accentShadow:"rgba(245,158,11,.4)" },
  sad:    { emoji:"😢", color:"#74B9FF", bg:"#EBF5FF", dk:"#1A6FC4",
            accent:"#2563eb", accentDark:"#1d4ed8", accentBg:"rgba(37,99,235,.1)", accentRing:"rgba(37,99,235,.18)", accentGrad:"linear-gradient(135deg,#1d4ed8,#2563eb)", accentShadow:"rgba(37,99,235,.4)" },
  angry:  { emoji:"😡", color:"#FF6B6B", bg:"#FFF0F0", dk:"#C0392B",
            accent:"#f43f5e", accentDark:"#e11d48", accentBg:"rgba(244,63,94,.1)", accentRing:"rgba(244,63,94,.18)", accentGrad:"linear-gradient(135deg,#f87171,#f43f5e)", accentShadow:"rgba(244,63,94,.4)" },
  boring: { emoji:"😐", color:"#A29BFE", bg:"#F3F2FF", dk:"#6C5CE7",
            accent:"#8b5cf6", accentDark:"#7c3aed", accentBg:"rgba(139,92,246,.1)", accentRing:"rgba(139,92,246,.18)", accentGrad:"linear-gradient(135deg,#a78bfa,#8b5cf6)", accentShadow:"rgba(139,92,246,.4)" },
};

function applyAccent(emotion) {
  const em = EMOTIONS[emotion]; if (!em) return;
  const r = document.documentElement.style;
  r.setProperty("--accent",          em.accent);
  r.setProperty("--accent-dark",     em.accentDark);
  r.setProperty("--accent-bg",       em.accentBg);
  r.setProperty("--accent-ring",     em.accentRing);
  r.setProperty("--accent-gradient", em.accentGrad);
  r.setProperty("--accent-shadow",   em.accentShadow);
}

// ── TYPEWRITER ──────────────────────────────────────────────
const TW_TEXT = "Every emotion has a home here. Every feeling has a face. Every person has someone who gets it.";
let _twTimer = null;
function startTypewriter() {
  const el = document.getElementById("slogan-tw"); if (!el) return;
  el.innerHTML = '<span class="tw-cursor"></span>';
  if (_twTimer) clearTimeout(_twTimer);
  let i = 0;
  function tick() {
    if (i >= TW_TEXT.length) return;
    const ch = TW_TEXT[i++];
    const cur = el.querySelector(".tw-cursor");
    const sp = document.createElement("span"); sp.textContent = ch;
    cur.insertAdjacentElement("beforebegin", sp);
    _twTimer = setTimeout(tick, ".,!?".includes(ch) ? 200 : 40);
  }
  setTimeout(tick, 400);
}

// ── TOAST ───────────────────────────────────────────────────
function showToast(msg, isErr) {
  const t = document.getElementById("toast"); if (!t) return;
  t.textContent = msg;
  t.className = "toast" + (isErr ? " error" : "");
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 2800);
}

// ── API FETCH (session-based, no tokens) ────────────────────
async function apiCall(method, path, body) {
  const opts = { method, headers: { "Content-Type": "application/json" } };
  if (body) opts.body = JSON.stringify(body);
  const res  = await fetch(path, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "Error " + res.status);
  return data;
}
