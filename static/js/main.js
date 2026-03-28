/* ===== Globals ===== */
let currentTab = 'file';
let selectedFile = null;
let rawMarkdown = '';

/* ===== Tab Switching ===== */
function switchTab(tab) {
  currentTab = tab;
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
  document.getElementById('tab-' + tab).classList.add('active');
  document.getElementById('panel-' + tab).classList.add('active');
  hideError();
}

/* ===== File Handling ===== */
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');

dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  const files = e.dataTransfer.files;
  if (files.length > 0) selectFile(files[0]);
});

fileInput.addEventListener('change', () => {
  if (fileInput.files.length > 0) selectFile(fileInput.files[0]);
});

function selectFile(file) {
  selectedFile = file;
  const dropContent = dropZone.querySelector('.drop-zone-content');
  if (dropContent) dropContent.style.display = 'none';
  const selectedDiv = document.getElementById('selected-file');
  document.getElementById('file-name-display').textContent = file.name + '  (' + formatSize(file.size) + ')';
  selectedDiv.style.display = 'flex';
  hideError();
}

function clearFile() {
  selectedFile = null;
  fileInput.value = '';
  document.getElementById('selected-file').style.display = 'none';
  const dropContent = dropZone.querySelector('.drop-zone-content');
  if (dropContent) dropContent.style.display = 'flex';
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

/* ===== Analysis ===== */
async function startAnalysis() {
  hideError();

  const btn = document.getElementById('analyze-btn');
  btn.disabled = true;

  // Validate input
  if (currentTab === 'file') {
    if (!selectedFile) {
      showError('请先选择或拖入一个文件');
      btn.disabled = false;
      return;
    }
  } else {
    const text = document.getElementById('text-input').value.trim();
    if (!text) {
      showError('请粘贴文书文本内容');
      btn.disabled = false;
      return;
    }
  }

  showProgress(true);
  hideResult();

  try {
    let response;

    if (currentTab === 'file') {
      const formData = new FormData();
      formData.append('file', selectedFile);
      response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
      });
    } else {
      const formData = new FormData();
      formData.append('text', document.getElementById('text-input').value.trim());
      response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
      });
    }

    const data = await response.json();

    if (!response.ok || data.error) {
      showError(data.error || '服务器错误，请稍后重试');
      return;
    }

    rawMarkdown = data.result || '';
    renderResult(rawMarkdown);

  } catch (err) {
    showError('网络请求失败：' + err.message);
  } finally {
    showProgress(false);
    btn.disabled = false;
  }
}

/* ===== Render Result ===== */
function renderResult(markdown) {
  const container = document.getElementById('result-content');

  // Configure marked
  marked.setOptions({
    gfm: true,
    breaks: true,
  });

  container.innerHTML = marked.parse(markdown);

  // Render Mermaid diagrams if present
  mermaid.initialize({ startOnLoad: false, theme: 'default' });
  const mermaidBlocks = container.querySelectorAll('code.language-mermaid');
  mermaidBlocks.forEach(async (block, index) => {
    try {
      const id = 'mermaid-' + index;
      const svgResult = await mermaid.render(id, block.textContent);
      const wrapper = document.createElement('div');
      wrapper.className = 'mermaid-diagram';
      wrapper.innerHTML = svgResult.svg;
      block.parentElement.replaceWith(wrapper);
    } catch (e) {
      console.warn('Mermaid render failed:', e);
    }
  });

  document.getElementById('result-section').style.display = 'block';
  document.getElementById('result-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/* ===== Copy & Download ===== */
function copyResult() {
  if (!rawMarkdown) return;
  navigator.clipboard.writeText(rawMarkdown).then(() => {
    alert('已复制到剪贴板');
  }).catch(() => {
    // Fallback
    const ta = document.createElement('textarea');
    ta.value = rawMarkdown;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    alert('已复制到剪贴板');
  });
}

function downloadResult() {
  if (!rawMarkdown) return;
  const blob = new Blob([rawMarkdown], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = '庭长阅核报告_' + new Date().toISOString().slice(0, 10) + '.md';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function resetApp() {
  clearFile();
  document.getElementById('text-input').value = '';
  hideResult();
  hideError();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

/* ===== Helpers ===== */
function showProgress(show) {
  document.getElementById('progress-section').style.display = show ? 'flex' : 'none';
}

function hideResult() {
  document.getElementById('result-section').style.display = 'none';
}

function showError(msg) {
  const el = document.getElementById('error-msg');
  el.textContent = msg;
  el.style.display = 'block';
}

function hideError() {
  document.getElementById('error-msg').style.display = 'none';
}
