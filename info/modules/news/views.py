from info.modules.news import news_blue


@news_blue.route('/detail/<int:news_id>')
def news_detail(news_id):
    """新闻详情"""
