"""文档解析模块：支持 PDF、DOCX、TXT 格式"""
import io
from pathlib import Path


def parse_document(content: bytes, filename: str) -> str:
    """
    根据文件扩展名自动选择解析方式，返回纯文本内容。
    支持格式：.txt .pdf .docx .doc
    """
    suffix = Path(filename).suffix.lower()

    if suffix in (".txt", ".md"):
        return _parse_text(content)
    elif suffix == ".pdf":
        return _parse_pdf(content)
    elif suffix in (".docx", ".doc"):
        return _parse_docx(content)
    else:
        # 尝试作为纯文本解析
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return content.decode("gbk")
            except UnicodeDecodeError as exc:
                raise ValueError(f"不支持的文件格式：{suffix}") from exc


def _parse_text(content: bytes) -> str:
    for encoding in ("utf-8", "gbk", "gb2312", "utf-16"):
        try:
            return content.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue
    raise ValueError("无法识别文本编码")


def _parse_pdf(content: bytes) -> str:
    try:
        import pypdf  # type: ignore
    except ImportError as exc:
        raise ImportError("请安装 pypdf 库：pip install pypdf") from exc

    reader = pypdf.PdfReader(io.BytesIO(content))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def _parse_docx(content: bytes) -> str:
    try:
        import docx  # type: ignore
    except ImportError as exc:
        raise ImportError("请安装 python-docx 库：pip install python-docx") from exc

    doc = docx.Document(io.BytesIO(content))
    paragraphs = [para.text for para in doc.paragraphs]
    return "\n".join(paragraphs)
