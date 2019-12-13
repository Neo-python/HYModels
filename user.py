"""用户"""
from models.HYModels import business
from plugins.HYplugins.orm import Common, UUIDModel, Coordinate, db, AddressInfo
from plugins.HYplugins.common.authorization import Token


class UserToken(object):
    """用户类型模型,token相关方法"""

    def generate_token(self):
        """生成缓存"""
        builder = Token(user=self)
        token = builder.generate_token(uuid=self.uuid)
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

    _privacy_fields = {'status', 'open_id', 'id', 'remark'}

    open_id = db.Column(db.String(length=32), unique=True, nullable=False, comment='用户微信uuid')
    name = db.Column(db.String(length=10), nullable=False, comment='用户名:驾驶员名')
    phone = db.Column(db.String(length=13), nullable=False, comment='手机号')
    number_plate = db.Column(db.String(length=10), default='', comment='车牌号:驾驶员特有字段')
    verify = db.Column(db.SMALLINT, default=False, comment='账号审核状态. -2:封禁 -1:审核失败 0:待审核 1:审核通过')


class DriverSystemMessageBase(Common, db.Model):
    """驾驶员系统消息"""

    __tablename__ = 'driver_system_message'

    driver_uuid = db.Column(db.String(length=39), db.ForeignKey('driver.uuid'), nullable=False, comment='驾驶员UUID')
    genre = db.Column(db.SmallInteger, default=1, comment='消息通知类型.1:个人通知 2.订单信息')
    remark = db.Column(db.String(length=255), default='', comment='消息内容')
    reviewed = db.Column(db.SmallInteger, default=0, comment='用户查看状态. 0:未查看 1:已查看')
