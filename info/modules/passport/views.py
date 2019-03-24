from flask import request, abort, current_app, make_response

from info import redis_store, constants
from info.utils.captcha.captcha import *
from . import passport_blue


@passport_blue.route('/image_code', method=["GET"])
def get_image_code():
    """
    获取图片验证码
    :return:
    """

    # 1.接受参数(uuid)
    imageCodeId = request.args.get('imageCodeId')

    # 2.校验参数(判断uuid是否为空)
    if not imageCodeId:
        abort(403)

    # 3.生成图片验证码
    name, text, image = captcha.generate_captcha()

    # 4.保存图片验证码redis
    try:
        redis_store.set('ImageCode:'+imageCodeId, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        abort(500)

    # 5.修改image的ContentType = ’image/jpg‘
    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'

    # 5.响应图片验证码
    return response