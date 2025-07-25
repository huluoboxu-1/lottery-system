from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import random
import pandas as pd
import os
import configparser
import sys
from pathlib import Path

app = Flask(__name__)
CORS(app)

# 测试首页路由（用于验证是否能访问）
@app.route('/')
def test():
    return "服务已启动！"  # 简单响应，排除复杂逻辑干扰

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent


class LotteryBackend:
    def __init__(self):
        # 读取配置文件
        self.config = configparser.ConfigParser()
        config_path = BASE_DIR / "config.ini"
        self.config.read(config_path, encoding='utf-8')

        # 修复布尔值解析问题 - 兼容多种写法
        repeated_str = self.config.get('repeated', 'repeated', fallback='false').lower()
        self.allow_repeated = repeated_str in ('true', '1', 'yes', 'y')

        # 读取中签人数配置
        self.winner_num = self.config.getint('WinnerNum', 'num', fallback=1)

        # 读取标题配置
        self.title = self.config.get('Settings', 'title', fallback='抽签系统')

        # 初始化数据
        self.options = []
        self.candidates = []
        self.results = []
        self.load_data()

    def load_data(self):
        """读取Excel数据"""
        try:
            file_path = BASE_DIR / "resource.xlsx"
            if not file_path.exists():
                self.options = ["员工A", "员工B", "员工C", "员工D", "员工E"]
                return

            df = pd.read_excel(file_path)
            if df.shape[1] < 2:
                self.options = ["员工A", "员工B", "员工C", "员工D", "员工E"]
                return

            self.options = df.iloc[:, 1].dropna().astype(str).tolist()
            if not self.options:
                self.options = ["员工A", "员工B", "员工C", "员工D", "员工E"]
        except Exception as e:
            print(f"读取数据出错: {e}")
            self.options = ["员工A", "员工B", "员工C", "员工D", "员工E"]

    def start_rolling(self):
        """开始抽签"""
        if not self.candidates and not self.allow_repeated:
            self.candidates = self.options.copy()
        return random.choice(self.options)

    def stop_rolling(self):
        """停止抽签"""
        available = self.candidates if not self.allow_repeated else self.options
        actual_num = min(self.winner_num, len(available))
        winners = []

        for _ in range(actual_num):
            if self.allow_repeated:
                winner = random.choice(self.options)
            else:
                winner = random.choice(self.candidates)
                self.candidates.remove(winner)
            winners.append(winner)

        self.results.extend(winners)
        return winners

    def get_history(self):
        """获取历史记录"""
        return self.results

    def get_config(self):
        """获取配置信息"""
        return {
            "title": self.title,
            "allow_repeated": self.allow_repeated,
            "winner_num": self.winner_num
        }


# 实例化后端
lottery = LotteryBackend()


# 路由
@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')


@app.route('/start', methods=['GET'])
def start():
    return jsonify({"result": lottery.start_rolling()})


@app.route('/stop', methods=['GET'])
def stop():
    return jsonify({"winners": lottery.stop_rolling()})


@app.route('/history', methods=['GET'])
def history():
    return jsonify({"history": lottery.get_history()})


@app.route('/config', methods=['GET'])
def get_config():
    return jsonify(lottery.get_config())


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # 优先读取Vercel的PORT变量
    app.run(
        host='0.0.0.0',  # 必须是0.0.0.0，允许外部访问
        port=port,
        debug=False  # 生产环境禁用debug模式（会导致端口冲突）
    )
