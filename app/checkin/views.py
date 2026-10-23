# -*- coding: utf-8 -*-
"""打卡视图：选科目、填时长、写心得，一键打卡"""
from datetime import date, timedelta

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from . import bp
from ..extensions import db
from ..models import Checkin, Subject


@bp.route('/checkin', methods=['GET', 'POST'])
@login_required
def add():
    """打卡页：GET 显示表单，POST 保存记录"""
    subjects = Subject.query.all()

    if request.method == 'POST':
        subject_id = request.form.get('subject_id', type=int)
        duration = request.form.get('duration', type=int)
        note = request.form.get('note', '').strip()

        if not subject_id:
            flash('请先选择学习的科目', 'danger')
        elif not duration or duration <= 0 or duration > 1440:
            flash('学习时长要填 1 ~ 1440 之间的分钟数', 'danger')
        else:
            item = Checkin(user_id=current_user.id, subject_id=subject_id,
                           duration=duration, note=note, date=date.today())
            db.session.add(item)
            current_user.points += 10            # 打卡奖励 10 积分
            db.session.commit()
            flash('打卡成功！今日学习 %d 分钟，积分 +10' % duration, 'success')
            return redirect(url_for('main.profile'))

    # 今天的打卡记录 + 近 7 天时长
    today_list = Checkin.query.filter_by(user_id=current_user.id, date=date.today()) \
                              .order_by(Checkin.created_at.desc()).all()
    week_start = date.today() - timedelta(days=6)
    week_list = Checkin.query.filter(Checkin.user_id == current_user.id,
                                     Checkin.date >= week_start).all()
    today_minutes = sum(i.duration for i in today_list)
    week_minutes = sum(i.duration for i in week_list)

    return render_template('clock.html', subjects=subjects, today_list=today_list,
                           today_minutes=today_minutes, week_minutes=week_minutes)
