"""庭长阅核系统 - 后端 API 服务"""
import os
import io
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from document_parser import parse_document
from ai_analyzer import analyze_document

app = FastAPI(
    title="庭长阅核系统",
    description="智能辅助庭长审阅裁判文书草稿，生成案情摘要、研究报告及修订建议",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_path / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    index_path = frontend_path / "index.html"
    return HTMLResponse(content=index_path.read_text(encoding="utf-8"))


@app.post("/api/analyze")
async def analyze(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    api_key: Optional[str] = Form(None),
    model: Optional[str] = Form("gpt-4o"),
    base_url: Optional[str] = Form(None),
):
    """
    接收裁判文书草稿（文件或纯文本），调用 AI 分析并返回三部分阅核报告。
    """
    document_text = ""

    if file and file.filename:
        content = await file.read()
        try:
            document_text = parse_document(content, file.filename)
        except Exception as exc:
            raise HTTPException(status_code=422, detail=f"文档解析失败：{exc}") from exc
    elif text:
        document_text = text.strip()
    else:
        raise HTTPException(status_code=400, detail="请上传文件或直接粘贴文书内容")

    if not document_text:
        raise HTTPException(status_code=422, detail="无法从上传文件中提取文字内容")

    # Use provided API key or fall back to environment variable
    key = api_key.strip() if api_key and api_key.strip() else os.environ.get("OPENAI_API_KEY", "")
    url = base_url.strip() if base_url and base_url.strip() else os.environ.get("OPENAI_BASE_URL", "")

    try:
        result = await analyze_document(
            document_text=document_text,
            api_key=key,
            model=model or "gpt-4o",
            base_url=url or None,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI 分析失败：{exc}") from exc

    return JSONResponse(content={"result": result, "char_count": len(document_text)})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
