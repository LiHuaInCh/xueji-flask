# 学迹 —— 基于 Flask 的学习打卡与资料共享平台

《Python 与 Web 开发》期末项目。记录每日学习打卡、自动生成可视化统计曲线、共享并评价课程/考研资料的小型学习社区。

## 技术栈

Flask 3 + Jinja2 + Flask-SQLAlchemy + Flask-Login + SQLite + Bootstrap 5 + ECharts 5

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动
python run.py

# 3. 浏览器打开 http://127.0.0.1:5000
```

演示账号：`demo / 123456`、`xiaoming / 123456`、`xiaohong / 123456`

## 目录结构

```
xueji/
├── run.py                  入口：python run.py 启动
├── config.py               开发/生产环境配置类
├── gen_doc.py              生成《说明.doc》，自动填真实行号 + 内嵌界面截图
├── shot.py                 用无头浏览器给每个页面截图（可选，需 playwright）
├── db.sql                  SQLite 建表脚本（主键/外键/索引）
├── 说明.doc / 说明.md      说明文档（23 条基本 + 5 条扩展 + 界面预览 + 答辩问答）
├── 截图/                   11 张页面截图（由 shot.py 生成，已内嵌进 说明.doc）
├── requirements.txt
├── app/
│   ├── __init__.py         应用工厂 create_app()、蓝图注册、请求钩子、404
│   ├── extensions.py       db / login_manager 集中管理
│   ├── models.py           6 张表的模型
│   ├── auth/               蓝图①：注册 / 登录 / 退出
│   ├── checkin/            蓝图②：每日打卡
│   ├── share/              蓝图③：资料上传 / 列表 / 详情 / 下载 / 评论 / 收藏
│   └── main/               蓝图④：首页 / 个人中心 / 统计图表 / JSON 接口 / 排行榜
├── templates/              12 个模板
└── static/
    ├── css/ js/ img/       Bootstrap、ECharts 已下载到本地，断网也能演示
    └── uploads/            上传的资料文件
```

## 页面清单

| 路由 | 模板 | 功能 |
|---|---|---|
| `/` | index.html | 首页：今日打卡入口、统计卡片、热门资料、最新动态 |
| `/auth/login`、`/auth/register` | login / register.html | 登录、注册（密码二次确认 + 用户名查重） |
| `/checkin` | clock.html | 每日打卡：选科目、填时长、写心得 |
| `/profile` | main.html | 个人中心：积分等级、我的打卡（分页）、我的资料、收藏夹 |
| `/calendar` + `/api/stats` | calendar.html | 统计图表：30 天热力图、科目饼图、近 7 天柱状图（ECharts + JSON 接口） |
| `/share/` | share.html | 资料列表：关键字搜索、分类筛选、分页 |
| `/share/detail/<id>` | detail.html | 资料详情：下载、评分、评论区、AJAX 收藏 |
| `/share/upload` | upload.html | 上传资料：类型白名单 + 8MB 限制 + `secure_filename` |
| `/rank` | rank.html | 学习时长排行榜 |

## 安全相关的几点

- 密码用 `werkzeug.security.generate_password_hash` 加盐哈希存储，不存明文。
- 上传做三重校验：后缀白名单、`secure_filename` 去目录、`MAX_CONTENT_LENGTH` 限制 8MB。
- 需要登录的页面统一用 `@login_required` 保护，未登录自动跳登录页。
- 查询全部走 SQLAlchemy ORM 参数化，避免 SQL 注入。
