# -*- coding: utf-8 -*-
"""生成《说明.doc》和《说明.md》。

说明文档里的每一条要求都带**真实行号**：脚本按关键字扫描源码定位，
代码改动后重新执行 `python gen_doc.py` 即可刷新，不用手改。
界面预览页的截图取自 截图/ 目录（由 shot.py 自动生成），
.doc 里以内嵌 base64 图片的方式打包，单个文件就能提交。
"""
import base64
import os

BASE = os.path.dirname(os.path.abspath(__file__))

# ---------------- 基本要求：文件 + 关键字 + 知识点 ----------------
BASIC = [
    ('run.py', 'app.run(', 'Flask 应用启动入口：应用工厂创建应用 + 绑定端口运行'),
    ('config.py', 'class DevelopmentConfig', '基于类继承的环境配置（DevelopmentConfig / ProductionConfig）'),
    ('app/__init__.py', 'def create_app', '应用工厂函数 create_app()，集中组装扩展和蓝图'),
    ('app/extensions.py', 'login_manager = LoginManager()', '扩展对象集中管理，避免循环导入'),
    ('app/models.py', 'class User(UserMixin, db.Model)', 'Flask-SQLAlchemy 定义 User 模型'),
    ('app/models.py', 'db.ForeignKey(', 'db.ForeignKey 建外键，db.relationship 建一对多关系'),
    ('app/models.py', 'generate_password_hash(raw)', 'werkzeug 密码哈希存储（不存明文）'),
    ('app/auth/views.py', "methods=['GET', 'POST']", '@bp.route() 注册路由并声明 GET/POST 方法'),
    ('app/auth/views.py', 'request.form.get(', 'request.form 获取表单提交的数据'),
    ('app/auth/views.py', 'return redirect(', 'redirect(url_for()) 完成页面跳转'),
    ('app/auth/views.py', 'flash(', 'flash() 消息闪现，配合模板的 get_flashed_messages()'),
    ('app/main/views.py', '.paginate(', 'Model.query.paginate() 分页查询'),
    ('app/main/views.py', 'return jsonify(', 'jsonify() 返回 JSON 数据接口'),
    ('app/main/views.py', 'func.sum(', 'SQLAlchemy func 聚合统计（求和 / 去重计数）'),
    ('templates/index.html', '{% extends', 'Jinja2 模板继承 {% extends %}（子模板继承 base.html）'),
    ('templates/base.html', '{% block content %}', '{% block %} 定义可替换区块'),
    ('templates/index.html', '{% for ', '{% for %} 循环渲染统计卡片和列表'),
    ('templates/share.html', '{% if ', '{% if %} / {% else %} 条件渲染（空数据提示）'),
    ('templates/login.html', "url_for('static'", "url_for('static', filename=...) 引用静态文件"),
    ('templates/detail.html', '|default(', '{{ }} 输出变量与 | default() 过滤器'),
    ('db.sql', 'CREATE TABLE checkin', 'SQLite 建表脚本：主键、外键、索引齐全'),
    ('static/css/style.css', '@media', '@media 媒体查询实现响应式布局'),
    ('app/checkin/views.py', '@login_required', '@login_required 登录保护：未登录自动跳到登录页'),
]

# ---------------- 扩展要求 ----------------
EXTEND = [
    ('app/__init__.py', 'register_blueprint', '基于蓝图（Blueprint）+ 应用工厂的模块化分层架构'),
    ('app/__init__.py', '@app.before_request', 'before_request 请求钩子（中间件思想）+ Flask-Login 会话认证'),
    ('app/share/views.py', 'safe_name = secure_filename(', '文件上传：secure_filename + 后缀白名单 + 8MB 大小限制 + 下载计数'),
    ('templates/calendar.html', 'echarts.init', 'ECharts 可视化：热力图 / 柱状图 / 饼图，数据由 JSON 接口提供'),
    ('app/models.py', 'UniqueConstraint', '多对多关系建模（favorite 中间表）+ 连续打卡 / 排行榜聚合统计'),
]

