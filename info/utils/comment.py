# 公共的工具文件
from flask import session,current_app,g
from info.models import User
from functools import wraps


def do_rank(index):
    """根据index，返回对应的first,second,third"""
    if index == 1:
        return 'first'
    elif index == 2:
        return 'second'
    elif index == 3:
        return 'third'
    else:
        return ''


# view_func == news_detail
def user_login_data(view_func):
    """使用装饰器的形式获取登录用户信息"""

    # 提示：wrapper函数会拦截到传给被装饰的函数的参数
    # 提示：装饰器会修改被装饰的函数的__name__属性，将所有被装饰的函数的名字都叫做wrapper
    # 解决：@wraps(view_func):会还原被装饰的函数的__name__属性

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        """具体获取登录用户信息的逻辑"""
        user_id = session.get('user_id', None)
        user = None
        if user_id:
            # 表示用户已经登录，然后查询用户的信息
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)

        # 使用全局的g变量存储查询出来的登录用户信息
        g.user = user

        # 执行被装饰的视图函数
        return view_func(*args, **kwargs)

    return wrapper


# def user_login_data():
#     """获取登录用户的信息的函数"""
#     user_id = session.get('user_id', None)
#     user = None
#     if user_id:
#         # 表示用户已经登录，然后查询用户的信息
#         try:
#             user = User.query.get(user_id)
#         except Exception as e:
#             current_app.logger.error(e)
#
#     return user