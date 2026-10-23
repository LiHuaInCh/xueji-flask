"""给 学迹 项目每个页面截图（用于说明文档的「界面预览」页）。"""
import os
from playwright.sync_api import sync_playwright

BASE = os.environ.get('BASE', 'http://127.0.0.1:5000')
OUT = os.environ.get('OUT', '/tmp/shots')
os.makedirs(OUT, exist_ok=True)

PAGES = [
    ('01_index', '/', '首页'),
    ('02_login', '/auth/login', '登录'),
    ('03_register', '/auth/register', '注册'),
    ('04_checkin', '/checkin', '每日打卡'),
    ('05_profile', '/profile', '个人中心'),
    ('06_calendar', '/calendar', '统计图表'),
    ('07_share', '/share/', '资料共享'),
    ('08_detail', '/share/detail/1', '资料详情'),
    ('09_upload', '/share/upload', '上传资料'),
    ('10_rank', '/rank', '排行榜'),
    ('11_mobile_index', '/', '手机端首页'),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 1280, 'height': 860}, device_scale_factor=1)
    page = ctx.new_page()
    page.goto(BASE + '/auth/login')
    page.fill('input[name=username]', 'demo')
    page.fill('input[name=password]', '123456')
    page.click('button[type=submit]')
    page.wait_for_load_state('networkidle')

    mobile = False
    for name, path, _title in PAGES:
        if 'mobile' in name and not mobile:
            page.set_viewport_size({'width': 400, 'height': 860})
            mobile = True
        page.goto(BASE + path)
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(600)
        page.screenshot(path=os.path.join(OUT, name + '.png'), full_page=True)
        print('shot', name)
    b.close()
print('done ->', OUT)
