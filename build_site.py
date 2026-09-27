# -*- coding: utf-8 -*-
"""build_site.py - 连环画画库静态书站生成器（GitHub Pages 用）。

扫描三卷：
  资治通鉴/   —— 解析每个 故事.md 生成 NN-回名.html 回页（书封封面 + 第X回回目 + 白话配文）
  成语故事/   —— 解析每个 故事.md 自动生成 NN-名称.html 册页（页面与图片同目录，相对引用）
  笑林广记/   —— 解析每个 笑话.md 自动生成 NN-名称.html 册页
产出：
  index.html  总目录（封面 + 三卷书目 + 缩略图 thumbs/）
  各故事文件夹内 NN-*.html 回页/册页
  thumbs/     首页缩略图（每故事取第一幅，长边 180px）
用法：
  python3 build_site.py          # 全量重建（幂等，直接覆盖）
组画清单表：| 画 | 场景 | 题款原文 | 白话 |——第四列白话为通鉴卷每幅配文，缺省回退场景描述。
设计：宣纸米白极简。
"""
import html as H
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
THUMBS = os.path.join(ROOT, 'thumbs')

HUAN = {'01': '一', '02': '二', '03': '三', '04': '四', '05': '五',
        '06': '六', '07': '七', '08': '八', '09': '九', '10': '十',
        '11': '十一', '12': '十二', '13': '十三', '14': '十四', '15': '十五',
        '16': '十六', '17': '十七', '18': '十八', '19': '十九', '20': '二十',
        '21': '二十一', '22': '二十二', '23': '二十三', '24': '二十四',
        '25': '二十五', '26': '二十六', '27': '二十七', '28': '二十八',
        '29': '二十九', '30': '三十'}

# ——— 与回页定稿一致的 CSS（宣纸米白极简）———
CSS = '''
  :root { --paper:#f5f1e8; --ink:#1a1a1a; --grey:#6b6558; --hair:#d8d2c4; --line:#2a2622; }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:var(--paper); color:var(--ink);
         font-family:"Songti SC","STSong","SimSun","Noto Serif SC",serif; }
  a { color:inherit; }
  .book { max-width:860px; margin:0 auto; padding:48px 24px 72px; }
  .topline { text-align:center; font-size:12px; color:var(--grey); letter-spacing:4px;
             padding-bottom:18px; border-bottom:1px solid var(--line); }
  .topline a { text-decoration:none; color:var(--grey); }
  .cover { text-align:center; padding:34px 0 36px; }
  .cover-frame { display:inline-block; border:3px double var(--line);
                 padding:34px 44px 30px; background:rgba(255,253,248,.55); }
  .title-strip { display:flex; flex-direction:row-reverse; justify-content:center;
                 align-items:center; gap:16px; }
  .title-strip .v { writing-mode:vertical-rl; text-orientation:upright;
                    font-weight:700; line-height:1; }
  .title-strip .main { font-size:clamp(40px,8vw,54px); letter-spacing:12px; }
  .title-strip .sub { font-size:clamp(30px,6vw,42px); letter-spacing:10px; }
  .cover .subtitle { margin-top:22px; color:var(--grey); font-size:14px; letter-spacing:6px; }
  .cover .author { margin-top:8px; color:var(--grey); font-size:13px; letter-spacing:3px; }
  .chapter { text-align:center; padding:36px 0 26px; }
  .chapter .hui { font-size:15px; color:var(--grey); letter-spacing:6px; }
  .chapter h1 { font-size:38px; font-weight:700; letter-spacing:8px; margin:14px 0 12px; }
  .chapter .source { font-size:13px; color:var(--grey); letter-spacing:2px; }
  .panel { margin:46px 0; }
  .panel img { display:block; width:100%; border:1px solid var(--hair); }
  .panel .cap { margin-top:14px; }
  .panel .no { display:inline-block; font-size:12px; color:var(--grey); letter-spacing:4px;
               border:1px solid var(--hair); padding:3px 10px; margin-bottom:10px; }
  .panel .orig { font-size:15.5px; line-height:1.9; }
  .panel .trans { font-size:13.5px; color:var(--grey); line-height:1.9; margin-top:6px; }
  .sect { margin:52px 0 0; border:1px solid var(--hair); border-left:3px solid var(--ink);
          padding:26px 30px; background:rgba(255,253,248,.65); }
  .sect .label { font-size:15px; font-weight:700; letter-spacing:6px; margin-bottom:14px; }
  .sect p { font-size:14.5px; line-height:2.0; }
  .sect p + p { margin-top:10px; }
  .sect ul { margin:10px 0 0 2px; list-style:none; }
  .sect li { font-size:14px; line-height:1.9; padding-left:1em; text-indent:-1em; }
  .sect li::before { content:"· "; color:var(--grey); }
  .pager { display:flex; justify-content:space-between; margin-top:56px; padding-top:22px;
            border-top:1px solid var(--line); font-size:14px; color:var(--grey); letter-spacing:2px; }
  .pager a { text-decoration:none; color:var(--grey); }
  .pager span.off { opacity:.35; }
  footer { text-align:center; margin-top:60px; font-size:12px; color:var(--grey); letter-spacing:3px; }
'''

