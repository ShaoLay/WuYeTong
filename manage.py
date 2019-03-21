from flask import Flask


app = Flask(__name__)

class Config(object):
    """工程配置信息"""
    DEBUG = True

app.config.from_object(Config)

@app.route('/index')
def index():
    return 'index'

if __name__ == '__main__':
    app.run()