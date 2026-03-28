# 庭长阅核系统

裁判文书智能阅核辅助平台 — 帮助庭长对裁判文书草稿进行智能阅核审查，自动生成三部分 Markdown 阅核报告。

## 功能特性

- **案情事实与思维导图**：自动概括原告诉求、被告答辩及案件核心事实，绘制案情时间线或法律关系图，提炼争议焦点。
- **案件研究报告**：基于现行公司法及商事法律规范，进行法律适用审查、类案裁判规则提示，并给出阅核意见。
- **判决书修订建议**：针对文书中存在的问题段落给出带修订痕迹的修改意见（加粗新增、删除线删除）。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入你的 OPENAI_API_KEY
```

`.env` 配置说明：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI 或兼容服务的 API 密钥（**必填**） | — |
| `OPENAI_BASE_URL` | API 基础 URL（可选，适用于 Azure OpenAI 等） | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | 使用的模型名称（可选） | `gpt-4o` |
| `PORT` | 服务端口（可选） | `5000` |
| `FLASK_DEBUG` | 是否启用调试模式（可选） | `false` |

### 3. 启动应用

**桌面模式（推荐）** — 自动弹出原生窗口，无需手动打开浏览器：

```bash
python main.py
```

**Web 模式** — 以传统 Web 服务运行，需在浏览器中打开：

```bash
python app.py
# 然后打开浏览器访问 http://localhost:5000
```

## 使用说明

1. 上传裁判文书草稿（支持 PDF、DOCX、TXT、MD 格式），或直接粘贴文书文本。
2. 点击「开始阅核分析」按钮，等待 AI 分析完成。
3. 查看自动生成的三部分阅核报告，支持复制或下载为 Markdown 文件。

## 项目结构

```
.
├── main.py                 # 桌面应用启动入口（推荐）
├── app.py                  # Flask 主应用 / Web 模式入口
├── requirements.txt        # Python 依赖
├── .env.example            # 环境变量示例
├── prompts/
│   └── analysis_prompt.py  # LLM 提示词
├── utils/
│   ├── document_parser.py  # 文档解析（PDF/DOCX/TXT）
│   └── llm_client.py       # LLM 调用封装
├── templates/
│   └── index.html          # 前端页面
└── static/
    ├── css/style.css       # 样式表
    └── js/main.js          # 前端交互逻辑
```

## 免责声明

本系统仅供辅助参考，AI 生成的阅核报告不构成法律意见，最终阅核结论以庭长判断为准。