COVER_HTML = ('<div class="cover"><div class="cover-frame"><div class="title-strip">'
              '<span class="v main">资治通鉴</span><span class="v sub">连环画</span>'
              '</div></div><div class="subtitle">白描敷彩 · 以画为鉴</div>'
              '<div class="author">司马光 原著 · 第一辑</div></div>')


def esc(s):
    return H.escape(s or '', quote=False)


def inline(s):
    s = esc(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    return s


def render_block(lines):
    """md 行组 → html：- 行成 <ul>，其余成 <p>，空行分段，跳过表格行。"""
    out, para, items = [], [], []
    def flush_para():
        if para:
            out.append('<p>' + ''.join(inline(x) for x in para) + '</p>')
            para.clear()
    def flush_items():
        if items:
            out.append('<ul>' + ''.join('<li>%s</li>' % inline(x) for x in items) + '</ul>')
            items.clear()
    for ln in lines:
        s = ln.strip()
        if not s:
            flush_para(); flush_items(); continue
        if s.startswith('- '):
            flush_para(); items.append(s[2:]); continue
        if s.startswith('|'):
            continue
        flush_items(); para.append(s)
    flush_para(); flush_items()
    return ''.join(out)


def parse_story_md(path):
    md = open(path, encoding='utf-8').read()
    title, intro, secs, cur = '', [], {}, None
    for ln in md.split('\n'):
        if ln.startswith('# ') and not title:
            title = ln[2:].strip()
            continue
        if ln.startswith('## '):
            cur = ln[3:].strip()
            secs.setdefault(cur, [])
            continue
        if cur is None:
            if ln.strip():
                intro.append(ln.strip())
        else:
            secs[cur].append(ln)
    panels = []
    for ln in secs.get('组画清单', []):
        s = ln.strip()
        if not s.startswith('|') or '---' in s or s.startswith('| 画'):
            continue
        cells = [c.strip() for c in s.strip('|').split('|')]
        if len(cells) >= 3 and cells[0].endswith('.jpg'):
            panels.append((cells[0], cells[1], cells[2],
                           cells[3] if len(cells) >= 4 else ''))
    return title, ' / '.join(intro), secs, panels


def story_page(vol_label, folder, title, intro, secs, panels, prev, next_,
               rel_index, cover=False, hui=None, footer_note=None,
               book_index=None):
    parts = []
    parts.append('<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="UTF-8">\n'
                 '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
                 '<title>%s</title>\n<style>%s</style>\n</head>\n<body>\n<div class="book">'
                 % (esc(title), CSS))
    parts.append('<div class="topline"><a href="%s">连环画画库</a> · %s</div>'
                 % (rel_index, esc(vol_label)))
    if cover:
        parts.append(COVER_HTML)
    name = title.split('·')[-1].strip() if '·' in title else title
    src_div = ('<div class="source">%s</div>' % esc(intro)) if intro.strip() else ''
    parts.append('<div class="chapter"><div class="hui">%s</div><h1>%s</h1>%s</div>'
                 % (esc(hui or vol_label), esc(name), src_div))
    for fn, scene, insc, baihua in panels:
        img = os.path.join(folder, fn)
        if not os.path.exists(img):
            print('  ! 缺图跳过:', fn)
            continue
        no = fn.rsplit('.', 1)[0]
        m = re.match(r'(\d+)-(.+)', no)
        label = ('其%s · %s' % (m.group(1), m.group(2))) if m else no
        parts.append('<div class="panel"><img src="%s" alt="%s"><div class="cap">'
                     '<span class="no">%s</span><div class="orig">%s</div>'
                     % (esc(fn), esc(no), esc(label), inline(insc)))
        trans = baihua or scene
        if trans:
            parts.append('<div class="trans">%s</div>' % inline(trans))
        parts.append('</div></div>')
    skip = {'组画清单', '制作说明'}
    for name_sec, lines in secs.items():
        if name_sec in skip:
            continue
        body = render_block(lines)
        if not body:
            continue
        parts.append('<div class="sect"><div class="label">%s</div>%s</div>'
                     % (esc(name_sec), body))
    toc = book_index or rel_index
    left = ('<a href="%s">← %s</a>' % (prev[1], esc(prev[0]))) if prev else \
           ('<a href="%s">← 本书目录</a>' % toc)
    right = ('<a href="%s">%s →</a>' % (next_[1], esc(next_[0]))) if next_ else \
            '<a href="%s">本书目录 →</a>' % toc
    parts.append('<div class="pager">%s%s</div>' % (left, right))
    parts.append('<footer>%s</footer></div>\n</body>\n</html>'
                 % esc(footer_note or (vol_label + ' · 连环画画库 · 以画为鉴')))
    return ''.join(parts)


def make_thumb(src, dst, size=180):
    from PIL import Image
    try:
        im = Image.open(src)
        im.thumbnail((size, size))
        im.save(dst, 'JPEG', quality=82)
    except Exception as e:
        print('  ! 缩略图跳过（文件可能正被并行写入）:', os.path.basename(src), e)


def build_volume(series_dir, md_name, vol_label, rel_index='../../index.html',
                 cover=False, hui_prefix=None, footer_note=None,
                 book_index=None):
    """生成一卷所有回页/册页，返回 [(文件夹, 显示名, 链接, 缩略图)]。"""
    entries = []
    for d in sorted(os.listdir(series_dir)):
        folder = os.path.join(series_dir, d)
        md_path = os.path.join(folder, md_name)
        if not os.path.isdir(folder) or not os.path.exists(md_path):
            continue
        title, intro, secs, panels = parse_story_md(md_path)
        have = [p for p, _s, _i, _b in panels
                if os.path.exists(os.path.join(folder, p))]
        if not panels or len(have) != len(panels):
            print('  跳过（未完成）: %s（%d/%d 图）' % (d, len(have), len(panels)))
            continue
        entries.append((d, title, folder, intro, secs, panels))
    n = len(entries)
    for i, (d, title, folder, intro, secs, panels) in enumerate(entries):
        prev = next_ = None
        hui = None
        if hui_prefix:
            num = d.split('-', 1)[0]
            hui = '第 %s 回' % HUAN.get(num, num) if hui_prefix == '通鉴' else None
            if hui is None:
                hui = hui_prefix
        if i > 0:
            p = entries[i - 1]
            prev = (p[0].split('-', 1)[-1], '../%s/%s.html' % (p[0], p[0]))
        if i < n - 1:
            nx = entries[i + 1]
            next_ = (nx[0].split('-', 1)[-1], '../%s/%s.html' % (nx[0], nx[0]))
        page = story_page(vol_label, folder, title, intro, secs, panels,
                          prev, next_, rel_index=rel_index, cover=cover,
                          hui=hui, footer_note=footer_note,
                          book_index=book_index)
        out = os.path.join(folder, d + '.html')
        with open(out, 'w', encoding='utf-8') as f:
            f.write(page)
        print('  回页:', os.path.relpath(out, ROOT))
        for fn, _s, _i, _b in panels:
            if os.path.exists(os.path.join(folder, fn)):
                dst = os.path.join(THUMBS, d + '.jpg')
                make_thumb(os.path.join(folder, fn), dst)
                break
    return [(d, d.split('-', 1)[-1], d + '/' + d + '.html',
             os.path.join(THUMBS, d + '.jpg'))
            for d, *_ in entries]


def parse_tongjian_plan():
    """解析 资治通鉴/总览.md 的回目表 → [(回号, 回名, 状态, 链接|None)]。"""
    path = os.path.join(ROOT, '资治通鉴', '总览.md')
    rows, cn = [], ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九',
                    '十', '十一', '十二', '十三', '十四', '十五', '十六',
                    '十七', '十八', '十九', '二十', '二十一', '二十二',
                    '二十三', '二十四', '二十五', '二十六', '二十七',
                    '二十八', '二十九', '三十']
    if not os.path.exists(path):
        return rows
    tj_dir = os.path.join(ROOT, '资治通鉴')
    for ln in open(path, encoding='utf-8'):
        s = ln.strip()
        if not s.startswith('|') or '---' in s or ('回' in s and '故事' in s and '状态' in s):
            continue
        cells = [c.strip() for c in s.strip('|').split('|')]
        if len(cells) < 4 or not cells[0].startswith('第'):
            continue
        hui, name = cells[0], re.sub(r'（.*?）', '', cells[1])
        try:
            num = cn.index(hui.replace('第', '').replace('回', ''))
        except ValueError:
            num = 0
        link = None
        # 优先生成器回页（文件夹内 NN-回名.html），退回系列根旧页
        for d in sorted(os.listdir(tj_dir)):
            fp = os.path.join(tj_dir, d, d + '.html')
            if os.path.isfile(fp) and d.startswith('%02d-' % num if num else 'zzz'):
                link = '资治通鉴/' + d + '/' + d + '.html'
                break
        if not link:
            for cand in sorted(os.listdir(tj_dir)):
                if cand.startswith('%02d-' % num if num else 'zzz') and cand.endswith('.html'):
                    link = '资治通鉴/' + cand
        rows.append((hui, name, cells[3], link))
    return rows


