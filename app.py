import os
import traceback

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from utils.document_parser import parse_document
from utils.llm_client import analyze_document

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB upload limit
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt', 'md'}


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Accepts a multipart/form-data request with either:
      - 'file': an uploaded document file, or
      - 'text': raw document text pasted directly.
    Returns JSON with the markdown analysis result.
    """
    document_text = ''

    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400
        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的文件格式，请上传 PDF、DOCX、TXT 或 MD 文件'}), 400

        filename = secure_filename(file.filename)
        try:
            document_text = parse_document(file.stream, filename)
        except ValueError as e:
            return jsonify({'error': str(e)}), 422
        except Exception as e:
            app.logger.error(traceback.format_exc())
            return jsonify({'error': f'文件解析出错：{str(e)}'}), 500

    elif 'text' in request.form:
        document_text = request.form.get('text', '').strip()
    else:
        return jsonify({'error': '请上传文件或粘贴文书文本'}), 400

    if not document_text:
        return jsonify({'error': '文件内容为空，无法进行分析'}), 422

    api_key = os.environ.get('OPENAI_API_KEY', '')
    if not api_key:
        return jsonify({'error': '未配置 AI 服务密钥，请在 .env 文件中设置 OPENAI_API_KEY'}), 503

    try:
        result = analyze_document(document_text)
    except Exception as e:
        app.logger.error(traceback.format_exc())
        return jsonify({'error': f'AI 分析出错：{str(e)}'}), 500

    return jsonify({'result': result})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
