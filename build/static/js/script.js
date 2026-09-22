const form = document.getElementById("detect-form");
const codeInput = document.getElementById("code-input");
const fileInput = document.getElementById("file-input");
const fileBadge = document.getElementById("file-badge");
const status = document.getElementById("status");
const resultPanel = document.getElementById("result-panel");

let currentFilename = null;

fileInput?.addEventListener("change", async () => {
  const file = fileInput.files[0];
  if (!file) return;
  currentFilename = file.name;
  fileBadge.hidden = false;
  fileBadge.textContent = file.name;
  codeInput.value = await file.text();
  detect();
});

form?.addEventListener("submit", (event) => {
  event.preventDefault();
  detect();
});

let debounceTimer;
codeInput?.addEventListener("input", () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(detect, 400);
});

async function detect() {
  const code = codeInput.value;
  if (!code.trim()) {
    resultPanel.hidden = true;
    return;
  }

  status.textContent = "detecting…";
  try {
    const response = await fetch("/api/detect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, filename: currentFilename }),
    });
    const data = await response.json();
    renderResult(data);
    status.textContent = "";
  } catch (err) {
    status.textContent = "detection failed — check your connection";
  }
}

function renderResult(data) {
  if (!data.language) {
    resultPanel.hidden = true;
    return;
  }

  const ranked = Object.entries(data.scores).sort((a, b) => b[1] - a[1]);
  const runnerUps = ranked.slice(1, 4).map(([lang]) => lang);
  const reasons = (data.matched_rules[data.language] || []).slice(0, 6);

  resultPanel.innerHTML = `
    <div class="result-top">
      <span class="result-label">${escapeHtml(data.language)}</span>
      <span class="result-confidence">${data.confidence}% confidence</span>
    </div>
    <ul class="rule-chips">
      ${reasons.map((r) => `<li>${escapeHtml(r)}</li>`).join("")}
    </ul>
    ${
      runnerUps.length
        ? `<div class="runner-ups">
             <span class="runner-ups-label">also considered</span>
             ${runnerUps.map((l) => `<span class="runner-up">${escapeHtml(l)}</span>`).join("")}
           </div>`
        : ""
    }
  `;
  resultPanel.hidden = false;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
