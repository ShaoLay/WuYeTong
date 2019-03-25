# 主页模块
import datetime
import re

from . import index_blue
from flask import render_template,current_app,session,request,jsonify
from info.models import User, News
from info import constants, response_code, redis_store, db


@index_blue.route('/register', methods=["POST"])
def register():
    """
    注册功能实现
    :return:
    """
    # 1. 接受参数(手机号， 短信验证码， 密码明文)
    json_data = request.json
    mobile = json_data.get("mobile")
    smscode_client = json_data.get("smscode")
    password = json_data.get("password")

    # 2.校验参数(判断是否缺少和手机号是否合法)
    if not all([mobile, smscode_client, password]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数！')
    if not re.match(r'^1[345678][0-9]{9}$', mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='手机号码不正确！')

    # 3.查询服务器的短信验证码
    try:
        smscode_server = redis_store.get('SMS:' + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询短信验证码失败！')
    if not smscode_server:
        return jsonify(errno=response_code.RET.NODATA, errmsg='短信验证码不存在！')

    # 4.跟客户端传入的短信验证码相比
    if smscode_client != smscode_server:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='输入短信验证码有误！')

    # 5.如果对比成功, 就创建User模型对象, 并对属性赋值
    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    user.password = password
    # 记录最后一次登录时间
    user.last_login = datetime.datetime.now()

    # 6.将模型数据同步到数据库中
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify(errno=response_code.RET.DBERR, errmsg='保存注册数据失败')

    # 7.保存session, 实现状态保持, 注册即登录
    session['user_id'] = user.id
    session['mobile'] = user.mobile
    session['nick_name'] = user.nick_name

    # 8.响应注册结果
    return jsonify(errno=response_code.RET.OK, errmsg='注册成功')


@index_blue.route('/news_list')
def index_news_list():
    """提供主页新闻列表数据
    1.接受参数（分类id,要看第几页，每页几条数据）
    2.校验参数 （判断以上参数是否为数字）
    3.根据参数查询用户想看的新闻列表数据
    4.构造响应的新闻列表数据
    5.响应新闻列表数据
    """
    # 1.接受参数（分类id,要看第几页，每页几条数据）
    cid = request.args.get('cid', '1')
    page = request.args.get('page', '1')
    per_page = request.args.get('per_page', '10')

    # 2.校验参数 （判断以上参数是否为数字）
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')

    # 3.根据参数查询用户想看的新闻列表数据
    if cid == 1:
        # 从所有的新闻中，根据时间倒叙，每页取出10条数据
        # paginate = [News,News,News,News,News,News,News,News,News,News]
        paginate = News.query.order_by(News.create_time.desc()).paginate(page, per_page, False)
    else:
        # 从指定的分类中，查询新闻，根据时间倒叙，每页取出10条数据
        paginate = News.query.filter(News.category_id==cid).order_by(News.create_time.desc()).paginate(page, per_page, False)

    # 4.构造响应的新闻列表数据
    # news_list = [News,News,News,News,News,News,News,News,News,News]
    # 取出当前页的所有的模型对象
    news_list = paginate.items
    # 读取分页的总页数，将来在主页新闻列表上拉刷新时使用的
    total_page = paginate.pages
    # 读取当前是第几页，将来在主页新闻列表上拉刷新时使用的
    current_page = paginate.page

    # 将模型对象列表转成字典列表，让json在序列化时乐意认识
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())

    # 构造响应给客户单的数据
    data = {
        'news_dict_list':news_dict_list,
        'total_page':total_page,
        'current_page':current_page
    }

    # 5.响应新闻列表数据
    return jsonify(errno=response_code.RET.OK, errmsg='OK', data=data)


@index_blue.route('/')
def index():
    """主页
    1.处理网页右上角的用户展示数据：当用户已登录展示'用户名 退出'；反之，展示'登录 注册'
    2.新闻点击排行展示：在News数据库表中查询，根据点击量clicks倒叙
    """
    # 1.处理网页右上角的用户展示数据
    user_id = session.get('user_id', None)
    user = None
    if user_id:
        # 表示用户已经登录，然后查询用户的信息
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 2.新闻点击排行展示
    # news_clicks = [News,News,News,News,News,News]
    news_clicks = []
    try:
        news_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    # 构造渲染模板的上下文数据
    context = {
        'user':user,
        'news_clicks':news_clicks
    }

    # 渲染主页
    return render_template('news/index.html', context=context)


@index_blue.route('/favicon.ico', methods=['GET'])
def favicon():
    """title左侧图标"""
    # return 'Users/zhangjie/Desktop/Information_29/info/static/news/favicon.ico'
    return current_app.send_static_file('news/favicon.ico')