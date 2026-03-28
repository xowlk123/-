import os
import io

def parse_txt(file_stream):
    """Parse plain text file."""
    content = file_stream.read()
    if isinstance(content, bytes):
        for encoding in ('utf-8', 'gbk', 'gb2312', 'utf-16'):
            try:
                return content.decode(encoding)
            except (UnicodeDecodeError, LookupError):
                continue
        return content.decode('utf-8', errors='replace')
    return content


def parse_pdf(file_stream):
    """Parse PDF file and extract text."""
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(file_stream)
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        return '\n'.join(text_parts)
    except Exception as e:
        raise ValueError(f"PDF解析失败：{str(e)}")


def parse_docx(file_stream):
    """Parse DOCX file and extract text."""
    try:
        from docx import Document
        doc = Document(file_stream)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return '\n'.join(paragraphs)
    except Exception as e:
        raise ValueError(f"DOCX解析失败：{str(e)}")


def parse_document(file_stream, filename):
    """Parse document based on file extension and return text content."""
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.pdf':
        return parse_pdf(file_stream)
    elif ext in ('.docx', '.doc'):
        return parse_docx(file_stream)
    elif ext in ('.txt', '.md'):
        return parse_txt(file_stream)
    else:
        # Try as plain text
        return parse_txt(file_stream)
