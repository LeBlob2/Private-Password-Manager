const API = "http://localhost:5000";

const screenLogin   = document.getElementById("screen-login");
const screenEntries = document.getElementById("screen-entries");
const dbSelect      = document.getElementById("db-select");
const inputPassword = document.getElementById("input-password");
const btnUnlock     = document.getElementById("btn-unlock");
const loginError    = document.getElementById("login-error");
const dbLabel       = document.getElementById("db-label");
const btnLock       = document.getElementById("btn-lock");
const inputSearch   = document.getElementById("input-search");
const entriesList   = document.getElementById("entries-list");

let currentDb  = null;
let allEntries = [];

function saveSession(db_name) {
  sessionStorage.setItem("unlocked_db", db_name);
}

function clearSession() {
  sessionStorage.removeItem("unlocked_db");
}

function getSavedSession() {
  return sessionStorage.getItem("unlocked_db");
}


async function init() {
  try {
    const res = await fetch(`${API}/databases`);
    const dbs = await res.json();
    dbSelect.innerHTML = dbs.length
      ? dbs.map(d => `<option value="${d}">${d}</option>`).join("")
      : `<option disabled>No databases found</option>`;
  } catch {
    loginError.textContent = "Cannot reach API — is api.py running?";
    btnUnlock.disabled = true;
    return;
  }

  const saved = getSavedSession();
  if (saved) {
    const res = await fetch(`${API}/fetch?db_name=${encodeURIComponent(saved)}`);
    if (res.ok) {
      currentDb  = saved;
      allEntries = await res.json();
      dbLabel.textContent = currentDb;
      renderEntries(allEntries);
      showScreen("entries");
      return;
    }
    clearSession();
  }

  showScreen("login");
}

btnUnlock.addEventListener("click", async () => {
  loginError.textContent = "";
  const db_name  = dbSelect.value;
  const password = inputPassword.value;

  if (!password) { loginError.textContent = "Enter your master password."; return; }

  try {
    const res  = await fetch(`${API}/unlock`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ db_name, password })
    });
    const data = await res.json();

    if (!res.ok) { loginError.textContent = data.error || "Wrong password."; return; }

    currentDb = db_name;
    saveSession(db_name);
    inputPassword.value = "";
    await loadEntries();
    showScreen("entries");
  } catch {
    loginError.textContent = "Could not connect to API.";
  }
});

inputPassword.addEventListener("keydown", e => { if (e.key === "Enter") btnUnlock.click(); });

async function loadEntries() {
  const res  = await fetch(`${API}/fetch?db_name=${encodeURIComponent(currentDb)}`);
  allEntries = await res.json();
  dbLabel.textContent = currentDb;
  renderEntries(allEntries);
}

function renderEntries(entries) {
  if (!entries.length) {
    entriesList.innerHTML = `<p class="no-results">No entries found.</p>`;
    return;
  }

  entriesList.innerHTML = entries.map((e, i) => `
    <div class="entry-card">
      <div class="entry-website">${esc(e.website)}</div>

      <div class="entry-row">
        <span class="entry-key">Username</span>
        <span class="entry-val">${esc(e.username)}</span>
        <button class="btn-copy" data-val="${esc(e.username)}">Copy</button>
      </div>

      <div class="entry-row">
        <span class="entry-key">Email</span>
        <span class="entry-val">${esc(e.email)}</span>
        <button class="btn-copy" data-val="${esc(e.email)}">Copy</button>
      </div>

      <div class="entry-row">
        <span class="entry-key">Password</span>
        <span class="entry-val masked" id="pw-${i}" data-plain="${esc(e.password)}">••••••••</span>
        <button class="btn-toggle" data-target="pw-${i}">Show</button>
        <button class="btn-copy" data-val="${esc(e.password)}">Copy</button>
      </div>
    </div>
  `).join("");

  entriesList.querySelectorAll(".btn-copy").forEach(btn => {
    btn.addEventListener("click", () => {
      navigator.clipboard.writeText(btn.dataset.val);
      btn.textContent = "✓";
      btn.classList.add("copied");
      setTimeout(() => { btn.textContent = "Copy"; btn.classList.remove("copied"); }, 1500);
    });
  });

  entriesList.querySelectorAll(".btn-toggle").forEach(btn => {
    btn.addEventListener("click", () => {
      const span  = document.getElementById(btn.dataset.target);
      const shown = btn.textContent === "Hide";
      span.textContent = shown ? "••••••••" : span.dataset.plain;
      span.classList.toggle("masked", shown);
      btn.textContent  = shown ? "Show" : "Hide";
    });
  });
}

inputSearch.addEventListener("input", () => {
  const q = inputSearch.value.toLowerCase();
  renderEntries(
    allEntries.filter(e =>
      e.website.toLowerCase().includes(q)  ||
      e.username.toLowerCase().includes(q) ||
      e.email.toLowerCase().includes(q)
    )
  );
});

btnLock.addEventListener("click", async () => {
  await fetch(`${API}/lock`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ db_name: currentDb })
  });
  clearSession();
  currentDb  = null;
  allEntries = [];
  entriesList.innerHTML = "";
  inputSearch.value     = "";
  showScreen("login");
});

function showScreen(name) {
  screenLogin.classList.toggle("hidden",   name !== "login");
  screenEntries.classList.toggle("hidden", name !== "entries");
}

function esc(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

init();