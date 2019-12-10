"""通用模型"""
from plugins.HYplugins.orm import Common, db


class ImagesBase(Common, db.Model):
    """图片记录"""
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    user_uuid = db.Column(db.String(32), nullable=False, comment='用户ID')
    url = db.Column(db.String(length=255), nullable=False, unique=True, comment='图片地址')
    genre = db.Column(db.String(length=10), nullable=False, comment='图片用途')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    superior_id = db.Column(db.Integer)
    name = db.Column(db.String(length=255))
    level = db.Column(db.Integer)


class Area2(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    superior_id = db.Column(db.Integer)
    name = db.Column(db.String(length=255))
    level = db.Column(db.Integer)