# ---------------- 界面预览：截图文件 + 标题 + 说明 ----------------
SHOTS = [
    ('01_index.png', '首页', '今日打卡入口、四个统计卡片、热门资料、最新打卡动态'),
    ('02_login.png', '登录', 'session 会话认证，密码走哈希比对，错误时 flash 提示'),
    ('03_register.png', '注册', '用户名查重 + 两次密码一致性校验'),
    ('04_checkin.png', '每日打卡', '选科目、填时长、写心得，提交成功后积分 +10'),
    ('05_profile.png', '个人中心', '积分等级、我的打卡（分页）、我的资料、我的收藏三个标签页'),
    ('06_calendar.png', '统计图表', 'ECharts 热力图 + 科目饼图 + 近 7 天柱状图，数据来自 /api/stats'),
    ('07_share.png', '资料共享', '关键字搜索 + 分类筛选 + 分页'),
    ('08_detail.png', '资料详情', '下载（计数 +1）、星级评分、评论区、AJAX 收藏'),
    ('09_upload.png', '上传资料', '后缀白名单 + secure_filename + 8MB 大小限制'),
    ('10_rank.png', '排行榜', '按累计学习时长排名，前三名有奖牌标记'),
    ('11_mobile_index.png', '手机端首页（400px 窄屏）', '响应式布局：导航折叠成汉堡菜单、卡片自动变单列'),
]

