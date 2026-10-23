# -*- coding: utf-8 -*-
"""把 Markdown 稿子转成 Word/WPS 能直接打开的 .doc（HTML 内容 + .doc 后缀）。
只支持我用到的几种写法：# / ## / ### 标题、- 列表、| 表格 |、> 引用、--- 分隔线、**加粗**、`代码`。
用法：python md2doc.py 答辩稿.md 答辩稿.doc
"""
import html
import re
import sys

CSS = """
body { font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif; font-size: 11pt;
       line-height: 1.8; color: #222; margin: 40px 50px; }
h1 { font-size: 20pt; color: #2b3a67; border-bottom: 3px solid #4e6ef2; padding-bottom: 8px; }
h2 { font-size: 15pt; color: #2b3a67; margin-top: 26px; border-left: 5px solid #4e6ef2;
     padding-left: 10px; }
h3 { font-size: 12.5pt; color: #33406b; margin-top: 18px; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; }
th, td { border: 1px solid #c9d2e8; padding: 6px 9px; font-size: 10.5pt; text-align: left;
         vertical-align: top; }
th { background: #eef2ff; }
blockquote { background: #f5f7ff; border-left: 4px solid #a9b8f0; margin: 12px 0;
             padding: 8px 14px; color: #444; }
code { background: #f2f3f7; padding: 1px 4px; font-family: Consolas, monospace; }
hr { border: 0; border-top: 1px solid #dde3f0; margin: 22px 0; }
ul { margin: 6px 0 6px 20px; }
"""


def inline(text):
    """处理行内 **加粗** 和 `代码`"""
    text = html.escape(text, quote=False)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text


def cells(line):
    return [c.strip() for c in line.strip().strip('|').split('|')]


def convert(md):
    out, para, bullets, quote = [], [], [], []

    def flush():
        if para:
            out.append('<p>%s</p>' % '<br>'.join(para))
            del para[:]
        if bullets:
            out.append('<ul>%s</ul>' % ''.join('<li>%s</li>' % b for b in bullets))
            del bullets[:]
        if quote:
            out.append('<blockquote>%s</blockquote>' % '<br>'.join(quote))
            del quote[:]

    lines = md.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        # 表格：连续的 | 行
        if line.startswith('|') and i + 1 < len(lines) and set(lines[i + 1]) <= set('|-: '):
            flush()
            head = cells(line)
            i += 2
            body = []
            while i < len(lines) and lines[i].startswith('|'):
                body.append(cells(lines[i]))
                i += 1
            rows = ['<tr>%s</tr>' % ''.join('<th>%s</th>' % inline(c) for c in head)]
            for r in body:
                rows.append('<tr>%s</tr>' % ''.join('<td>%s</td>' % inline(c) for c in r))
            out.append('<table>%s</table>' % ''.join(rows))
            continue
        if line.startswith('### '):
            flush(); out.append('<h3>%s</h3>' % inline(line[4:]))
        elif line.startswith('## '):
            flush(); out.append('<h2>%s</h2>' % inline(line[3:]))
        elif line.startswith('# '):
            flush(); out.append('<h1>%s</h1>' % inline(line[2:]))
        elif line.startswith('> '):
            if para or bullets:
                flush()
            quote.append(inline(line[2:]))
        elif line.startswith('- '):
            if para or quote:
                flush()
            bullets.append(inline(line[2:]))
        elif line.strip() == '---':
            flush(); out.append('<hr>')
        elif not line.strip():
            flush()
        else:
            if bullets or quote:
                flush()
            para.append(inline(line))
        i += 1
    flush()
    return '\n'.join(out)


def main():
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding='utf-8') as f:
        md = f.read()
    title = md.split('\n', 1)[0].lstrip('# ').strip()
    doc = ('<html><head><meta charset="utf-8"><title>%s</title><style>%s</style></head>'
           '<body>%s</body></html>' % (html.escape(title), CSS, convert(md)))
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(doc)
    print('已生成 %s（%.1f KB）' % (dst, len(doc.encode('utf-8')) / 1024))


if __name__ == '__main__':
    main()
