# -*- coding: utf-8 -*-
"""compose_inscription.py - 在无字水墨底图上合成统一字体的竖排题款 + 朱红印章。

成语故事系列标准工具（2026-09-26 定标：题款一律程序合成，不再模型直题——
模型直题乱字不可控且各幅字体不一致；统一用方正清刻本悦宋 GB 简体实例）。

用法:
    python3 compose_inscription.py <底图> -c '右起第一列' -c '右起第二列' -s '印文四字' [-o 输出]
    缺省输出：<底图名>-题款.jpg；--in-place 直接覆盖底图

布局常量（2K 画幅，叶公好龙 02 已验证）: 字号 68、行距 pitch 88、右起第一列 x=1878、
列距 120、首字 y=130、印章 r=54 在末列（最左列）下方。印文四字按传统印序：
右列自上而下，再左列自上而下。墨色 (38,36,33)、朱红 (176,56,50)、印字 (247,242,235)。题款区干净度检查区域按列布局与印章位置自动推导。
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = os.path.expanduser('~/Library/Fonts/FZQKBYSJW--GB1-0.ttf')
FONT_FALLBACK = '/System/Library/Fonts/Supplemental/Songti.ttc'
INK = (38, 36, 33)
RED = (176, 56, 50)
PAPER = (247, 242, 235)


def load_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        for idx in (6, 4, 0):  # Songti SC Regular / STSong / Songti SC Black
            try:
                return ImageFont.truetype(FONT_FALLBACK, size, index=idx)
            except Exception:
                continue
    raise SystemExit('无可用中文字体')


def load_font_path(path, size):
    """按路径加载指定字体（如篆体印文字库），失败回退题款字体。"""
    try:
        return ImageFont.truetype(path, size)
    except Exception as e:
        print('印章字体加载失败(%s)，回退题款字体：%s' % (path, e))
        return load_font(size)


def draw_col(d, text, xc, y0, pitch, font, fill, size=68):
    for i, ch in enumerate(text):
        b = d.textbbox((0, 0), ch, font=font)
        w, h = b[2] - b[0], b[3] - b[1]
        x = xc - w / 2 - b[0]
        y = y0 + i * pitch - h / 2 - b[1]
        d.text((x, y), ch, font=font, fill=fill)
        # 「曰」补笔（2026-09-26）：本字体曰字中横仅约 4px 且偏右（刻本弱横），
        # 人眼/模型均难与日区分；合成时加画一条醒目浮空短横（同墨色）。
        if ch == '曰':
            yt = y + h * 0.42  # 对齐本字体弱横原位（bbox 顶约 40% 处），合成一条干净短横
            x1, x2 = x + w * 0.3, x + w * 0.7
            t = max(3, int(size * 0.06))
            for k in range(t):
                d.line([(x1, yt + k), (x2, yt + k)], fill=fill)


def draw_seal(d, font, xc, y, text):
    r = 54
    d.rounded_rectangle((xc - r, y, xc + r, y + 2 * r), radius=9, fill=RED)
    cells = [(xc + 27, y + 27), (xc + 27, y + 81),
             (xc - 27, y + 27), (xc - 27, y + 81)]
    for (cx, cy), ch in zip(cells, text):
        b = d.textbbox((0, 0), ch, font=font)
        w, h = b[2] - b[0], b[3] - b[1]
        d.text((cx - w / 2 - b[0], cy - h / 2 - b[1]), ch, font=font, fill=PAPER)


def title_area_clean(im, box):
    g = im.crop(box).convert('L')
    h = g.histogram()
    frac = sum(h[:128]) / (g.size[0] * g.size[1])
    print('题款区%s墨迹占比 %.4f' % (str(box), frac))
    return frac < 0.035


def main():
    ap = argparse.ArgumentParser(description='合成统一字体题款（系列标准）')
    ap.add_argument('image', help='无字底图路径')
    ap.add_argument('-c', '--col', action='append', required=True,
                    help='题款一列文字，按右起顺序重复 -c（如 -c 第一列 -c 第二列）')
    ap.add_argument('-s', '--seal', required=True, help='印文（四字）')
    ap.add_argument('-o', '--out', default=None,
                    help='输出路径（缺省 <底图名>-题款.jpg）')
    ap.add_argument('--in-place', action='store_true', help='覆盖底图')
    ap.add_argument('--size', type=int, default=68, help='字号（默认 68）')
    ap.add_argument('--pitch', type=int, default=88, help='行距（默认 88）')
    ap.add_argument('--xc-right', type=int, default=1878, help='右起第一列 x（默认 1878）')
    ap.add_argument('--col-gap', type=int, default=120, help='列距（默认 120）')
    ap.add_argument('--y0', type=int, default=130, help='首字 y（默认 130）')
    ap.add_argument('--seal-font', default=None,
                    help='印章字体路径（如篆体印文字库；缺省同题款字体）')
    ap.add_argument('--seal-size', type=int, default=40, help='印文字号（默认 40）')
    ap.add_argument('--force', action='store_true', help='跳过题款区干净度检查')
    a = ap.parse_args()

    im = Image.open(a.image).convert('RGB')
    if im.size != (2048, 2048):
        print('警告：画幅非 2048x2048（%sx%s），布局常量按 2K 设计，效果未验证'
              % im.size)

    cols = a.col
    xcs = [a.xc_right - i * a.col_gap for i in range(len(cols))]
    seal_y = a.y0 + (len(cols[-1]) - 1) * a.pitch + a.pitch // 2 + 60
    # 检查区域须覆盖最高列底部（长列 + 短末列印章场景）
    max_bottom = max(seal_y + 128,
                     a.y0 + max(len(c) for c in cols) * a.pitch + 60)
    region = (max(0, min(xcs) - 80), max(0, a.y0 - 40),
              im.size[0], min(im.size[1], max_bottom))
    if not a.force and not title_area_clean(im, region):
        print('题款区被画入内容（墨迹>=3.5%%），建议重新生成底图；或 --force 强行合成')
        return 2

    font = load_font(a.size)
    print('题款字体:', font.getname()[0])
    if a.seal_font:
        seal_font = load_font_path(a.seal_font, a.seal_size)
        print('印章字体:', seal_font.getname()[0])
    else:
        seal_font = load_font(a.seal_size)
    d = ImageDraw.Draw(im)
    for xc, text in zip(xcs, cols):
        if len(text) * a.pitch + a.y0 > 1900:
            print('警告：列「%s」过长可能超出画幅' % text)
        draw_col(d, text, xc, a.y0, a.pitch, font, INK, a.size)
    draw_seal(d, seal_font, xcs[-1], seal_y, a.seal)

    out = a.image if a.in_place else (
        a.out or (a.image.rsplit('.', 1)[0] + '-题款.' +
                  (a.image.rsplit('.', 1)[1] if '.' in a.image else 'jpg')))
    im.save(out, 'JPEG', quality=92)
    print('合成完成 ->', os.path.abspath(out), '|', os.path.getsize(out), 'bytes')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