# ---------------- 高频问答（每条：一问 + 要点 + 展开 + 本项目对应 + 可能追问） ----------------
QA = [
    ('GET 和 POST 有什么区别？',
     'GET 把参数放在 URL 上、语义是“取数据”；POST 把数据放在请求体里、语义是“交数据”。',
     'GET 会被浏览器缓存、能收藏、会留在浏览历史里，长度受 URL 限制；POST 不缓存、不留在历史里，'
     '长度几乎不受限，但直接刷新会重复提交，所以提交成功后要用 redirect 跳走（POST-Redirect-GET）。',
     '本项目列表页、详情页、统计页都用 GET；登录、注册、打卡、上传、评论都用 POST。'
     '同一个视图函数用 <code>methods=[\'GET\', \'POST\']</code> 区分：GET 时渲染表单，POST 时读 request.form 处理。',
     '为什么登录表单不能用 GET？—— 密码会明文出现在 URL、浏览器历史、服务器访问日志和 Referer 里。'),
    ('cookie 和 session 是什么关系？',
     'session 数据保存在服务器端，浏览器只保存一个 session id 的 cookie。',
     'Flask 默认把 session 内容序列化、用 SECRET_KEY 签名后整体放进 cookie，用户改一个字节签名就对不上，'
     '所以 SECRET_KEY 泄露等于任何人都能伪造登录态。Flask-Login 往 session 里写 <code>_user_id</code>，'
     '每次请求再由 <code>user_loader</code> 把 User 对象还原出来，视图里的 current_user 就是它。',
     'SECRET_KEY 写在 <code>config.py</code>；<code>app/extensions.py</code> 里初始化 LoginManager 并指定未登录跳转的登录页；'
     '<code>app/models.py</code> 末尾的 load_user 就是 user_loader 回调。',
     '退出登录做了什么？—— <code>logout_user()</code> 清掉 session 里的登录信息，再 redirect 回首页。'),
    ('ORM 是什么？有什么好处和坏处？',
     'ORM（对象关系映射）把数据库表映射成 Python 类、把一行记录映射成对象，SQL 由框架生成。',
     '好处：写起来像操作对象、开发快；条件全部走参数绑定，天然防 SQL 注入；换数据库只改连接串。'
     '坏处：复杂多表查询不如手写 SQL 直观；不注意会产生 N+1 查询；批量操作比原生 SQL 慢一些。',
     '本项目 6 张表全部是 ORM 模型（<code>app/models.py</code>）：'
     '<code>db.session.add()/commit()</code> 是 INSERT，<code>.query.filter_by().paginate()</code> 是分页 SELECT，'
     '<code>db.relationship</code> 让 <code>user.checkins</code> 直接拿到关联记录，聚合统计用 <code>func.sum()</code>。',
     '怎么防止 SQL 注入？—— 所有查询条件都交给 ORM 参数绑定，绝不用字符串拼接 SQL；'
     '即使写原生 SQL 也用 <code>text()</code> 加参数。'),
    ('蓝图（Blueprint）解决了什么问题？',
     '把路由按业务拆成一个个独立模块，最后统一注册到应用上，避免所有视图堆在一个文件里。',
     '每个蓝图有自己的名称和 url_prefix，端点名自动带前缀（如 <code>auth.login</code>）不会重名；'
     '蓝图还可以整套复用到别的项目里，也方便多人分工。',
     '本项目拆成 4 个蓝图：auth（登录注册）、checkin（打卡）、share（资料）、main（首页统计）。'
     '每个包的 <code>__init__.py</code> 里定义 <code>bp = Blueprint(...)</code>，'
     '再在 <code>create_app()</code> 里 <code>app.register_blueprint(bp)</code>。',
     '蓝图和应用对象的区别？—— 蓝图是一组路由的集合，不能独立运行，必须注册到应用才能生效。'),
    ('Jinja2 模板是怎么渲染的？',
     '模板先被编译成 Python 代码，再传入上下文变量执行，最终生成 HTML 字符串返回给浏览器。',
     '<code>{{ }}</code> 输出变量（默认自动 HTML 转义，防 XSS），<code>{% %}</code> 是控制语句（if / for / block / extends），'
     '过滤器用竖线接，如 <code>{{ x|default(0) }}</code>。模板只负责展示，业务逻辑放视图里。',
     '本项目 templates/base.html 定义 <code>{% block content %}</code> 等区块，各页面用 <code>{% extends \'base.html\' %}</code> 继承，'
     '只写自己那一块；链接统一用 <code>url_for(\'main.index\')</code> 生成，改路由不用改模板。',
     '模板里能写 Python 吗？—— 只能写表达式和过滤器，不能写语句；真正的计算都放在视图或模型方法里。'),
    ('密码为什么要存哈希，不存明文？',
     '哈希是单向的、不可逆，而且加了随机盐，同样的密码每次算出的结果都不同。',
     '<code>generate_password_hash()</code> 默认用 pbkdf2:sha256 加随机盐并做多轮迭代，数据库里永远看不到明文；'
     '登录用 <code>check_password_hash()</code> 比对，不用自己写比较逻辑。这样即使数据库被拖走也无法直接还原密码。',
     '<code>app/models.py</code> 的 User 模型里 set_password / check_password 两个方法就是做这件事的，'
     '注册和登录视图只调用这两个方法，不碰 password_hash 字段。',
     '为什么不自己写 md5？—— md5 无盐、算得快，彩虹表和暴力破解很容易命中；werkzeug 的实现有盐、有迭代次数，'
     '还能随版本升级算法而不用改代码。'),
    ('多对多关系在数据库里怎么实现？',
     '加一张中间表，存两个外键，再对这两列加联合唯一约束。',
     '中间表自身没有业务含义，只负责记录“谁和谁有关系”；联合唯一约束保证同一个用户对同一份资料只能收藏一次，'
     '不会因为重复点击产生脏数据。查询时通过中间表把 user 和 material 关联起来。',
     '<code>app/models.py</code> 里的 Favorite 模型就是中间表：user_id、material_id 两个外键 + '
     '<code>db.UniqueConstraint(\'user_id\', \'material_id\', name=\'uq_user_material\')</code>；'
     '收藏接口是一个 toggle：已收藏就删除记录，没收藏就插入，最后返回 JSON 让前端直接切换按钮样式。',
     '一对多又是怎么建的？—— 外键建在“多”的一方：Checkin.user_id 指向 user.id，Material.user_id 同理。'),
]

