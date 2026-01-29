/* ──────────────────────────────────────────────────────────
   Molty Dashboard v2 — Frontend
   ────────────────────────────────────────────────────────── */

const STATES = {
  sleeping:  { label: "Sleeping",           color: "#6b7280" },
  thinking:  { label: "Thinking",           color: "#f59e0b" },
  coding:    { label: "Writing Code",       color: "#6c5ce7" },
  searching: { label: "Researching",        color: "#3b82f6" },
  pushing:   { label: "Publishing",         color: "#34d399" },
};

let currentState = "";
let sessionStart = Date.now();
let logBuffer = [];
const MAX_LOGS = 12;

// ── DOM refs ──

const $orb         = document.getElementById("orb");
const $stateLabel  = document.getElementById("state-label");
const $connPill    = document.getElementById("conn-pill");
const $projects    = document.getElementById("stat-projects");
const $commits     = document.getElementById("stat-commits");
const $loc         = document.getElementById("stat-loc");
const $uptime      = document.getElementById("stat-uptime");
const $grid        = document.getElementById("project-grid");
const $feed        = document.getElementById("feed-list");
const $footerTime  = document.getElementById("footer-time");

// ── helpers ──

function fmt(n) {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
  if (n >= 1_000)     return (n / 1_000).toFixed(1) + "k";
  return String(n);
}

function pad(n) { return String(n).padStart(2, "0"); }

function updateUptime() {
  const s = Math.floor((Date.now() - sessionStart) / 1000);
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  $uptime.textContent = h ? `${h}:${pad(m)}:${pad(sec)}` : `${pad(m)}:${pad(sec)}`;
  $footerTime.textContent = new Date().toLocaleTimeString();
}

// ── state ──

function setState(state) {
  if (state === currentState) return;
  const info = STATES[state] || STATES.sleeping;
  currentState = state;

  $orb.className = "orb " + state;
  $stateLabel.textContent = info.label;
  $stateLabel.style.color = info.color;
}

// ── logs ──

function pushLogs(entries) {
  for (const e of entries) {
    logBuffer.unshift({ ...e, time: new Date().toLocaleTimeString() });
  }
  if (logBuffer.length > MAX_LOGS) logBuffer.length = MAX_LOGS;
  renderFeed();
}

function renderFeed() {
  if (!logBuffer.length) {
    $feed.innerHTML = '<li class="feed-empty">Waiting for activity…</li>';
    return;
  }
  $feed.innerHTML = logBuffer
    .map(l => `<li class="${l.type || "info"}"><span class="feed-time">${l.time}</span>${esc(l.message)}</li>`)
    .join("");
}

function esc(s) {
  const d = document.createElement("span");
  d.textContent = s;
  return d.innerHTML;
}

// ── projects gallery ──

async function loadProjects() {
  try {
    const res = await fetch("/api/projects");
    const projects = await res.json();
    if (!projects.length) {
      $grid.innerHTML = '<p style="color:var(--text-2);font-size:.85rem">No projects yet.</p>';
      return;
    }
    $grid.innerHTML = projects.map(p => {
      const href = p.repo || "#";
      const target = p.repo ? ' target="_blank" rel="noopener"' : "";
      return `
        <a class="project-card" href="${esc(href)}"${target}>
          <div class="pc-name">${esc(p.name)}</div>
          <div class="pc-desc">${esc(p.description || p.status || "")}</div>
          <div class="pc-meta">
            ${p.stack ? `<span class="tag">${esc(p.stack)}</span>` : ""}
            ${p.date  ? `<span class="tag">${esc(p.date)}</span>`  : ""}
          </div>
        </a>`;
    }).join("");
  } catch { /* silent */ }
}

// ── stats ──

async function loadStats() {
  try {
    const res = await fetch("/api/stats");
    const s = await res.json();
    $projects.textContent = s.projects ?? "—";
    $commits.textContent  = fmt(s.commits ?? 0);
    $loc.textContent      = fmt(s.loc ?? 0);
  } catch { /* silent */ }
}

// ── status polling ──

async function poll() {
  try {
    const res = await fetch("/api/status");
    const d = await res.json();

    setState(d.state || "sleeping");

    if (d.logs?.length) pushLogs(d.logs);

    $connPill.textContent = "live";
    $connPill.className = "pill live";
  } catch {
    $connPill.textContent = "offline";
    $connPill.className = "pill off";
  }
}

// ── init ──

(function init() {
  setState("sleeping");
  updateUptime();
  setInterval(updateUptime, 1000);

  poll();
  setInterval(poll, 2000);

  loadProjects();
  loadStats();
  // refresh projects + stats every 30s
  setInterval(() => { loadProjects(); loadStats(); }, 30_000);
})();
