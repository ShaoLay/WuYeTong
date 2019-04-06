# 专门处理文件上传存储的
import qiniu


access_key = 'u8ZpB-0AGQHiU7DOEaesk7NSvpUyYf1Wn9gx5MMw'
secret_key = 'DqcqoV4wYtdflyWXZmpX0FF4RgqnLiia89ldn5sa'
bucket_name = 'ihome'


def upload_file(data):
    """
    上传文件到七牛云
    :param data: 要上传的文件的二进制
    """
    q = qiniu.Auth(access_key, secret_key)
    token = q.upload_token(bucket_name)
    ret, info = qiniu.put_data(token, None, data)

    print(ret['key'])

    if info.status_code != 200:
        raise Exception('七牛上传失败')

    return ret['key']

#
# if __name__ == '__main__':
#
#     path = '/Users/zhangjie/Desktop/Images/timg.jpeg'
#     with open(path, 'rb') as file:
#         upload_file(file.read())

