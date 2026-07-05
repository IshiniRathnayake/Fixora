const API_BASE = "http://localhost:8000";

const $ = (id) => document.getElementById(id);

function show(id) {
  ["login-section", "main-section", "result-section", "loading-section"].forEach((s) => {
    $(s).classList.toggle("hidden", s !== id);
  });
}

async function getPageContext() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id) return {};
  try {
    const response = await chrome.tabs.sendMessage(tab.id, { type: "GET_CONTEXT" });
    return { ...response, tabUrl: tab.url, tabTitle: tab.title };
  } catch {
    return { page_url: tab.url, page_title: tab.title };
  }
}

async function login(email, password) {
  const body = new URLSearchParams({ username: email, password });
  const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!res.ok) throw new Error("Invalid credentials");
  const data = await res.json();
  await chrome.storage.local.set({ fixora_token: data.access_token, fixora_email: email });
  return data.access_token;
}

async function analyzeIssue(token, description, context) {
  const payload = {
    description,
    source: "extension",
    page_url: context.page_url || context.tabUrl,
    page_title: context.page_title || context.tabTitle,
    page_error: context.page_error,
    browser: navigator.userAgent.split(" ").pop(),
    os_info: navigator.platform,
    selected_text: context.selected_text,
  };
  const res = await fetch(`${API_BASE}/api/v1/support/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || "Analysis failed");
  }
  return res.json();
}

function renderContext(ctx) {
  const parts = [];
  if (ctx.page_title || ctx.tabTitle) parts.push(`Page: ${ctx.page_title || ctx.tabTitle}`);
  if (ctx.page_url || ctx.tabUrl) parts.push(`URL: ${(ctx.page_url || ctx.tabUrl || "").slice(0, 60)}…`);
  if (ctx.page_error) parts.push(`Error: ${ctx.page_error}`);
  $("page-context").textContent = parts.length ? parts.join("\n") : "No page context captured.";
}

function renderResult(data) {
  const res = data.resolution || {};
  $("result-summary").innerHTML = `<strong>${res.summary || "Analysis complete"}</strong>` +
    (res.likely_cause ? `<br><span style="color:#8b9bb0">Cause: ${res.likely_cause}</span>` : "");

  const stepsEl = $("result-steps");
  stepsEl.innerHTML = "";
  (res.steps || []).forEach((step) => {
    const li = document.createElement("li");
    li.textContent = step;
    stepsEl.appendChild(li);
  });

  $("result-meta").textContent =
    `Category: ${data.category} | Priority: ${data.priority} | Confidence: ${Math.round((data.confidence || 0) * 100)}%`;

  const ticketEl = $("ticket-info");
  if (data.ticket) {
    ticketEl.classList.remove("hidden");
    ticketEl.textContent = `IT Ticket #${data.ticket.id} created — ${data.ticket.title}`;
  } else {
    ticketEl.classList.add("hidden");
  }

  const agentList = $("agent-list");
  agentList.innerHTML = "";
  (data.workflow?.agents || []).forEach((a) => {
    const li = document.createElement("li");
    li.textContent = `${a.agent} (${a.duration_ms}ms) — ${a.status}`;
    agentList.appendChild(li);
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  const stored = await chrome.storage.local.get(["fixora_token", "fixora_email"]);
  let pageContext = await getPageContext();

  if (stored.fixora_token) {
    show("main-section");
    renderContext(pageContext);
    if (stored.fixora_email) $("email").value = stored.fixora_email;
  } else {
    show("login-section");
  }

  $("login-btn").addEventListener("click", async () => {
    const email = $("email").value.trim();
    const password = $("password").value;
    $("login-error").classList.add("hidden");
    try {
      await login(email, password);
      pageContext = await getPageContext();
      renderContext(pageContext);
      show("main-section");
    } catch {
      $("login-error").textContent = "Login failed. Use admin@fixora.local / admin123";
      $("login-error").classList.remove("hidden");
    }
  });

  $("logout-btn").addEventListener("click", async () => {
    await chrome.storage.local.remove(["fixora_token", "fixora_email"]);
    show("login-section");
  });

  $("analyze-btn").addEventListener("click", async () => {
    const description = $("issue").value.trim();
    if (description.length < 5) return;
    const { fixora_token } = await chrome.storage.local.get("fixora_token");
    if (!fixora_token) { show("login-section"); return; }

    show("loading-section");
    try {
      pageContext = await getPageContext();
      const result = await analyzeIssue(fixora_token, description, pageContext);
      renderResult(result);
      show("result-section");
    } catch (err) {
      show("main-section");
      alert(err.message || "Analysis failed. Is the API running on localhost:8000?");
    }
  });

  $("back-btn").addEventListener("click", () => {
    $("issue").value = "";
    show("main-section");
  });
});
