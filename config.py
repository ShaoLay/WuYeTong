from redis import StrictRedis
import logging


class Config(object):
    """配置文件的加载"""

    # 项目秘钥：CSRF/session,还有其他的一些签名算法会用
    SECRET_KEY = 'q7pBNcWPgmF6BqB6b5VICF7z7pI+90o0O4CaJsFGjzRsYiya9SEgUDytXvzFsIaR'

    # 开启调试模式
    DEBUG = True

    # 配置MySQL数据库连接信息:真实开发中，要使用mysql数据库的真实IP
    SQLALCHEMY_DATABASE_URI = 'mysql://root@127.0.0.1:3306/information'
    # 不去追踪数据库的修改，节省开销
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 配置redis数据库:因为redis模块不是flask的扩展，所以就不会自动的从config中读取配置信息，只能自己读取
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # 指定session使用什么来存储
    SESSION_TYPE = 'redis'
    # 指定session数据存储在后端的位置
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 是否使用secret_key签名你的sessin
    SESSION_USE_SIGNER = True
    # 设置过期时间，要求'SESSION_PERMANENT', True。而默认就是31天
    PERMANENT_SESSION_LIFETIME = 60*60*24 # 一天有效期


# 以下代码是封装不同开发环境下的配置信息

class DevlopmentConfig(Config):
    """开发环境"""
    # 开发环境和父类基本一致

    # 开发环境日志等级
    LEVEL_LOG = logging.DEBUG


class ProductionConfig(Config):
    """生产环境"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root@127.0.0.1:3306/information'
    # 生产环境日志等级
    LEVEL_LOG = logging.ERROR


class UnittestConfig(Config):
    """测试环境"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root@127.0.0.1:3306/information'
    # 生产环境日志等级
    LEVEL_LOG = logging.DEBUG


# 定义字典，存储关键字对应的不同的配置类的类名
configs = {
    'dev':DevlopmentConfig,
    'pro':ProductionConfig,
    'unit':UnittestConfig
}