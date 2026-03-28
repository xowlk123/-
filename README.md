# 庭长阅核系统

> 智能辅助庭长审阅裁判文书草稿，自动生成案情摘要、研究报告及修订建议。

## 功能简介

上传裁判文书草稿（PDF / DOCX / TXT），系统将调用 AI 大模型自动生成以下三部分内容（全部 Markdown 格式）：

### 一、案情事实与思维导图
- **案情简述**：精炼概括原告诉求、被告答辩及核心事实
- **事实思维导图**：Mermaid 图表（时间线 / 法律关系图 / 资金流向图）
- **争议焦点**：提炼核心争议

### 二、案件研究报告
- **法律适用审查**：核查法条引用准确性，分析法律适用逻辑
- **类案裁判规则提示**：商事审判原则、常见裁判尺度
- **阅核意见**：签发建议（**建议签发** / **建议退改**）及理由

### 三、判决书修订建议（修订人：石）
- 针对事实认定不清、说理不透彻或表述不规范的段落给出修订意见
- 使用**加粗**标注新增内容，使用~~删除线~~标注删除内容
- 附【石评】修改说明

---

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置 API Key（可选）

可以通过以下两种方式提供 AI API Key：

**方式一：环境变量（推荐）**
```bash
export OPENAI_API_KEY=sk-...
# 如使用第三方 OpenAI 兼容服务，还需设置：
export OPENAI_BASE_URL=https://your-api-endpoint/v1
```

**方式二：在网页界面中填写**  
启动后在左侧 "API 设置" 面板中直接填写 API Key。

> 若未配置 API Key，系统将进入**演示模式**，展示功能界面但不进行真实 AI 分析。

### 3. 启动服务

```bash
cd backend
python main.py
```

或使用 uvicorn：

```bash
uvicorn backend.main:app --reload --port 8000
```

浏览器访问：**http://localhost:8000**

---

## 支持的 AI 模型

系统支持所有兼容 OpenAI API 的服务，内置以下模型选项：

| 模型 | 说明 |
|------|------|
| GPT-4o | 默认推荐，综合能力强 |
| GPT-4o mini | 快速、经济 |
| GPT-4 Turbo | 长上下文支持 |
| 自定义 | 支持任意 OpenAI 兼容模型（如 DeepSeek、通义千问等） |

配置自定义模型时，在 "API Base URL" 中填写服务端点，在 "自定义模型名称" 中填写模型 ID。

---

## 支持的文件格式

| 格式 | 说明 |
|------|------|
| `.txt` | 纯文本文件（UTF-8 / GBK 编码） |
| `.pdf` | PDF 文档（需 `pypdf` 库） |
| `.docx` / `.doc` | Word 文档（需 `python-docx` 库） |
| `.md` | Markdown 文件 |

文件大小限制：**20 MB**

---

## 项目结构

```
.
├── backend/
│   ├── main.py              # FastAPI 应用入口
│   ├── document_parser.py   # 文档解析（PDF/DOCX/TXT）
│   ├── ai_analyzer.py       # AI 分析模块（OpenAI 接口）
│   └── requirements.txt     # Python 依赖
├── frontend/
│   ├── index.html           # 主页面
│   └── static/
│       ├── css/style.css    # 样式表
│       └── js/app.js        # 前端逻辑
└── README.md
```

---

## 技术栈

- **后端**：Python + FastAPI + uvicorn
- **AI 集成**：OpenAI Python SDK（兼容第三方服务）
- **文档解析**：pypdf（PDF）、python-docx（Word）
- **前端**：原生 HTML/CSS/JavaScript
- **Markdown 渲染**：marked.js
- **图表渲染**：Mermaid.js

---

## 许可证

本项目用于司法辅助工作，仅供内部使用。
