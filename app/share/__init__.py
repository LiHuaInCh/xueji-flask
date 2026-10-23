# -*- coding: utf-8 -*-
"""蓝图③：资料共享（上传 / 列表 / 详情 / 评论 / 收藏）"""
from flask import Blueprint

bp = Blueprint('share', __name__, url_prefix='/share')

from . import views  # noqa: E402,F401
