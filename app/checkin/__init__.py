# -*- coding: utf-8 -*-
"""蓝图②：学习打卡"""
from flask import Blueprint

bp = Blueprint('checkin', __name__)

from . import views  # noqa: E402,F401
