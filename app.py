from flask import Flask
from routes.batch import batch_bp
from routes.single import single_bp

app = Flask(__name__)

# 注册蓝图
app.register_blueprint(batch_bp)
app.register_blueprint(single_bp)

if __name__ == "__main__":
    app.run(debug=True)