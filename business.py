"""业务"""
import datetime
from plugins.HYplugins.orm import Common, OrderIdModel, Coordinate, db, Contact, AddressInfo
from sqlalchemy import event


class OrderBaseInfo(Contact, AddressInfo, Coordinate):
    """订单基础信息"""


class FactoryContactBase(Common, OrderBaseInfo, db.Model):
    """厂家常用联系人"""
    __tablename__ = 'factory_contact'

    factory_uuid = db.Column(db.String(length=40), db.ForeignKey('factory.uuid'), nullable=False, comment='厂家UUID')


class OrderBase(Common, OrderIdModel, db.Model, OrderBaseInfo):
    """厂家订单"""
    """update_time:司机接单时,提交订单原更新时间.原更新时间与订单现更新时间一致,接单通过.否则返回特有错误."""
    __tablename__ = 'factory_order'

    _privacy_fields = {'factory_uuid', 'status', 'id'}

    factory_uuid = db.Column(db.String(length=40), db.ForeignKey('factory.uuid'), nullable=False, comment='厂家UUID')

    description = db.Column(db.Text, comment='订单详情')
    images = db.Column(db.JSON, comment='订单图片')
    date = db.Column(db.Date, default=datetime.date.today, comment='订单开始日期')
    time = db.Column(db.Time, comment='订单具体时间')
    schedule = db.Column(db.SMALLINT, default=0, comment='订单进度:0:待接单,1:已接单,2:已完成', index=True)  # 增加索引 -> 事务锁,不会造成表锁
    update_time = db.Column(db.DateTime, default=datetime.datetime.now, comment='订单内容更新时间')
    driver_order_uuid = db.Column(db.String(12), db.ForeignKey('driver_order.order_uuid'), comment='驾驶员订单编号')
    # driver_order_uuid = db.Column(db.String(12), comment='驾驶员订单编号')  # 厂家订单的驾驶员订单编号外键不做约束

    factory = db.relationship('FactoryBase', backref='orders')
    driver_order = db.relationship('DriverOrderBase', lazy='joined', foreign_keys=[driver_order_uuid])

    def factory_info(self, result: dict, *args, **kwargs):
        """厂家详情"""
        result['factory_info'] = self.factory.serialization(remove={'create_time'})

    def driver_info(self, result: dict, *args, **kwargs):
        """驾驶员详情"""
        if self.driver_order:
            result['driver_info'] = self.driver_order.driver.serialization(remove={'verify', 'create_time'})
            result['driver_schedule'] = [item.serialization(remove={'driver_order_uuid', 'id'}) for item in
                                         self.driver_order.schedules]
        else:
            result['driver_info'] = {}
            result['driver_schedule'] = []

    def driver_serialization(self, increase: set = None, remove: set = None):
        """驾驶员端序列化"""
        if increase is None: increase = set()
        if remove is None: remove = set()
        # 自定义需要去除的字段可以写成 remove = remove | {'field'}
        remove = remove | set()
        increase = increase | set()

        result = dict()
        result.update({'order_info': self.serialization(increase=increase, remove=remove)})
        self.factory_info(result=result)
        return result

    def factory_serialization(self, increase: set = None, remove: set = None):
        """厂家端序列化"""
        if increase is None: increase = set()
        if remove is None: remove = set()
        result = dict()
        result.update({'order_info': self.serialization(increase=increase, remove=remove)})
        self.driver_info(result=result)
        return result


class DriverOrderBase(Common, OrderIdModel, db.Model, OrderBaseInfo):
    """驾驶员订单列表"""
    _privacy_fields = {'status', 'user_id', 'id'}
    __tablename__ = 'driver_order'

    driver_uuid = db.Column(db.String(length=40), db.ForeignKey('driver.uuid'), nullable=False, comment='驾驶员UUID')
    factory_order_uuid = db.Column(db.String(12), db.ForeignKey('factory_order.order_uuid'), comment='订单编号')
    description = db.Column(db.Text, comment='订单详情')
    images = db.Column(db.JSON, comment='订单图片')
    date = db.Column(db.Date, default=datetime.date.today, comment='订单开始日期')
    time = db.Column(db.Time, comment='订单具体时间')

    driver_schedule = db.Column(db.SMALLINT, default=1,
                                comment='驾驶员进度:-1:订单已取消,0:未接单1:已接单,2:已出发,3:已到达厂家,4:返程中,5:已送达,6:已验收')

    order = db.relationship(OrderBase, foreign_keys=[factory_order_uuid])

    driver = db.relationship("DriverBase", foreign_keys=[driver_uuid])

    def order_infos(self, result: dict, *args, **kwargs):
        """添加厂家详情与进度详情"""
        # self.factory_info(result, *args, **kwargs)
        self.schedule_info(result, *args, **kwargs)

    def schedule_info(self, result: dict, *args, **kwargs):
        """进度详情"""
        result['schedules'] = [item.serialization(remove={'driver_order', 'id'}) for item in self.schedules]

    def customize_serialization(self):
        """自定义序列化"""
        result = dict()
        result.update({'schedules': [item.serialization(remove={'driver_order', 'id'}) for item in self.schedules]})
        result.update({'order_info': self.serialization()})
        result.update({'factory_info': self.order.factory.serialization()})
        return result


class DriverOrderScheduleLogBase(Common, db.Model):
    """驾驶员订单进度日志"""
    __tablename__ = 'driver_order_schedule_log'

    driver_order_uuid = db.Column(db.String(length=12), db.ForeignKey('driver_order.order_uuid'), comment='订单编号')
    schedule = db.Column(db.SMALLINT, default=1, comment='驾驶员进度:0:未接单1:已接单,2:已出发,3:已到达厂家,4:返程中,5:已送达,6:已验收,-1:订单已取消')

    order = db.relationship(DriverOrderBase, backref='schedules')


@event.listens_for(DriverOrderBase.driver_schedule, 'set', propagate=True)
def driver_order_receive_set(target, value, old_value, initiator):
    """驾驶员订单状态改变,记录日志.
    触发器内部不做事务提交,统一由引发者提交事务
    :param target: 目标对象
    :param value: 触发值, schedule进度值
    :param old_value: 旧值
    :param initiator: 引发者
    :return:
    """
    if not target.id:
        target.direct_flush_()  # 驾驶员首次接受订单时,驾驶员订单编号为空.先提交事务获取订单编号

    DriverOrderScheduleLogBase(driver_order_uuid=target.order_uuid, schedule=value).direct_add_()

    if value == -1:
        OrderBase.query.filter_by(order_uuid=target.factory_order_uuid).update(
            {'schedule': 0, 'driver_order_uuid': None})
    else:
        OrderBase.query.filter_by(order_uuid=target.order_uuid).update({'schedule': value})
