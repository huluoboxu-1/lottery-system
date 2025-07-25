from flask import Flask
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


# 仅保留一个简单路由
@app.route('/')
def home():
    return "服务正常运行中！端口：" + os.environ.get('PORT', '5000')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Flask服务启动，端口：{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
