# -*- coding: utf-8 -*-
"""配置类：用类继承区分开发环境和生产环境"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """公共配置"""
    SECRET_KEY = 'xueji-2025-secret-key'                      # session 加密用的密钥
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'xueji.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')   # 上传文件的保存目录
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024                          # 上传文件最大 8MB
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx',
                          'txt', 'md', 'zip', 'rar', 'png', 'jpg', 'jpeg'}


class DevelopmentConfig(Config):
    """开发环境：打开调试"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境：关闭调试"""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
