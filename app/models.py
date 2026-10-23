# -*- coding: utf-8 -*-
"""数据库模型：6 张表（user / subject / checkin / material / comment / favorite）"""
from datetime import date, datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db, login_manager


class User(UserMixin, db.Model):
    """用户表"""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.now)
    points = db.Column(db.Integer, default=0)          # 积分，打卡和上传资料都能加

    # 一对多：一个用户有多条打卡 / 多份资料 / 多条评论
    checkins = db.relationship('Checkin', backref='user', cascade='all, delete-orphan')
    materials = db.relationship('Material', backref='user', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='user', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='user', cascade='all, delete-orphan')

    def set_password(self, raw):
        """密码不明文存，存哈希值"""
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        """校验密码"""
        return check_password_hash(self.password_hash, raw)

    @property
    def level(self):
        """积分等级：每 100 分一级"""
        return self.points // 100 + 1


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login 根据 session 里的 id 把用户查出来"""
    return db.session.get(User, int(user_id))


class Subject(db.Model):
    """科目表"""
    __tablename__ = 'subject'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    icon = db.Column(db.String(16), default='📘')


class Checkin(db.Model):
    """打卡表：user 一对多 checkin"""
    __tablename__ = 'checkin'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    duration = db.Column(db.Integer, default=0)        # 学习时长（分钟）
    note = db.Column(db.Text)
    date = db.Column(db.Date, default=date.today, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    subject = db.relationship('Subject', backref='checkins')


class Material(db.Model):
    """资料表：user 一对多 material"""
    __tablename__ = 'material'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(32), default='其他', index=True)
    description = db.Column(db.Text)
    filename = db.Column(db.String(200))               # 存在磁盘上的真实文件名
    filesize = db.Column(db.Integer, default=0)
    downloads = db.Column(db.Integer, default=0)
    score_avg = db.Column(db.Float, default=0.0)       # 平均评分
    created_at = db.Column(db.DateTime, default=datetime.now)

    comments = db.relationship('Comment', backref='material', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='material', cascade='all, delete-orphan')

    @property
    def size_text(self):
        """把字节数显示成 B / KB / MB"""
        if self.filesize >= 1024 * 1024:
            return '%.1f MB' % (self.filesize / 1024 / 1024)
        if self.filesize >= 1024:
            return '%.1f KB' % (self.filesize / 1024)
        return '%d B' % self.filesize


class Comment(db.Model):
    """评论表：material 一对多 comment"""
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    rating = db.Column(db.Integer, default=5)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)


class Favorite(db.Model):
    """收藏表：user 和 material 的多对多中间表"""
    __tablename__ = 'favorite'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    __table_args__ = (db.UniqueConstraint('user_id', 'material_id', name='uq_user_material'),)
