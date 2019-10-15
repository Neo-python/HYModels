"""用户"""
from init import db
from plugins.HYplugins.orm import Common, UUIDModel, UserToken


#  用户

class Factory(Common, db.Model, UUIDModel, UserToken):
    """厂家用户"""

    _privacy_fields = {'status', 'open_id', 'id'}

    open_id = db.Column(db.String(length=32), unique=True, nullable=False, comment='用户微信uuid')
    name = db.Column(db.String(length=50), nullable=False, comment='用户名:厂家名')
    phone = db.Column(db.String(length=13), nullable=False, comment='手机号')
    address = db.Column(db.String(length=255), default='', comment='用户地址')
    address_replenish = db.Column(db.String(length=255), default='', comment='地址补充')
    longitude = db.Column(db.Float, comment='经度:厂家特有字段')
    latitude = db.Column(db.Float, comment='纬度:厂家特有字段')


class Driver(Common, db.Model, UUIDModel, UserToken):
    """驾驶员用户"""

    _privacy_fields = {'status', 'open_id', 'id'}
    open_id = db.Column(db.String(length=32), unique=True, nullable=False, comment='用户微信uuid')
    name = db.Column(db.String(length=50), nullable=False, comment='用户名:驾驶员名')
    phone = db.Column(db.String(length=13), nullable=False, comment='手机号')
    number_plate = db.Column(db.String(length=10), default='', comment='车牌号:驾驶员特有字段')
    verify = db.Column(db.Boolean, default=False, comment='账号审核状态')
