# 个人中心
from info.utils.file_storage import upload_file
from . import user_blue
from flask import render_template,g,redirect,url_for,request,jsonify,current_app,session
from info.utils.comment import user_login_data
from info import response_code, db, constants


@user_blue.route('/user_collection')
@user_login_data
def user_collection():
    """用户收藏"""
    # 1.获取登录用户信息
    user = g.user
    if not user:
        return redirect(url_for('index.index'))

        # 2.接受参数
        page = request.args.get('p', '1')

        # 3.校验参数
        try:
            page = int(page)
        except Exception as e:
            current_app.logger.error(e)
            page = '1'  # 公司中对于这种处理会有专门的方案的，不需要操心

        # 4.分页查询 : user.collection_news == BaseQuery类型的对象
        paginate = None
        try:
            paginate = user.collection_news.paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        except Exception as e:
            current_app.logger.error(e)

        # 5.构造渲染模板的数据
        news_list = paginate.items
        total_page = paginate.pages
        current_page = paginate.page

        news_dict_list = []
        for news in news_list:
            news_dict_list.append(news.to_basic_dict())

        context = {
            'news_list': news_dict_list,
            'total_page': total_page,
            'current_page': current_page
        }

        # 6.渲染模板
        return render_template('news/user_collection.html', context=context)

@user_blue.route('/pass_info', methods=['GET', 'POST'])
@user_login_data
def pass_info():
    """修改密码"""

    # 1.获取登录用户信息
    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    # 2.GET请求逻辑：渲染修改密码的界面
    if request.method == 'GET':
        return render_template('news/user_pass_info.html')

    # 3. POST请求逻辑： 修改密码业务逻辑实现
    if request.method == 'POST':
        # 3.1 接受参数
        old_password = request.json.get('old_password')
        new_password = request.json.get('new_password')

        # 3.2 校验参数
        if not all([old_password, new_password]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')

        # 判断输入的旧的密码是否是该登录用户的密码
        if not user.check_password(old_password):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='原密码输入有误')

        # 3.4 更新密码 # password ：setter方法
        user.password = new_password

        # 3.5 同步到数据库
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg='保存修改后的密码失败')

        # 3.5 响应修改密码结果
        return jsonify(errno=response_code.RET.OK, errmsg='修改密码成功')

@user_blue.route('/pic_info', methods=['GET', 'POST'])
@user_login_data
def pic_info():
    """设置头像
    """
    # 1.获取登录用户信息
    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    # 2.实现GET请求逻辑
    if request.method == 'GET':
        # 构造渲染数据的上下文
        context = {
            'user': user.to_dict()
        }
        # 渲染界面
        return render_template('news/user_pic_info.html', context=context)

    # 3.POST请求逻辑:上传用户头像
    if request.method == 'POST':
        # 3.1 获取参数（图片）
        avatar_file = request.files.get('avatar')

        # 3.2 校验参数（图片）
        try:
            avatar_data = avatar_file.read()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='读取头像数据失败')

        # 3.3 调用上传的方法，将图片上传的七牛
        try:
            key = upload_file(avatar_data)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.THIRDERR, errmsg='上传失败')

        # 3.4 保存用户头像的key到数据库
        user.avatar_url = key
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg='保存用户头像失败')

        data = {
            'avatar_url':constants.QINIU_DOMIN_PREFIX + key
        }
        # 3.5 响应头像上传的结果
        return jsonify(errno=response_code.RET.OK, errmsg='上传成功',data=data)


@user_blue.route('/base_info', methods=['GET', 'POST'])
@user_login_data
def base_info():
    """基本资料
    """
    # 1.获取登录用户信息
    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    # 2.实现GET请求逻辑
    if request.method == 'GET':
        # 构造渲染数据的上下文
        context = {
            'user': user.to_dict()
        }
        # 渲染界面
        return render_template('news/user_base_info.html',context=context)

    # 3.POST请求逻辑:修改用户基本信息
    if request.method == 'POST':
        # 3.1获取参数（签名，昵称，性别）
        nick_name = request.json.get('nick_name')
        signature = request.json.get('signature')
        gender = request.json.get('gender')

        # 3.2校验参数
        if not all([nick_name,signature,gender]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
        if gender not in ['MAN','WOMAN']:
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')

        # 3.3修改用户基本信息
        user.signature = signature
        user.nick_name = nick_name
        user.gender = gender

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg='修改用户资料失败')

        # 4."注意"：修改了昵称以后，记得将状态保持信息中的昵称页修改
        session['nick_name'] = nick_name

        # 5 响应修改资料的结果
        return jsonify(errno=response_code.RET.OK, errmsg='修改基本资料成功')


@user_blue.route('/info')
@user_login_data
def user_info():
    """个人中心入口
    提示：必须是登录用户才能进入
    """
    # 获取登录用户信息
    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    context = {
        'user':user.to_dict()
    }

    return render_template('news/user.html', context=context)