def book_cover(strip_main, strip_sub, subtitle, author, href):
    """书架页里的一本书：双列竖排书名书封。"""
    return ('<a href="%s" style="text-decoration:none;color:inherit" '
            'onmouseover="this.style.background=\'rgba(0,0,0,.03)\'" '
            'onmouseout="this.style.background=\'none\'">'
            '<div style="display:inline-block;border:3px double var(--line);'
            'padding:30px 40px 26px;background:rgba(255,253,248,.55);'
            'min-height:300px">'
            '<div style="display:flex;flex-direction:row-reverse;justify-content:center;'
            'align-items:flex-start;gap:14px">'
            '<span style="writing-mode:vertical-rl;text-orientation:upright;'
            'font-weight:700;line-height:1;font-size:clamp(38px,7vw,50px);'
            'letter-spacing:11px">%s</span>'
            '<span style="writing-mode:vertical-rl;text-orientation:upright;'
            'font-weight:700;line-height:1;font-size:clamp(28px,5vw,38px);'
            'letter-spacing:9px;color:var(--grey)">%s</span>'
            '</div></div>'
            '<div style="margin-top:14px;font-size:13px;color:var(--grey);'
            'letter-spacing:4px">%s</div>'
            '<div style="margin-top:6px;font-size:12px;color:var(--grey);'
            'letter-spacing:2px">%s</div></a>'
            % (href, esc(strip_main), esc(strip_sub), esc(subtitle), esc(author)))


