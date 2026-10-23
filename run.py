# -*- coding: utf-8 -*-

from app import create_app

app = create_app('development')

if __name__ == '__main__':
    # 0.0.0.0 是为了同一局域网下用手机也能打开演示
    app.run(host='0.0.0.0', port=5000, debug=True)
