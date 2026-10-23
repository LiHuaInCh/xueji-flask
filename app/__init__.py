# -*- coding: utf-8 -*-
"""应用工厂：所有扩展和蓝图都在这里组装"""
import os

from flask import Flask, render_template, request

from config import config
from .extensions import db, login_manager

# 项目根目录（templates / static 都在根目录下，不在 app 包里）
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 默认科目，第一次运行自动写进数据库
DEFAULT_SUBJECTS = [('Python', '🐍'), ('Web 前端', '🌐'), ('数据结构', '🌲'),
                    ('计算机网络', '📡'), ('高等数学', '📐'), ('英语', '🔤'),
                    ('考研政治', '📕'), ('其他', '📘')]


def create_app(config_name='default'):
    app = Flask(__name__,
                template_folder=os.path.join(BASE_DIR, 'templates'),
                static_folder=os.path.join(BASE_DIR, 'static'))
    app.config.from_object(config[config_name])

    # 1. 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)

    # 2. 注册蓝图（模块化分层）
    from .auth.views import bp as auth_bp
    from .checkin.views import bp as checkin_bp
    from .share.views import bp as share_bp
    from .main.views import bp as main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(checkin_bp)
    app.register_blueprint(share_bp)
    app.register_blueprint(main_bp)

    # 3. 请求钩子：每个请求进来先记一条日志（中间件思想）
    @app.before_request
    def log_request():
        app.logger.info('%s %s', request.method, request.path)

    # 4. 模板全局变量
    @app.context_processor
    def inject_site():
        return {'site_name': '学迹'}

    # 5. 统一 404 页面
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404

    # 上传文件超过 8MB 时给个友好提示，而不是报错页面
    @app.errorhandler(413)
    def file_too_large(error):
        return render_template('413.html'), 413

    # 6. 建表 + 初始化科目
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    with app.app_context():
        from .models import Subject
        db.create_all()
        if Subject.query.count() == 0:
            for name, icon in DEFAULT_SUBJECTS:
                db.session.add(Subject(name=name, icon=icon))
            db.session.commit()

    return app