def build_book_index(path, rel_back, book_title, strip_main, strip_sub,
                     subtitle, author, entries, entries_label,
                     footer_note, note=None, plan_rows=None):
    """单本书目录页：书封 + 全部回目/册目（含制作中条目）+ 回书架。"""
    parts = ['<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="UTF-8">\n'
             '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
             '<title>%s · 目录</title>\n<style>%s</style>\n</head>\n<body>\n'
             '<div class="book">' % (esc(book_title), CSS)]
    parts.append('<div class="topline"><a href="%s">连环画画库</a> · %s</div>'
                 % (rel_back, esc(book_title)))
    parts.append('<div class="cover"><div class="cover-frame"><div class="title-strip">'
                 '<span class="v main">%s</span><span class="v sub">%s</span>'
                 '</div></div><div class="subtitle">%s</div>'
                 '<div class="author">%s</div></div>'
                 % (esc(strip_main), esc(strip_sub), esc(subtitle), esc(author)))
    if note:
        parts.append('<div style="text-align:center;font-size:12.5px;color:var(--grey);'
                     'letter-spacing:2px;margin:0 0 34px">%s</div>' % esc(note))

    def head(no, name, cnt):
        return ('<div style="margin-top:40px"><div style="font-size:12px;'
                'color:var(--grey);letter-spacing:4px;padding-bottom:10px;'
                'border-bottom:2px solid var(--line)">%s</div>'
                '<div style="display:flex;justify-content:space-between;'
                'align-items:baseline;margin:16px 0 8px">'
                '<div style="font-size:24px;font-weight:700;letter-spacing:6px">%s</div>'
                '<div style="font-size:12px;color:var(--grey);letter-spacing:2px">%s</div>'
                '</div></div>' % (no, esc(name), cnt))

    if plan_rows is not None:
        # 通鉴：用总览计划（含制作中），按辑分章
        groups = [('第一辑 · 战国秦汉晋（全十回）', 1, 10),
                  ('第二辑 · 汉末至南北朝（第十一至二十回）', 11, 20),
                  ('第三辑 · 隋唐五代（第二十一至三十回）', 21, 30)]
        cn_num = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                  '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八',
                  '十九', '二十', '二十一', '二十二', '二十三', '二十四', '二十五',
                  '二十六', '二十七', '二十八', '二十九', '三十']

        def hui_num(hui):
            try:
                return cn_num.index(hui.replace('第', '').replace('回', ''))
            except ValueError:
                return 0
        for gname, lo, hi in groups:
            rows = [r for r in plan_rows if lo <= hui_num(r[0]) <= hi]
            parts.append(head('目录', gname, '%d 回' % len(rows)))
            for hui, name, status, link in rows:
                label = '%s · %s' % (hui, name)
                if link:
                    # plan 链接是站根相对，本页在系列目录内——剥掉系列前缀
                    rel = link.split('/', 1)[1] if '/' in link else link
                    parts.append('<a href="%s" style="display:block;padding:11px 14px;'
                                 'border-bottom:1px solid var(--hair);text-decoration:none;'
                                 'font-size:15px;letter-spacing:2px" '
                                 'onmouseover="this.style.background=\'rgba(0,0,0,.03)\'" '
                                 'onmouseout="this.style.background=\'none\'">%s</a>'
                                 % (rel, esc(label)))
                else:
                    parts.append('<div style="display:block;padding:11px 14px;'
                                 'border-bottom:1px solid var(--hair);font-size:15px;'
                                 'letter-spacing:2px;color:var(--grey);opacity:.55">%s'
                                 '<span style="font-size:12px;margin-left:12px">（%s）'
                                 '</span></div>' % (esc(label), esc(status or '制作中')))
    else:
        parts.append(head('目录', entries_label, '%d 篇' % len(entries)))
        for nn_name, disp, href, thumb in entries:
            # href 已是系列目录相对（NN/NN.html）；thumb 是绝对路径 → 相对系列目录加 ../
            t = os.path.relpath(thumb, ROOT)
            t = '../' + t
            parts.append('<a href="%s" style="display:flex;align-items:center;gap:16px;'
                         'padding:10px 14px;border-bottom:1px solid var(--hair);'
                         'text-decoration:none" '
                         'onmouseover="this.style.background=\'rgba(0,0,0,.03)\'" '
                         'onmouseout="this.style.background=\'none\'">'
                         '<img src="%s" style="width:44px;height:44px;object-fit:cover;'
                         'border:1px solid var(--hair);flex:none">'
                         '<span style="font-size:15px;letter-spacing:2px">%s</span></a>'
                         % (href, t, esc(disp)))

    parts.append('<div class="pager"><a href="%s">← 书架</a>'
                 '<a href="%s">翻开第一篇 →</a></div>'
                 % (rel_back, entries[0][2] if entries else rel_back))
    parts.append('<footer>%s</footer></div>\n</body>\n</html>'
                 % esc(footer_note))
    with open(path, 'w', encoding='utf-8') as f:
        f.write(''.join(parts))
    print('  book index:', os.path.relpath(path, ROOT))


