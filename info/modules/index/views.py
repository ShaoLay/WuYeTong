from . import index_blu


@index_blu.route('/index')
def index():
    return 'index'