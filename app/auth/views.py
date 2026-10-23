# -*- coding: utf-8 -*-
"""认证视图：注册 / 登录 / 退出"""
from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user

from . import bp
from ..extensions import db
from ..models import User


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """注册：用户名查重 + 密码二次确认"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')

        if not username or not password:
            flash('用户名和密码都不能为空', 'danger')
        elif len(password) < 6:
            flash('密码至少 6 位', 'danger')
        elif password != password2:
            flash('两次输入的密码不一致', 'danger')
        elif User.query.filter_by(username=username).first():
            flash('用户名「%s」已经被注册了' % username, 'danger')
        else:
            user = User(username=username, email=email, points=0)
            user.set_password(password)          # 存哈希，不存明文
            db.session.add(user)
            db.session.commit()
            flash('注册成功，快去登录吧', 'success')
            return redirect(url_for('auth.login'))

    return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """登录：校验密码，写 session（Flask-Login 完成）"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('用户名或密码错误', 'danger')
        else:
            login_user(user, remember=remember)
            session['username'] = user.username         # 顺手存一个方便展示
            flash('欢迎回来，%s' % user.username, 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))

    return render_template('login.html')


@bp.route('/logout')
@login_required
def logout():
    """退出登录：清掉 session"""
    logout_user()
    session.clear()
    flash('已退出登录', 'info')
    return redirect(url_for('main.index'))
