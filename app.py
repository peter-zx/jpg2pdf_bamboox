import sys
import os
import webbrowser
from flask import Flask
from routes.batch import batch_bp
from routes.single import single_bp

# 检测是否以 PyInstaller 打包形式运行
if getattr(sys, 'frozen', False):
    # 打包后的临时路径
    base_path = sys._MEIPASS
    template_folder = os.path.join(base_path, 'templates')
    static_folder = os.path.join(base_path, 'static')
else:
    # 开发模式下的路径
    base_path = os.path.dirname(__file__)
    template_folder = os.path.join(base_path, 'templates')
    static_folder = os.path.join(base_path, 'static')

app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

# 注册蓝图
app.register_blueprint(batch_bp)
app.register_blueprint(single_bp)

if __name__ == "__main__":
    # 启动后自动打开浏览器
    url = "http://127.0.0.1:5000"
    webbrowser.open(url)
    app.run(host="127.0.0.1", port=5000, debug=False)