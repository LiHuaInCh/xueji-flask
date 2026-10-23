# -*- coding: utf-8 -*-
"""蓝图④：首页 / 个人中心 / 统计图表 / 排行榜"""
from flask import Blueprint

bp = Blueprint('main', __name__)

from . import views  # noqa: E402,F401
