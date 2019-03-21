from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

class Config(object):
    """工程配置信息"""
    DEBUG = True
    # 数据库配置信息_MySQL
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app.config.from_object(Config)
db = SQLAlchemy(app)

@app.route('/index')
def index():
    return 'index'

if __name__ == '__main__':
    app.run()