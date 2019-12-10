"""用户"""
from plugins.HYplugins.orm import Common, UUIDModel, Coordinate, db
from plugins.HYplugins.common.authorization import Token


class UserToken(object):
    """用户类型模型,token相关方法"""

    def generate_token(self):
        """生成缓存"""
        builder = Token(user=self)
        token = builder.generate_token(sub=self.uuid, user_type=self.__class__.__name__)
        builder.cache()
        return token


#  用户

class FactoryBase(Common, db.Model, UUIDModel, UserToken, Coordinate):
    """厂家用户"""

    __tablename__ = 'factory'

    _privacy_fields = {'status', 'open_id', 'id'}

    open_id = db.Column(db.String(length=32), unique=True, nullable=False, comment='用户微信uuid')
    name = db.Column(db.String(length=50), nullable=False, comment='用户名:厂家名')
    phone = db.Column(db.String(length=13), nullable=False, comment='手机号')
    address = db.Column(db.String(length=255), default='', comment='用户地址')
    address_replenish = db.Column(db.String(length=255), default='', comment='地址补充')


class DriverBase(Common, db.Model, UUIDModel, UserToken):
    """驾驶员用户"""

    __tablename__ = 'driver'

    _privacy_fields = {'status', 'open_id', 'id'}

    open_id = db.Column(db.String(length=32), unique=True, nullable=False, comment='用户微信uuid')
    name = db.Column(db.String(length=10), nullable=False, comment='用户名:驾驶员名')
    phone = db.Column(db.String(length=13), nullable=False, comment='手机号')
    number_plate = db.Column(db.String(length=10), default='', comment='车牌号:驾驶员特有字段')
    # verify = db.Column(db.Boolean, default=True, comment='账号审核状态')
