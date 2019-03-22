from . import index_blue
from flask import render_template


@index_blue.route('/')
@index_blue.route('/index')
def index():
    """主页"""

    # 渲染主页
    return render_template('news/index.html')