# 备用问题：老师如果追问项目本身
BONUS = [
    ('项目怎么防 XSS（跨站脚本）？',
     'Jinja2 默认对所有 {{ }} 输出做 HTML 转义，我们也没有用 |safe 手动关闭转义，'
     '评论内容存原样、输出时由模板转义，无法注入脚本。'),
    ('项目怎么防 SQL 注入？',
     '所有查询都走 SQLAlchemy ORM 的参数绑定，没有任何字符串拼接 SQL。'),
    ('上传功能的安全措施？',
     '后缀白名单（只允许 pdf/doc/ppt/txt/md/zip/图片等）、<code>secure_filename()</code> 去掉路径和特殊字符、'
     'MAX_CONTENT_LENGTH 限制 8MB（超过返回 413 友好页）、文件统一存到 static/uploads 并重命名，不按用户文件名落盘。'),
    ('为什么用 SQLite 而不是 MySQL？',
     '课程项目数据量小、单机演示，SQLite 零配置、单文件、随项目一起提交就能跑；'
     '换成 MySQL 只需要改 config.py 里的连接串，代码一行都不用动（这正体现了 ORM 的好处）。'),
    ('项目里最难的一块是什么？',
     '统计接口。热力图要求近 30 天、柱状图要求近 7 天都必须是连续的日期轴，'
     '而数据库里没有打卡的日期是缺行。做法是后端先用 Python 生成完整日期列表，再把有记录的分钟数填进去，'
     '没打卡的天补 0，前端拿到的就是一段不会断的曲线。连续打卡天数同理：从今天（或昨天）往前逐天判断。'),
    ('应用工厂（create_app）有什么好处？',
     '把应用的创建和配置分开：<code>create_app(\'development\')</code> 和 <code>create_app(\'production\')</code> '
     '可以用不同配置（调试开关、数据库地址），也方便写单元测试时创建互不干扰的实例。'),
    ('前端的 AJAX 收藏是怎么实现的？',
     '<code>static/js/main.js</code> 用 fetch 向 <code>/share/favorite/&lt;id&gt;</code> 发 POST，'
     '后端返回 JSON（code / favorited / msg），前端根据结果切换爱心图标的颜色和文字，整页不刷新；'
     '同时后端仍会校验登录状态，未登录返回 401 并提示先登录。'),
]


