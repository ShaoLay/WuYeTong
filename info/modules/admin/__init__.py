from flask import Blueprint,session,redirect,url_for,request


admin_blue = Blueprint('admin', __name__, url_prefix='/admin')

from . import views


@admin_blue.before_request
def check_admin():
    """验证用户身份是否是admin"""
    is_admin = session.get('is_admin', False)

    # 1.判断是否是管理员：只有管理员才能进入后台管理的主页
    # 2.当无论哪种用户访问后台 管理的登录界面，都是可以正常进入的。
        # 2.1 如果是前台用户，可以登录，但是登录后续的操作会被卡主
        # 2.2 如果是后台用户，可以登录，因为就是他的逻辑
        # 2.3 小猪佩奇输入 http://127.0.0.1:5000/admin/login
    # 3.如果管理员登录了后台管理，又误入了前台界面，当管理员在前台界面退出登录时，会留下"私生子（session is_admin=True）"
    if not is_admin and not request.url.endswith('/admin/login') and not request.url.endswith('/admin/user_count'):
        return redirect(url_for('index.index'))