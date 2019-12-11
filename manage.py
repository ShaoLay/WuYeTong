from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
# from info import app, db
from info import create_app, db, models # 这里导入models仅仅是为了在迁移时，让manage知道models的存在
from info.models import User



# 创建app
app = create_app('dev')

# 创建脚本管理器对象
manager = Manager(app)
# 让迁移和app和数据库建立管理
Migrate(app, db)
# 将数据库迁移的脚本添加到manager
manager.add_command('mysql', MigrateCommand)


# 脚本的使用 ： python manage.py createsuperuser -u admin -p 12345678 -m 18500000000
@manager.option('-u', '-username', dest='username')
@manager.option('-p', '-password', dest='password')
@manager.option('-m', '-mobile', dest='mobile')
def createsuperuser(username, password, mobile):
    """创建超级管理员用户的脚本函数"""

    if not all([username,password,mobile]):
        print('缺少必传参数')
    else:
        user = User()
        user.nick_name = username
        user.password = password
        user.mobile = mobile
        # 当is_admin为True时，才是管理员用户
        user.is_admin = True

        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)


if __name__ == '__main__':
    print(app.url_map)
    manager.run()