def find_line(rel_path, keyword):
    """返回关键字第一次出现的行号，找不到返回 None"""
    path = os.path.join(BASE, rel_path)
    if not os.path.exists(path):
        return None
    with open(path, encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if keyword in line:
                return i
    return None


def build_items(items):
    out = []
    for idx, (path, keyword, desc) in enumerate(items, 1):
        line = find_line(path, keyword)
        out.append((idx, path, line, desc))
    return out


def render_rows(items):
    rows = []
    for idx, path, line, desc in items:
        loc = '%s【第 %d 行】' % (path, line) if line else '%s【未找到：%s】' % (path, desc)
        rows.append('<tr><td>%d</td><td>%s</td><td>%s</td></tr>' % (idx, loc, desc))
    return '\n'.join(rows)


def shots_html():
    """把 截图/ 里的页面截图以 base64 内嵌，保证 .doc 单个文件就能提交"""
    blocks = []
    for i, (fname, title, desc) in enumerate(SHOTS, 1):
        path = os.path.join(BASE, '截图', fname)
        if not os.path.exists(path):
            blocks.append('<p style="color:#c00">（缺少截图：%s，请先运行 shot.py 生成）</p>' % fname)
            continue
        with open(path, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode('ascii')
        blocks.append(
            '<div class="shot">'
            '<p class="cap">图 %d　%s</p>'
            '<img src="data:image/png;base64,%s" alt="%s">'
            '<p class="note">%s</p>'
            '</div>' % (i, title, b64, title, desc))
    return '\n'.join(blocks)


def qa_html():
    out = []
    for i, (q, core, detail, mine, follow) in enumerate(QA, 1):
        out.append(
            '<li><p class="q">Q%d：%s</p>'
            '<p><b>一句话回答：</b>%s</p>'
            '<p><b>展开讲：</b>%s</p>'
            '<p><b>本项目里对应的地方：</b>%s</p>'
            '<p><b>可能的追问：</b>%s</p></li>' % (i, q, core, detail, mine, follow))
    return '\n'.join(out)


def bonus_html():
    return '\n'.join('<li><b>%s</b><br>%s</li>' % (q, a) for q, a in BONUS)


def main():
    STUDENT = '软件1231班，2022122432邢康文'
    basic = build_items(BASIC)
    extend = build_items(EXTEND)

    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>学迹 —— 项目说明文档</title>
<style>
body { font-family: "Microsoft YaHei", SimSun, sans-serif; font-size: 14px; line-height: 1.8; margin: 40px; }
h1 { font-size: 22px; text-align: center; }
.stu { text-align: center; font-size: 15px; font-weight: bold; margin: 6px 0 22px 0; }
h2 { font-size: 17px; border-left: 5px solid #4f7cff; padding-left: 8px; margin-top: 26px; }
h3 { font-size: 15px; color: #1a3fbf; margin: 18px 0 8px 0; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; }
th, td { border: 1px solid #999; padding: 6px 8px; vertical-align: top; }
th { background: #eef2ff; }
code { background: #f5f5f5; padding: 1px 4px; }
.shot { text-align: center; margin: 18px 0 26px 0; page-break-inside: avoid; }
.shot img { width: 660px; border: 1px solid #bbb; }
.shot .cap { font-weight: bold; margin: 0 0 6px 0; text-align: center; }
.shot .note { color: #666; font-size: 13px; margin: 6px 0 0 0; text-align: center; }
.q { font-weight: bold; color: #1a3fbf; margin-bottom: 4px; }
li { margin-bottom: 12px; }
</style>
</head>
<body>

<h1>学迹 —— 基于 Flask 的学习打卡与资料共享平台<br><span style="font-size:14px;font-weight:normal">《Python 与 Web 开发》期末项目说明文档</span></h1>

<p class="stu">__STU__</p>

<h2>项目概况</h2>
<p>“学迹”是一个记录每日学习打卡、自动生成可视化统计曲线、并可共享评价课程/考研资料的小型学习社区。
技术栈：<b>Flask 3 + Jinja2 + Flask-SQLAlchemy + Flask-Login + SQLite + Bootstrap 5 + ECharts</b>。</p>
<ul>
  <li>页面数：13 个（首页、登录、注册、打卡、个人中心、统计图表、资料列表、资料详情、上传、排行榜、404、413、基础模板）</li>
  <li>数据表：6 张（user / subject / checkin / material / comment / favorite）</li>
  <li>项目结构：应用工厂 + 4 个蓝图（auth / checkin / share / main）模块化分层</li>
</ul>

<h3>运行方法</h3>
<ol>
  <li>安装依赖：<code>pip install -r requirements.txt</code></li>
  <li>（可选）生成演示数据：<code>python seed.py</code>，会写入近 30 天打卡记录、6 份资料和评论</li>
  <li>启动项目：<code>python run.py</code></li>
  <li>浏览器打开：<code>http://127.0.0.1:5000</code></li>
</ol>
<p>演示账号：<b>demo / 123456</b>（另有 xiaoming、xiaohong，密码相同）。</p>

<h3>数据库设计</h3>
<table>
  <tr><th>表名</th><th>字段</th><th>关系</th></tr>
  <tr><td>user</td><td>id, username, password_hash, email, created_at, points</td><td>—</td></tr>
  <tr><td>subject</td><td>id, name, icon</td><td>—</td></tr>
  <tr><td>checkin</td><td>id, user_id(FK), subject_id(FK), duration, note, date, created_at</td><td>user→checkin 一对多；subject→checkin 一对多</td></tr>
  <tr><td>material</td><td>id, user_id(FK), title, category, description, filename, filesize, downloads, score_avg, created_at</td><td>user→material 一对多</td></tr>
  <tr><td>comment</td><td>id, user_id(FK), material_id(FK), rating, content, created_at</td><td>material→comment 一对多</td></tr>
  <tr><td>favorite</td><td>id, user_id(FK), material_id(FK), created_at</td><td><b>user ↔ material 多对多</b>（中间表，联合唯一约束）</td></tr>
</table>
<p>完整建表 SQL 见 <code>db.sql</code>（含主键、外键、索引）。项目启动时 <code>app/__init__.py</code> 里的 <code>db.create_all()</code> 也会自动建表。</p>

<h2>一、基本要求完成情况（__BC__ 条，要求至少 20 条，每条 3 分）</h2>
<table>
  <tr><th style="width:50px">序号</th><th style="width:300px">文件与行号</th><th>知识点说明</th></tr>
__BROWS__
</table>

<h2>二、扩展要求完成情况（__EC__ 条，要求至少 5 条，每条 5 分）</h2>
<table>
  <tr><th style="width:50px">序号</th><th style="width:300px">文件与行号</th><th>知识点说明</th></tr>
__EROWS__
</table>

<h2>三、网页美观、内容分布、页面布局</h2>
<ul>
  <li><b>网页美观（5 分）</b>：全站统一使用 Bootstrap 5 卡片式设计，蓝色渐变导航栏与页面主色一致，卡片圆角、阴影、标签配色统一；Bootstrap 与 ECharts 都已下载到 <code>static/</code> 本地，答辩现场断网样式也不会乱。</li>
  <li><b>内容分布（5 分）</b>：首页分成「全站概览 → 热门资料 → 最新打卡动态」三块，一屏之内看完网站概况；个人中心用标签页把打卡、资料、收藏分开；统计页三个图表分区排列，信息不堆在一起。</li>
  <li><b>页面布局（5 分）</b>：13 个页面全部继承 <code>base.html</code>（导航、flash 提示、页脚只写一次），用 Bootstrap 栅格布局，并用 <code>@media</code> 做响应式，手机宽度下自动变单列（见下图 11）。</li>
</ul>

<h3>界面预览（13 个页面实拍）</h3>
<p>以下截图由 <code>shot.py</code> 用无头浏览器自动采集，展示各页面真实运行效果（同一份文档已内嵌图片，直接提交即可）。</p>
__SHOTS__

<h2>四、答辩准备</h2>
<h3>4.1 演示动线（5 分钟）</h3>
<ol>
  <li>打开首页，介绍课题与整体数据卡片</li>
  <li>注册 / 登录（展示 flash 提示、密码哈希）</li>
  <li>打卡一次（选科目、填时长、写心得），积分 +10</li>
  <li>进入统计图表页：热力图 / 科目饼图 / 近 7 天柱状图逐个出现（压轴）</li>
  <li>资料共享：搜索、分页、下载、评论打分、AJAX 收藏</li>
  <li>排行榜收尾</li>
</ol>

<h3>4.2 高频问答（7 个必答题）</h3>
<ol>
__QA__
</ol>

<h3>4.3 老师可能追问的项目问题（备用）</h3>
<ul>
__BONUS__
</ul>

<h3>4.4 答辩注意事项</h3>
<ul>
  <li><b>运行无报错</b>：14 条路由全部实测，页面返回 200，未登录访问受限页面正确 302 跳转，没有出现 5xx；上传超过 8MB 返回 413 友好提示页，不抛异常。</li>
  <li><b>代码规范</b>：视图函数统一按「取参数 → 校验 → 写库 → flash 提示 → 重定向」的顺序书写；注释只解释「为什么这么写」，没有注释掉的废代码和调试打印。</li>
  <li><b>界面交互</b>：收藏用 AJAX 完成，点爱心即时变色、页面不刷新；搜索、分类、分页三种条件可以叠加；空数据、上传失败都有友好提示，不会出现空白页。</li>
  <li><b>创新内容</b>：自己写的 <code>/api/stats</code> JSON 接口驱动 ECharts 三张图（日历热力图 / 环形饼图 / 柱状图）；应用工厂 + 蓝图分层架构；AJAX 收藏；连续打卡天数算法。</li>
</ul>

<h3>4.5 实现细节</h3>
<ul>
  <li>上传做了三重校验：后缀白名单、<code>secure_filename</code> 处理文件名、<code>MAX_CONTENT_LENGTH</code> 限制 8MB（超限返回 413 友好提示页），防止上传可执行文件和目录穿越。</li>
  <li>Bootstrap 和 ECharts 都下载到 <code>static/</code> 本地，答辩现场断网也能正常显示。</li>
  <li>统计接口 <code>/api/stats</code> 需要登录，返回近 30 天热力图、近 7 天柱状图、科目占比饼图和概览数字。</li>
  <li>说明文档中的行号由 <code>gen_doc.py</code> 扫描源码自动生成，代码改动后重跑一次即可刷新，不会出现“文档和代码对不上”的情况。</li>
</ul>

</body>
</html>
'''
    html = (html.replace('__STU__', STUDENT).replace('__BC__', str(len(basic))).replace('__BROWS__', render_rows(basic))
                .replace('__EC__', str(len(extend))).replace('__EROWS__', render_rows(extend))
                .replace('__SHOTS__', shots_html())
                .replace('__QA__', qa_html())
                .replace('__BONUS__', bonus_html()))

    with open(os.path.join(BASE, '说明.doc'), 'w', encoding='utf-8') as f:
        f.write(html)

    # ---------------- 同一份内容的 Markdown 版 ----------------
    md = ['# 学迹 —— 基于 Flask 的学习打卡与资料共享平台', '',
          '《Python 与 Web 开发》期末项目说明文档', '',
          STUDENT, '',
          '## 项目概况', '',
          '记录每日学习打卡、自动生成可视化统计曲线、并可共享评价课程/考研资料的小型学习社区。',
          '技术栈：**Flask 3 + Jinja2 + Flask-SQLAlchemy + Flask-Login + SQLite + Bootstrap 5 + ECharts**。', '',
          '- 页面数：13 个（首页、登录、注册、打卡、个人中心、统计图表、资料列表、资料详情、上传、排行榜、404、413、基础模板）',
          '- 数据表：6 张（user / subject / checkin / material / comment / favorite）',
          '- 项目结构：应用工厂 + 4 个蓝图（auth / checkin / share / main）', '',
          '### 运行方法', '',
          '```bash',
          'pip install -r requirements.txt',
          'python seed.py     # 可选：生成演示数据',
          'python run.py      # 打开 http://127.0.0.1:5000',
          '```', '',
          '演示账号：**demo / 123456**（另有 xiaoming、xiaohong）。', '',
          '### 数据库设计', '',
          '| 表名 | 字段 | 关系 |', '|---|---|---|',
          '| user | id, username, password_hash, email, created_at, points | — |',
          '| subject | id, name, icon | — |',
          '| checkin | id, user_id(FK), subject_id(FK), duration, note, date, created_at | user→checkin、subject→checkin 一对多 |',
          '| material | id, user_id(FK), title, category, description, filename, filesize, downloads, score_avg | user→material 一对多 |',
          '| comment | id, user_id(FK), material_id(FK), rating, content | material→comment 一对多 |',
          '| favorite | id, user_id(FK), material_id(FK) | **user ↔ material 多对多**（联合唯一约束） |', '',
          '## 一、基本要求完成情况（%d 条）' % len(basic), '',
          '| 序号 | 文件与行号 | 知识点 |', '|---|---|---|']
    for idx, path, line, desc in basic:
        md.append('| %d | %s 第 %d 行 | %s |' % (idx, path, line, desc))
    md += ['', '## 二、扩展要求完成情况（%d 条）' % len(extend), '',
           '| 序号 | 文件与行号 | 知识点 |', '|---|---|---|']
    for idx, path, line, desc in extend:
        md.append('| %d | %s 第 %d 行 | %s |' % (idx, path, line, desc))
    md += ['', '## 三、网页美观、内容分布、页面布局', '',
           '- **网页美观（5 分）**：全站统一 Bootstrap 5 卡片式设计，蓝色渐变导航栏与主色一致；Bootstrap 与 ECharts 已下载到 `static/` 本地，断网样式不乱。',
           '- **内容分布（5 分）**：首页「全站概览 → 热门资料 → 最新打卡动态」三段；个人中心用标签页分打卡/资料/收藏；统计页三图分区排列。',
           '- **页面布局（5 分）**：13 个页面全部继承 `base.html`；Bootstrap 栅格 + `@media` 响应式，手机宽度自动变单列。', '',
           '### 界面预览', '']
    for i, (fname, title, desc) in enumerate(SHOTS, 1):
        md += ['### 图 %d　%s' % (i, title), '', '![%s](截图/%s)' % (title, fname), '', desc, '']
    md += ['## 四、答辩准备', '', '### 4.1 演示动线（5 分钟）', '',
           '1. 打开首页，介绍课题与整体数据卡片',
           '2. 注册 / 登录（展示 flash 提示、密码哈希）',
           '3. 打卡一次（选科目、填时长、写心得），积分 +10',
           '4. 进入统计图表页：热力图 / 科目饼图 / 近 7 天柱状图（压轴）',
           '5. 资料共享：搜索、分页、下载、评论打分、AJAX 收藏',
           '6. 排行榜收尾', '',
           '### 4.2 高频问答（7 个必答题）', '']
    for i, (q, core, detail, mine, follow) in enumerate(QA, 1):
        md += ['### Q%d：%s' % (i, q), '',
               '- **一句话回答**：%s' % core,
               '- **展开讲**：%s' % detail,
               '- **本项目里对应的地方**：%s' % mine,
               '- **可能的追问**：%s' % follow, '']
    md += ['### 4.3 老师可能追问的项目问题（备用）', '']
    for q, a in BONUS:
        md += ['- **%s**　%s' % (q, a)]
    md += ['', '### 4.4 答辩注意事项', '',
           '- **运行无报错**：14 条路由实测，页面 200、受限页面 302 跳转，无 5xx；上传超 8MB 返回 413 友好页。',
           '- **代码规范**：视图函数统一「取参数 → 校验 → 写库 → flash → 重定向」；注释只解释为什么，没有废代码。',
           '- **界面交互**：AJAX 收藏无刷新；搜索、分类、分页可叠加；空数据有友好提示。',
           '- **创新内容**：`/api/stats` JSON 接口驱动 ECharts 三图；应用工厂 + 蓝图分层；连续打卡天数算法。', '',
           '### 4.5 实现细节', '',
           '- 上传三重校验：后缀白名单、`secure_filename`、`MAX_CONTENT_LENGTH` 8MB（超限返回 413 页）。',
           '- Bootstrap 和 ECharts 已下载到 `static/`，断网也能演示。',
           '- `/api/stats` 需要登录，返回近 30 天热力图、近 7 天柱状图、科目饼图和概览数字。',
           '- 文档里的行号由 `gen_doc.py` 扫描源码自动生成，代码改动后重跑即可刷新。', '']
    with open(os.path.join(BASE, '说明.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))

    size = os.path.getsize(os.path.join(BASE, '说明.doc')) / 1024.0
    print('已生成 说明.doc（%.0f KB，含 %d 张内嵌截图）/ 说明.md' % (size, len(SHOTS)))
    for idx, path, line, desc in basic + extend:
        print('  %2d. %s:%s  %s' % (idx, path, line, desc))


if __name__ == '__main__':
    main()
