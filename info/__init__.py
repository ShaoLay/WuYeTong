import redis

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_session import Session

from config import Config


# 数据库
db = SQLAlchemy()
redis_store = None



def create_app(config_name):
    """通过传入不同的配置名字, 初始化其对应配置的应用实例"""
    app = Flask(__name__)
    # 配置
    app.config.from_object(Config)
    # 配置数据库
    db.init_app(app)
    # 配置redis
    global redis_store
    redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
    # 开启csrf保护
    # CSRFProtect(app)
    # 设置session保存位置
    Session(app)

    # 注册蓝图
    from info.modules.index import index_blue
    app.register_blueprint(index_blue)

    from info.modules.passport import passport_blue
    app.register_blueprint(passport_blue)

    return app

