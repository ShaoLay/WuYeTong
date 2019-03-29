# 新闻详情：收藏、评论、点赞、...
from . import news_blue
from flask import render_template,session,current_app,abort,g,jsonify,request
from info.models import User, News, Comment
from info import constants, db,response_code
from info.utils.comment import user_login_data


@news_blue.route('/news_comment', methods=['POST'])
@user_login_data
def news_comment():
    """新闻评论和回复评论
    """
    # 1.获取登录用户信息
    user = g.user
    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg='用户未登录')

    # 2.接受参数
    news_id = request.json.get('news_id')
    comment_content = request.json.get('comment')
    parent_id = request.json.get('parent_id')

    # 3.校验参数:parent_id只有回复评论时才需要传入
    if not all([news_id,comment_content]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
    try:
        news_id = int(news_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')

    # 4.查询要评论的新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询新闻数据失败')
    if not news:
        return jsonify(errno=response_code.RET.NODATA, errmsg='新闻数据不存在')

    # 5.实现新闻评论和回复评论逻辑
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news_id
    comment.content = comment_content

    # 回复评论
    if parent_id:
        comment.parent_id = parent_id

    # 同步数据到数据库
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='评论失败')

    # 6.响应评论结果
    return jsonify(errno=response_code.RET.OK, errmsg='OK', data=comment.to_dict())


@news_blue.route('/news_collect', methods=['POST'])
@user_login_data
def news_collect():
    """新闻收藏和取消"""
    # 1.获取登录用户信息
    user = g.user
    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg='用户未登录')

    # 2.接受参数(news_id, action)
    news_id = request.json.get('news_id')
    action = request.json.get('action')

    # 3.校验参数
    if not all([news_id, action]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
    if action not in ['collect', 'cancel_collect']:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')

    # 4. 查询新闻信息
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询新闻数据失败')
    if not news:
        return jsonify(errno=response_code.RET.NODATA, errmsg='新闻数据不存在')

    # 5.收藏和取消新闻
    if action == 'collect':
        # 当要收藏的新闻不在用户收藏列表中才需要收藏
        if news not in user.collection_news:
            user.collection_news.append(news)
        else:
            # 当要取消收藏的新闻在用户收藏列表中才需要取消收藏
            if news in user.collection_news:
                user.collection_news.remove(news)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=response_code.RET.DBERR, errmsg='操作失败')

    # 6.响应操作结果
    return jsonify(errno=response_code.RET.OK, errmsg='操作成功')

@news_blue.route('/detail/<int:news_id>')
@user_login_data
def news_detail(news_id):
    """
    新闻详情
    """
    # 1.查询登录用户信息
    # 从装饰器中的g变量中获取登录用户信息
    user = g.user

    # 2.查询点击排行
    # news_clicks = [News,News,News,News,News,News]
    news_clicks = []
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

    # 后续会给404的异常准备一个友好的提示页面
    if not news:
        abort(404)

    # 4.累加点击量
    news.clicks += 1
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

    # 5.收藏和取消收藏
    is_collected = False
    if user:
       if news in user.collection_news:
            is_collected = True

    context = {
        'user':user,
        'news_clicks':news_clicks,
        'news':news.to_dict(),
        'is_collected':is_collected
    }

    # 渲染模板
    return render_template('news/detail.html', context=context)