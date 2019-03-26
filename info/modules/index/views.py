# 主页模块
from . import index_blue
from flask import render_template,current_app,session,request,jsonify
from info.models import User, News
from info import constants,response_code



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