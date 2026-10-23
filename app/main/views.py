# -*- coding: utf-8 -*-
"""首页 / 个人中心 / 统计图表页 / JSON 统计接口 / 排行榜"""
from datetime import date, timedelta

from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func

from . import bp
from ..extensions import db
from ..models import User, Subject, Checkin, Material, Favorite


def count_streak(user_id):
    """聚合统计：算连续打卡天数（从今天往前数，断一天就停）"""
    rows = db.session.query(Checkin.date).filter(Checkin.user_id == user_id) \
                     .distinct().order_by(Checkin.date.desc()).all()
    days = [r[0] for r in rows]
    if not days:
        return 0

    streak = 0
    cursor = date.today()
    if days[0] != cursor:               # 今天还没打卡，允许从昨天开始算
        cursor = cursor - timedelta(days=1)
    for d in days:
        if d == cursor:
            streak += 1
            cursor = cursor - timedelta(days=1)
        elif d < cursor:
            break
    return streak


@bp.route('/')
def index():
    """首页：今日打卡入口 + 统计卡片 + 热门资料 + 最新动态"""
    today = date.today()
    stats = {
        'users': User.query.count(),
        'checkins': Checkin.query.count(),
        'materials': Material.query.count(),
        'today': Checkin.query.filter_by(date=today).count(),
    }
    hot_materials = Material.query.order_by(Material.downloads.desc(), Material.id.desc()) \
                                  .limit(4).all()
    latest_checkins = Checkin.query.order_by(Checkin.created_at.desc()).limit(7).all()

    today_list, today_minutes = [], 0
    if current_user.is_authenticated:
        today_list = Checkin.query.filter_by(user_id=current_user.id, date=today).all()
        today_minutes = sum(i.duration for i in today_list)

    return render_template('index.html', stats=stats, hot_materials=hot_materials,
                           latest_checkins=latest_checkins, today_list=today_list,
                           today_minutes=today_minutes, today=today)


@bp.route('/profile')
@login_required
def profile():
    """个人中心：我的资料 / 积分等级 / 我的打卡（分页） / 收藏夹"""
    page = request.args.get('page', 1, type=int)

    pagination = Checkin.query.filter_by(user_id=current_user.id) \
                              .order_by(Checkin.date.desc(), Checkin.id.desc()) \
                              .paginate(page=page, per_page=5, error_out=False)
    my_materials = Material.query.filter_by(user_id=current_user.id) \
                                 .order_by(Material.created_at.desc()).all()
    my_favorites = Favorite.query.filter_by(user_id=current_user.id) \
                                 .order_by(Favorite.created_at.desc()).all()

    total_minutes = db.session.query(func.sum(Checkin.duration)) \
                              .filter(Checkin.user_id == current_user.id).scalar() or 0
    total_days = db.session.query(func.count(func.distinct(Checkin.date))) \
                           .filter(Checkin.user_id == current_user.id).scalar() or 0

    return render_template('main.html', pagination=pagination, my_materials=my_materials,
                           my_favorites=my_favorites, total_minutes=total_minutes,
                           total_days=total_days, streak=count_streak(current_user.id))


@bp.route('/calendar')
@login_required
def calendar():
    """统计页：图表数据由下面的 JSON 接口提供，前端用 ECharts 画"""
    return render_template('calendar.html')


@bp.route('/api/stats')
@login_required
def api_stats():
    """JSON 数据接口：热力图 + 柱状图 + 饼图 + 概览数字"""
    uid = current_user.id
    today = date.today()
    start = today - timedelta(days=29)

    # 1) 近 30 天每日学习时长（热力图）
    rows = db.session.query(Checkin.date, func.sum(Checkin.duration)) \
                     .filter(Checkin.user_id == uid, Checkin.date >= start) \
                     .group_by(Checkin.date).all()
    day_map = {r[0].strftime('%Y-%m-%d'): int(r[1] or 0) for r in rows}
    heatmap = []
    for i in range(30):
        d = start + timedelta(days=i)
        key = d.strftime('%Y-%m-%d')
        heatmap.append([key, day_map.get(key, 0)])

    # 2) 近 7 天柱状图（每天的分钟数）
    week = []
    for i in range(7):
        d = today - timedelta(days=6 - i)
        minutes = db.session.query(func.sum(Checkin.duration)) \
                            .filter(Checkin.user_id == uid, Checkin.date == d).scalar() or 0
        week.append([d.strftime('%m-%d'), int(minutes)])

    # 3) 各科目时长占比（饼图）
    pie_rows = db.session.query(Subject.name, func.sum(Checkin.duration)) \
                         .join(Checkin, Checkin.subject_id == Subject.id) \
                         .filter(Checkin.user_id == uid) \
                         .group_by(Subject.name).all()
    pie = [{'name': r[0], 'value': int(r[1] or 0)} for r in pie_rows]

    total_minutes = db.session.query(func.sum(Checkin.duration)) \
                              .filter(Checkin.user_id == uid).scalar() or 0
    total_days = db.session.query(func.count(func.distinct(Checkin.date))) \
                           .filter(Checkin.user_id == uid).scalar() or 0

    return jsonify({
        'code': 0,
        'heatmap': heatmap,
        'week': week,
        'pie': pie,
        'total_minutes': int(total_minutes),
        'total_days': int(total_days),
        'streak': count_streak(uid),
        'avg': round(total_minutes / total_days, 1) if total_days else 0,
        'points': current_user.points,
    })


@bp.route('/rank')
def rank():
    """排行榜：按累计学习时长排名"""
    rows = db.session.query(User.username,
                            func.sum(Checkin.duration).label('minutes'),
                            func.count(Checkin.id).label('times')) \
                     .join(Checkin, Checkin.user_id == User.id) \
                     .group_by(User.id) \
                     .order_by(func.sum(Checkin.duration).desc()) \
                     .limit(20).all()
    return render_template('rank.html', rows=rows)
