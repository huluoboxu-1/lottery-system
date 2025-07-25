from flask import Flask
import os

app = Flask(__name__)


# 仅保留根路由，无任何额外逻辑
@app.route('/')
def index():
    return "服务正常，端口：" + os.environ.get('PORT', '5000')


# 关键：不使用if __name__ == '__main__'启动（Vercel会自动调用）
# 直接暴露app变量给Vercel的Python运行时
application = app  # Vercel的Python适配器会寻找application变量
