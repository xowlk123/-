"""Basic tests for the 庭长阅核 application."""
import io
import pytest
from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as c:
        yield c


def test_index_page(client):
    """The home page should return 200 and contain the app title."""
    resp = client.get('/')
    assert resp.status_code == 200
    assert '庭长阅核'.encode('utf-8') in resp.data


def test_analyze_no_input(client):
    """Posting with no file or text should return 400."""
    resp = client.post('/api/analyze')
    assert resp.status_code == 400
    data = resp.get_json()
    assert 'error' in data


def test_analyze_empty_text(client):
    """Posting empty text should return 422."""
    resp = client.post('/api/analyze', data={'text': '   '})
    assert resp.status_code == 422
    data = resp.get_json()
    assert 'error' in data


def test_analyze_unsupported_file_type(client):
    """Uploading an unsupported file type should return 400."""
    data = {
        'file': (io.BytesIO(b'fake content'), 'document.xyz'),
    }
    resp = client.post('/api/analyze', data=data, content_type='multipart/form-data')
    assert resp.status_code == 400
    json_data = resp.get_json()
    assert 'error' in json_data


def test_analyze_no_api_key(client, monkeypatch):
    """With text but no API key, should return 503."""
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    resp = client.post('/api/analyze', data={'text': '这是一份测试裁判文书草稿。'})
    assert resp.status_code == 503
    json_data = resp.get_json()
    assert 'error' in json_data


def test_document_parser_txt():
    """Plain text parsing should return the original text."""
    from utils.document_parser import parse_document
    content = '测试文书内容\n第二行'
    result = parse_document(io.BytesIO(content.encode('utf-8')), 'test.txt')
    assert '测试文书内容' in result


def test_document_parser_md():
    """Markdown file parsing should return text content."""
    from utils.document_parser import parse_document
    content = '# 标题\n正文内容'
    result = parse_document(io.BytesIO(content.encode('utf-8')), 'test.md')
    assert '正文内容' in result
