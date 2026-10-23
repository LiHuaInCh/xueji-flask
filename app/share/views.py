# -*- coding: utf-8 -*-
"""资料共享：列表 / 上传 / 详情 / 下载 / 评论 / 收藏"""
import os
import time

from flask import (render_template, request, redirect, url_for, flash,
                   send_from_directory, jsonify, current_app)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from . import bp
from ..extensions import db
from ..models import Material, Comment, Favorite

CATEGORIES = ['课件', '笔记', '真题', '电子书', '代码', '其他']


def allowed_file(filename):
    """后缀白名单校验，防止上传 .py .sh 之类的危险文件"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config['ALLOWED_EXTENSIONS']


@bp.route('/')
def index():
    """资料列表：支持关键字搜索 + 分类筛选 + 分页"""
    q = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    page = request.args.get('page', 1, type=int)

    query = Material.query
    if q:
        query = query.filter(db.or_(Material.title.contains(q),
                                    Material.description.contains(q)))
    if category:
        query = query.filter(Material.category == category)

    pagination = query.order_by(Material.created_at.desc()) \
                      .paginate(page=page, per_page=6, error_out=False)

    return render_template('share.html', pagination=pagination, materials=pagination.items,
                           q=q, category=category, categories=CATEGORIES)


@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """上传资料：表单校验 + 文件类型白名单 + 大小限制（config 里的 MAX_CONTENT_LENGTH）"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '其他')
        description = request.form.get('description', '').strip()
        file = request.files.get('file')

        if not title:
            flash('资料标题不能为空', 'danger')
        elif file is None or file.filename == '':
            flash('请选择要上传的文件', 'danger')
        elif not allowed_file(file.filename):
            flash('不支持这种文件类型，只能上传：' +
                  '、'.join(sorted(current_app.config['ALLOWED_EXTENSIONS'])), 'danger')
        else:
            # secure_filename 去掉路径和特殊字符，前面加时间戳防止重名覆盖
            safe_name = secure_filename(file.filename)
            save_name = '%d_%s' % (int(time.time()), safe_name)
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], save_name)
            file.save(save_path)
            size = os.path.getsize(save_path)

            material = Material(user_id=current_user.id, title=title, category=category,
                                description=description, filename=save_name, filesize=size)
            db.session.add(material)
            current_user.points += 20          # 上传资料奖励 20 积分
            db.session.commit()
            flash('上传成功，积分 +20', 'success')
            return redirect(url_for('share.detail', mid=material.id))

    return render_template('upload.html', categories=CATEGORIES)


@bp.route('/detail/<int:mid>')
def detail(mid):
    """资料详情：一对多关系渲染评论区"""
    material = db.get_or_404(Material, mid)
    is_fav = False
    if current_user.is_authenticated:
        is_fav = Favorite.query.filter_by(user_id=current_user.id,
                                          material_id=mid).first() is not None
    return render_template('detail.html', material=material, is_fav=is_fav)


@bp.route('/download/<int:mid>')
def download(mid):
    """下载：下载数 +1"""
    material = db.get_or_404(Material, mid)
    if not material.filename:
        flash('这份资料没有附件', 'warning')
        return redirect(url_for('share.detail', mid=mid))

    material.downloads += 1
    db.session.commit()

    ext = os.path.splitext(material.filename)[1]
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], material.filename,
                               as_attachment=True, download_name=material.title + ext)


@bp.route('/comment/<int:mid>', methods=['POST'])
@login_required
def comment(mid):
    """发表评论并打分，顺便刷新资料平均分"""
    material = db.get_or_404(Material, mid)
    content = request.form.get('content', '').strip()
    rating = request.form.get('rating', 5, type=int)
    rating = min(max(rating, 1), 5)

    if not content:
        flash('评论内容不能为空', 'danger')
    else:
        db.session.add(Comment(user_id=current_user.id, material_id=mid,
                               rating=rating, content=content))
        current_user.points += 2
        db.session.commit()
        refresh_score(material)
        flash('评论发表成功', 'success')

    return redirect(url_for('share.detail', mid=mid))


def refresh_score(material):
    """聚合统计：重新计算平均分"""
    from sqlalchemy import func
    avg = db.session.query(func.avg(Comment.rating)) \
                    .filter(Comment.material_id == material.id).scalar() or 0
    material.score_avg = round(float(avg), 1)
    db.session.commit()


@bp.route('/favorite/<int:mid>', methods=['POST'])
@login_required
def favorite(mid):
    """AJAX 收藏 / 取消收藏，返回 JSON 局部刷新"""
    material = db.get_or_404(Material, mid)
    record = Favorite.query.filter_by(user_id=current_user.id, material_id=mid).first()

    if record:                      # 已经收藏过 → 取消
        db.session.delete(record)
        db.session.commit()
        return jsonify({'code': 0, 'favorited': False, 'msg': '已取消收藏'})

    db.session.add(Favorite(user_id=current_user.id, material_id=mid))
    db.session.commit()
    return jsonify({'code': 0, 'favorited': True, 'msg': '收藏成功'})