def build_index(chengyu_list, xiaohua_list, tj_rows):
    parts = []
    parts.append('<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="UTF-8">\n'
                 '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
                 '<title>资治通鉴连环画 · 连环画画库</title>\n<style>%s</style>\n'
                 '</head>\n<body>\n<div class="book">' % CSS)
    parts.append('''
  <div style="text-align:center;padding:36px 0 40px;border-bottom:1px solid var(--line)">
    <div style="display:inline-block;border:3px double var(--line);padding:34px 44px 30px;background:rgba(255,253,248,.55)">
      <div style="display:flex;flex-direction:row-reverse;justify-content:center;align-items:center;gap:16px">
        <span style="writing-mode:vertical-rl;text-orientation:upright;font-weight:700;line-height:1;font-size:clamp(40px,8vw,54px);letter-spacing:12px">资治通鉴</span>
        <span style="writing-mode:vertical-rl;text-orientation:upright;font-weight:700;line-height:1;font-size:clamp(30px,6vw,42px);letter-spacing:10px">连环画</span>
      </div>
    </div>
    <div style="margin-top:22px;color:var(--grey);font-size:14px;letter-spacing:6px">白描敷彩 · 以画为鉴</div>
    <div style="margin-top:8px;color:var(--grey);font-size:13px;letter-spacing:3px">司马光 原著 · 连环画画库 · 三卷</div>
  </div>''')

    def vol_head(no, name, note):
        return ('<div style="margin-top:56px"><div style="font-size:12px;color:var(--grey);'
                'letter-spacing:4px;padding-bottom:10px;border-bottom:2px solid var(--line)">'
                '%s</div><div style="display:flex;justify-content:space-between;'
                'align-items:baseline;margin:16px 0 8px"><div style="font-size:26px;'
                'font-weight:700;letter-spacing:6px">%s</div><div style="font-size:12px;'
                'color:var(--grey);letter-spacing:2px">%s</div></div>' % (no, name, note))

    parts.append(vol_head('书架 · 三本', '连环画画库', '点击书封开卷 · 全站 %d 篇'
                          % (len(tj_rows) + len(chengyu_list) + len(xiaohua_list))))
    parts.append('<div style="display:flex;flex-wrap:wrap;justify-content:center;'
                 'gap:56px;padding:20px 0 10px">')
    parts.append(book_cover('资治通鉴', '连环画', '白描敷彩 · 峄山碑篆印 · 三辑三十回',
                            '司马光 原著', '资治通鉴/目录.html'))
    parts.append(book_cover('成语故事', '水墨组画', '水墨宣纸 · 浓淡相生 · %d 册'
                            % len(chengyu_list), '古代寓言', '成语故事/目录.html'))
    parts.append(book_cover('笑林广记', '笑话组画', '水墨笑话 · 一图一捧腹 · %d 册'
                            % len(xiaohua_list), '古代笑话', '笑林广记/目录.html'))
    parts.append('</div>')

    parts.append('''
  <div class="sect" style="margin-top:64px"><div class="label">关于本画库</div>
  <p>以 AI 绘制传统连环画：人物场景一致卡锁形，底图无字，题款以方正清刻本悦宋程序合成（竖排右起、无标点），资治通鉴卷钤峄山碑篆体「资治通鉴」朱印，逐幅经视觉模型逐字校验后上架。原文取自古籍开源语料（资治通鉴：daizhigev20 底本）。</p>
  <p>本站由 GitHub Pages 托管 · 图像生成 aicloud-seedream · 生成与校验工具链随仓库开源。</p></div>''')
    parts.append('<footer>资治通鉴连环画 · 连环画画库 · 以画为鉴</footer>'
                 '</div>\n</body>\n</html>')
    with open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(''.join(parts))
    print('  index.html')


