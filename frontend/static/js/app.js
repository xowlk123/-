/**
 * 庭长阅核系统 – Frontend Application
 */

/* ── State ─────────────────────────────── */
let currentFile = null;
let currentReportMd = "";
let activeTab = "file-tab";
let loadingTimer = null;

/* ── Init ───────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
  // Init Mermaid
  mermaid.initialize({
    startOnLoad: false,
    theme: "neutral",
    securityLevel: "loose",
    fontFamily: '"PingFang SC", "Microsoft YaHei", sans-serif',
  });

  // Init marked
  marked.setOptions({
    breaks: true,
    gfm: true,
  });

  // Upload area drag-and-drop
  const uploadArea = document.getElementById("uploadArea");
  uploadArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadArea.classList.add("drag-over");
  });
  uploadArea.addEventListener("dragleave", () => uploadArea.classList.remove("drag-over"));
  uploadArea.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadArea.classList.remove("drag-over");
    const f = e.dataTransfer.files[0];
    if (f) setFile(f);
  });
  uploadArea.addEventListener("click", () => document.getElementById("fileInput").click());

  // File input
  document.getElementById("fileInput").addEventListener("change", (e) => {
    if (e.target.files[0]) setFile(e.target.files[0]);
  });

  // Text area char count
  document.getElementById("textInput").addEventListener("input", updateCharCount);

  // Upload tabs
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => switchTab(btn.dataset.tab));
  });

  // Report section navigation tabs
  document.querySelectorAll(".report-tab").forEach((btn) => {
    btn.addEventListener("click", () => scrollToReportSection(btn.dataset.target));
  });

  // Model select
  document.getElementById("modelSelect").addEventListener("change", (e) => {
    document.getElementById("customModelGroup").style.display =
      e.target.value === "custom" ? "block" : "none";
  });

  // Nav items
  document.querySelectorAll(".nav-item").forEach((item) => {
    item.addEventListener("click", (e) => {
      e.preventDefault();
      const section = item.dataset.section;
      showSection(section === "upload" ? "upload-section" : "result-section");
      document.querySelectorAll(".nav-item").forEach((n) => n.classList.remove("active"));
      item.classList.add("active");
    });
  });
});

/* ── File Handling ──────────────────────── */
function setFile(file) {
  const MAX_SIZE = 20 * 1024 * 1024;
  if (file.size > MAX_SIZE) {
    showToast("文件过大，请上传 20MB 以内的文件", "error");
    return;
  }
  currentFile = file;
  document.getElementById("fileName").textContent = file.name;
  document.getElementById("fileSize").textContent = formatFileSize(file.size);
  document.getElementById("fileInfo").style.display = "flex";
  document.getElementById("uploadArea").style.display = "none";
}

function clearFile() {
  currentFile = null;
  document.getElementById("fileInfo").style.display = "none";
  document.getElementById("uploadArea").style.display = "block";
  document.getElementById("fileInput").value = "";
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / 1024 / 1024).toFixed(1) + " MB";
}

/* ── Tab Switching ──────────────────────── */
function switchTab(tabId) {
  activeTab = tabId;
  document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
  document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
  document.querySelector(`[data-tab="${tabId}"]`).classList.add("active");
  document.getElementById(tabId).classList.add("active");
}

/* ── Char Count ─────────────────────────── */
function updateCharCount() {
  const len = document.getElementById("textInput").value.length;
  document.getElementById("charCount").textContent = len.toLocaleString();
}

/* ── Section Switching ──────────────────── */
function showSection(sectionId) {
  document.querySelectorAll(".content-section").forEach((s) => s.classList.remove("active"));
  document.getElementById(sectionId).classList.add("active");
}

function backToUpload() {
  showSection("upload-section");
  document.querySelectorAll(".nav-item").forEach((n) => n.classList.remove("active"));
  document.querySelector('[data-section="upload"]').classList.add("active");
}

/* ── Analysis ───────────────────────────── */
async function startAnalysis() {
  const apiKey = document.getElementById("apiKey").value.trim();
  const modelSelect = document.getElementById("modelSelect").value;
  const model = modelSelect === "custom"
    ? document.getElementById("customModel").value.trim() || "gpt-4o"
    : modelSelect;
  const baseUrl = document.getElementById("baseUrl").value.trim();

  const formData = new FormData();
  if (activeTab === "file-tab") {
    if (!currentFile) {
      showToast("请先上传文书文件", "warning");
      return;
    }
    formData.append("file", currentFile);
  } else {
    const text = document.getElementById("textInput").value.trim();
    if (!text) {
      showToast("请输入或粘贴文书内容", "warning");
      return;
    }
    formData.append("text", text);
  }

  if (apiKey) formData.append("api_key", apiKey);
  if (model) formData.append("model", model);
  if (baseUrl) formData.append("base_url", baseUrl);

  showLoading();

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || `服务器错误 (${response.status})`);
    }

    hideLoading();
    showReport(data.result, data.char_count);
  } catch (err) {
    hideLoading();
    showToast("分析失败：" + err.message, "error");
  }
}

