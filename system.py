"""系统相关模型"""
from plugins.HYplugins.orm import db
from plugins.HYplugins.orm import Common, UUIDModel
from plugins.HYplugins.common.authorization import Token


class UserToken(object):
    """用户类型模型,token相关方法"""

    def generate_token(self):
        """生成缓存"""
        builder = Token(user=self)
        token = builder.generate_token(sub=self.uuid, user_type=self.__class__.__name__)
        builder.cache()
        return token


class Admin(Common, db.Model, UUIDModel, UserToken):
    """管理员模型"""
    """管理员注册流程:数据库写入手机号,通过手机号匹配短信验证码最终关联open_id"""

    open_id = db.Column(db.String(length=32), unique=True, nullable=False, comment='用户微信uuid')
    name = db.Column(db.String(length=10), nullable=False, comment='管理员姓名')
    phone = db.Column(db.String(length=13), nullable=False, comment='手机号')
    sms_status = db.Column(db.Boolean, default=False, comment='是否接收短信的状态')