def main():
    os.makedirs(THUMBS, exist_ok=True)
    tj_dir = os.path.join(ROOT, '资治通鉴')
    print('== 卷一 资治通鉴')
    tj_list = build_volume(tj_dir, '故事.md',
                           '资治通鉴连环画', rel_index='../../index.html', cover=True,
                           hui_prefix='通鉴',
                           footer_note='资治通鉴连环画 · 白描敷彩绘制 · 题款程序合成 · 峄山碑篆体印',
                           book_index='../目录.html')
    print('== 卷二 成语故事')
    chengyu = build_volume(os.path.join(ROOT, '成语故事'), '故事.md', '成语故事 · 水墨组画',
                           book_index='../目录.html')
    print('== 卷三 笑林广记')
    xiaohua = build_volume(os.path.join(ROOT, '笑林广记'), '笑话.md', '笑林广记 · 笑话组画',
                           book_index='../目录.html')
    tj = parse_tongjian_plan()
    print('== 三本书目录页')
    build_book_index(os.path.join(tj_dir, '目录.html'), '../index.html',
                     '资治通鉴连环画', '资治通鉴', '连环画',
                     '白描敷彩 · 以画为鉴', '司马光 原著 · 三辑三十回',
                     tj_list, '回目', '资治通鉴连环画 · 以画为鉴',
                     plan_rows=tj)
    build_book_index(os.path.join(ROOT, '成语故事', '目录.html'), '../index.html',
                     '成语故事 · 水墨组画', '成语故事', '水墨组画',
                     '水墨宣纸 · 浓淡相生', '古代寓言 · %d 册' % len(chengyu),
                     chengyu, '册目', '成语故事 · 水墨组画')
    build_book_index(os.path.join(ROOT, '笑林广记', '目录.html'), '../index.html',
                     '笑林广记 · 笑话组画', '笑林广记', '笑话组画',
                     '水墨笑话 · 一图一捧腹', '古代笑话 · %d 册' % len(xiaohua),
                     xiaohua, '册目', '笑林广记 · 笑话组画',
                     note='每册二至五幅，合幕题款覆盖原文全篇')
    print('== index.html 书架（通鉴 %d 回页 · 成语 %d 册 · 笑话 %d 册）'
          % (len(tj_list), len(chengyu), len(xiaohua)))
    build_index(chengyu, xiaohua, tj)
    print('DONE 通鉴 %d 回 · 成语 %d 册 · 笑话 %d 册' % (len(tj_list), len(chengyu), len(xiaohua)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
