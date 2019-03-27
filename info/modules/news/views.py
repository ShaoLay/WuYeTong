from flask import render_template, session, current_app, g, abort

from info import constants
from info.models import User, News
from info.modules.news import news_blue
from info.utils.comment import user_login_data


@news_blue.route('/detail/<int:news_id>')
@user_login_data
def news_detail(news_id):
    """新闻详情"""
    # 1.查询登录用户信息——从装饰器中的g变量中获取登录用户信息
    user = g.user

    # 2.查询点击排行
    news_click = []
    try:
        news_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    # 3.查询新闻详情
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    # 404提示页面
    if not news:
        abort(404)

    context = {
        'user':user,
        # 'news_clicks':news_clicks,
        'news':news.to_dict(),

    }

    return render_template('news/detail.html', context=context)
