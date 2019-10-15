"""用户"""
import datetime
from init import db
from plugins.HYplugins.orm import Common, UUIDModel
from plugins.HYplugins.common.authorization import Token
from sqlalchemy import event


#  用户

class Factory(Common, db.Model, UUIDModel):
    """厂家用户"""

    _privacy_fields = {'status', 'open_id'}

    open_id = db.Column(db.String(length=32), unique=True, nullable=False, comment='用户微信uuid')
    name = db.Column(db.String(length=50), nullable=False, comment='用户名:厂家名')
    phone = db.Column(db.String(length=13), nullable=False, comment='手机号')
    address = db.Column(db.String(length=255), default='', comment='用户地址')
    address_replenish = db.Column(db.String(length=255), default='', comment='地址补充')
    longitude = db.Column(db.Float, comment='经度:厂家特有字段')
    latitude = db.Column(db.Float, comment='纬度:厂家特有字段')

    def generate_token(self):
        """生成缓存"""
        builder = Token(user=self)
        token = builder.generate_token(sub=self.id)
        builder.cache()
        return token
