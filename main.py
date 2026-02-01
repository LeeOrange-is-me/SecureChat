import threading
import time
import webbrowser
import sys
import os

# 确保能找到当前目录下的模块
sys.path.append(os.getcwd())

from app import app, socketio

def open_browser():
    """等待 1.5 秒后自动打开浏览器"""
    time.sleep(1.5)
    url = "http://127.0.0.1:9999"
    print(f"[SYSTEM] 正在打开浏览器访问: {url}")
    webbrowser.open(url)

def main():
    print("="*40)
    print("      SecureWebChat 启动系统")
    print("="*40)
    
    # 1. 启动一个后台线程来打开浏览器
    threading.Thread(target=open_browser, daemon=True).start()
    
    # 2. 启动 Web 服务器 (SocketIO)
    # debug=True 方便调试，但在 main.py 启动时可能会导致浏览器打开两次(这是Flask特性)，
    # 这里设为 False 以保证体验
    print("[SERVER] Web 服务器正在启动...")
    socketio.run(app, host='0.0.0.0', port=9999, debug=False, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n[SYSTEM] 服务器已停止")
        sys.exit(0)