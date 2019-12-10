"""用户"""
from models.HYModels import business
from plugins.HYplugins.orm import Common, UUIDModel, Coordinate, db, AddressInfo
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

class FactoryBase(Common, db.Model, UUIDModel, UserToken, Coordinate, AddressInfo):
    """厂家用户"""

    __tablename__ = 'factory'

    _privacy_fields = {'status', 'open_id', 'id'}

    open_id = db.Column(db.String(length=32), unique=True, nullable=False, comment='用户微信uuid')
    name = db.Column(db.String(length=50), nullable=False, comment='用户名:厂家名')
    phone = db.Column(db.String(length=13), nullable=False, comment='手机号')

    def save_contact(self, contact_name: str, contact_phone: str, address: str, address_replenish: str,
                     longitude: float, latitude: float):
        """保存联系人
        如果存在相同的名称与手机号,则更新地址与坐标.
        如果不存在相同的名称与手机号,则新增联系人.
        :param contact_name: 名称
        :param contact_phone: 手机号
        :param address: 地址
        :param address_replenish:地址详情
        :param longitude: 经度
        :param latitude: 纬度
        :return:
        """
        query = business.FactoryContactBase.query

        contact = query.filter_by(factory_uuid=self.uuid, contact_name=contact_name,
                                  contact_phone=contact_phone).first()
        if contact:
            contact.address = address
            contact.address_replenish = address_replenish
            contact.longitude = longitude
            contact.latitude = latitude
        else:
            business.FactoryContactBase(factory_uuid=self.uuid, contact_name=contact_name,
                                        contact_phone=contact_phone, address=address,
                                        address_replenish=address_replenish, longitude=longitude,
                                        latitude=latitude).direct_add_()
        self.direct_update_()


class DriverBase(Common, db.Model, UUIDModel, UserToken):
    """驾驶员用户"""

    __tablename__ = 'driver'

    _privacy_fields = {'status', 'open_id', 'id'}

    open_id = db.Column(db.String(length=32), unique=True, nullable=False, comment='用户微信uuid')
    name = db.Column(db.String(length=10), nullable=False, comment='用户名:驾驶员名')
    phone = db.Column(db.String(length=13), nullable=False, comment='手机号')
    number_plate = db.Column(db.String(length=10), default='', comment='车牌号:驾驶员特有字段')
    verify = db.Column(db.Boolean, default=False, comment='账号审核状态')
