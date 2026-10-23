# -*- coding: utf-8 -*-
"""蓝图①：用户认证（注册 / 登录 / 退出）"""
from flask import Blueprint

bp = Blueprint('auth', __name__, url_prefix='/auth')

from . import views  # noqa: E402,F401  放在 bp 之后导入，避免循环引用
