"""
庭长阅核系统 — 桌面应用启动入口

使用 pywebview 将 Flask Web 应用嵌入原生桌面窗口，
双击或通过命令行 `python main.py` 即可启动可视化界面。
"""
import os
import sys
import socket
import threading

from dotenv import load_dotenv

load_dotenv()


def _find_free_port():
    """Find an available TCP port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def _start_flask(port):
    """Start the Flask server in a background thread."""
    from app import app
    app.run(host='127.0.0.1', port=port, threaded=True, use_reloader=False)


def main():
    """Launch the desktop GUI application."""
    import webview

    port = int(os.environ.get('PORT', 0)) or _find_free_port()
    url = f'http://127.0.0.1:{port}'

    # Start Flask in a daemon thread so it exits when the window closes
    server_thread = threading.Thread(target=_start_flask, args=(port,), daemon=True)
    server_thread.start()

    # Create and show the native desktop window
    webview.create_window(
        title='庭长阅核系统',
        url=url,
        width=1100,
        height=800,
        min_size=(800, 600),
    )
    webview.start()


if __name__ == '__main__':
    main()
