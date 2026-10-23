# -*- coding: utf-8 -*-
"""扩展对象集中管理，避免循环导入"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'                  # 未登录时跳到登录页
login_manager.login_message = '请先登录再访问该页面'
login_manager.login_message_category = 'warning'