/* ── Report Rendering ───────────────────── */
function showReport(markdown, charCount) {
  currentReportMd = markdown;

  // Update meta info
  const now = new Date().toLocaleString("zh-CN", {
    year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit",
  });
  document.getElementById("resultMeta").textContent =
    `生成时间：${now}　　文书字数：${charCount ? charCount.toLocaleString() + " 字符" : "—"}`;

  // Render Markdown
  const reportEl = document.getElementById("reportContent");
  reportEl.innerHTML = renderMarkdown(markdown);

  // Add section anchors for tab navigation
  addSectionAnchors(reportEl);

  // Render Mermaid diagrams
  renderMermaidInContainer(reportEl);

  // Show result section
  showSection("result-section");
  const navResult = document.getElementById("nav-result");
  navResult.style.display = "flex";

  document.querySelectorAll(".nav-item").forEach((n) => n.classList.remove("active"));
  navResult.classList.add("active");

  window.scrollTo({ top: 0, behavior: "smooth" });
}

function renderMarkdown(md) {
  // Pre-process: protect Mermaid code blocks from being broken by marked
  const mermaidBlocks = [];
  const placeholder = md.replace(/```mermaid\n([\s\S]*?)```/g, (_, code) => {
    const idx = mermaidBlocks.length;
    mermaidBlocks.push(code);
    return `MERMAID_PLACEHOLDER_${idx}`;
  });

  let html = marked.parse(placeholder);

  // Restore mermaid blocks as <div class="mermaid">
  html = html.replace(/MERMAID_PLACEHOLDER_(\d+)/g, (_, idx) => {
    return `<div class="mermaid">${mermaidBlocks[parseInt(idx, 10)]}</div>`;
  });

  return html;
}

async function renderMermaidInContainer(container) {
  const diagrams = container.querySelectorAll(".mermaid");
  for (let i = 0; i < diagrams.length; i++) {
    const el = diagrams[i];
    const graphDef = el.textContent.trim();
    if (!graphDef) continue;
    try {
      const id = "mermaid-" + Date.now() + "-" + i;
      const { svg } = await mermaid.render(id, graphDef);
      el.innerHTML = svg;
    } catch (err) {
      el.innerHTML = `<div style="color:#c8311a;font-size:.82rem;padding:8px;">图表渲染失败：${err.message}</div><pre><code>${escapeHtml(graphDef)}</code></pre>`;
    }
  }
}

function addSectionAnchors(container) {
  const headings = container.querySelectorAll("h1, h2");
  headings.forEach((h, i) => {
    const text = h.textContent;
    if (text.includes("一") || text.includes("案情")) h.id = "section-1";
    else if (text.includes("二") || text.includes("研究")) h.id = "section-2";
    else if (text.includes("三") || text.includes("修订")) h.id = "section-3";
  });
}

function scrollToReportSection(targetId) {
  document.querySelectorAll(".report-tab").forEach((t) => t.classList.remove("active"));
  document.querySelector(`[data-target="${targetId}"]`).classList.add("active");
  const el = document.getElementById(targetId);
  if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
}

/* ── Actions ────────────────────────────── */
async function copyReport() {
  try {
    await navigator.clipboard.writeText(currentReportMd);
    showToast("报告已复制到剪贴板");
  } catch {
    showToast("复制失败，请手动选中复制", "error");
  }
}

function downloadReport() {
  const blob = new Blob([currentReportMd], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  const now = new Date();
  const ts = `${now.getFullYear()}${String(now.getMonth()+1).padStart(2,"0")}${String(now.getDate()).padStart(2,"0")}`;
  a.href = url;
  a.download = `阅核报告_${ts}.md`;
  a.click();
  URL.revokeObjectURL(url);
  showToast("报告已下载");
}

/* ── Loading ────────────────────────────── */
const LOADING_STEPS = ["📋 解析文书内容", "🔍 提取案情要素", "⚖ 进行法律审查", "✍ 生成修订建议"];
let stepIndex = 0;

function showLoading() {
  document.getElementById("loading").style.display = "flex";
  document.getElementById("analyzeBtn").disabled = true;
  stepIndex = 0;
  updateLoadingStep();
  loadingTimer = setInterval(() => {
    if (stepIndex < LOADING_STEPS.length - 1) {
      stepIndex++;
      updateLoadingStep();
    }
  }, 3500);
}

function updateLoadingStep() {
  const steps = document.querySelectorAll(".loading-step");
  steps.forEach((s, i) => {
    s.className = "loading-step";
    if (i < stepIndex) s.classList.add("done");
    else if (i === stepIndex) s.classList.add("active");
  });
}

function hideLoading() {
  clearInterval(loadingTimer);
  document.getElementById("loading").style.display = "none";
  document.getElementById("analyzeBtn").disabled = false;
}

/* ── Toast ──────────────────────────────── */
let toastTimer = null;
function showToast(msg, type = "info") {
  const el = document.getElementById("toast");
  const icons = { info: "✓", error: "✕", warning: "⚠" };
  el.textContent = (icons[type] || "") + "  " + msg;
  el.style.display = "block";
  el.style.background = type === "error" ? "#c8311a" : type === "warning" ? "#b45309" : "#1a3c6e";
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.style.display = "none"; }, 3500);
}

/* ── Utils ──────────────────────────────── */
function escapeHtml(str) {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
