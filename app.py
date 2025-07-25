from flask import Flask

# 初始化应用（必须在所有路由前）
app = Flask(__name__)


# 仅保留最基础的路由，无任何额外逻辑
@app.route('/')
def index():
    return "Service running"


# 明确指定WSGI入口变量（与vercel.json中的wsgiEntrypoint对应）
application = app

# 移除本地启动代码（Vercel会自动调用WSGI入口）
# if __name__ == '__main__':
#     app.run()
