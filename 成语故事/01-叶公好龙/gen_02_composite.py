# -*- coding: utf-8 -*-
"""02-天龙下凡 - 题款合成兜底方案。

背景：三轮模型直绘题款均未通过逐字校验（乱字/错字/列数错，opus 结构化复核确认）。
改用确定性路径：
1) 生成右上留白的无字水墨底图（至多重试 3 次，直到题款区干净）
2) PIL 用方正清刻本悦宋（~/Library/Fonts/FZQKBYSJW--GB1-0.ttf，GB 简体实例，
   所需 18 字零缺字）竖排合成题款两列，程序绘制朱红印章 —— 字字精确
3) 输出覆盖 02-天龙下凡.jpg；无字底图归档 drafts/

用法: python3 gen_02_composite.py
"""
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'gen_image.py')
FINAL = os.path.join(HERE, '02-天龙下凡.jpg')
DRAFTS = os.path.join(HERE, 'drafts')

STYLE = ('中国传统水墨画，宣纸质感，浓墨勾勒轮廓，淡墨渲染云雾层次，大面积留白，'
         '构图空灵，全画黑白灰为主，意境悠远')
SCENE = ('风云突变，一条鳞爪飞扬的真龙自天而降来到叶府，巨大的龙头从窗户探进屋内，'
         '龙目圆睁，龙须飘动，长长的龙尾绕过厅堂摆动，云雾在屋宇间翻腾涌动。'
         + STYLE + '。画面中不得出现任何文字、任何汉字、任何印章印鉴，'
         '右上角区域大面积留白，什么都不画。')

FONT_PATH = os.path.expanduser('~/Library/Fonts/FZQKBYSJW--GB1-0.ttf')
FONT_FALLBACK = '/System/Library/Fonts/Supplemental/Songti.ttc'
COL1 = '于是天龙闻而下之'
COL2 = '窥头于牖施尾于堂'
SEAL = '叶公好龙'
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


def gen_base():
    r = subprocess.run([sys.executable, GEN, SCENE, '-d', HERE,
                        '-n', '02-无字底图'])
    if r.returncode != 0:
        return None
    for ext in ('.jpg', '.jpeg', '.png'):
        p = os.path.join(HERE, '02-无字底图' + ext)
        if os.path.exists(p):
            return p
    return None


def title_area_clean(im):
    g = im.crop((1600, 90, 2048, 1010)).convert('L')
    h = g.histogram()
    frac = sum(h[:128]) / (g.size[0] * g.size[1])
    print('    题款区墨迹占比 %.4f' % frac, flush=True)
    return frac < 0.035


def draw_col(d, text, xc, y0, pitch, font, fill):
    for i, ch in enumerate(text):
        b = d.textbbox((0, 0), ch, font=font)
        w, h = b[2] - b[0], b[3] - b[1]
        d.text((xc - w / 2 - b[0], y0 + i * pitch - h / 2 - b[1]), ch,
               font=font, fill=fill)


def draw_seal(d, font):
    r = 54
    xc, y = 1758, 850
    d.rounded_rectangle((xc - r, y, xc + r, y + 2 * r), radius=9, fill=RED)
    # 传统印序：右列自上而下，再左列自上而下
    cells = [(xc + 27, y + 27), (xc + 27, y + 81),
             (xc - 27, y + 27), (xc - 27, y + 81)]
    for (cx, cy), ch in zip(cells, SEAL):
        b = d.textbbox((0, 0), ch, font=font)
        w, h = b[2] - b[0], b[3] - b[1]
        d.text((cx - w / 2 - b[0], cy - h / 2 - b[1]), ch, font=font, fill=PAPER)


def main():
    os.makedirs(DRAFTS, exist_ok=True)
    base = None
    for att in range(1, 4):
        print('=== 底图尝试', att, flush=True)
        p = gen_base()
        if not p:
            print('    生成失败')
            continue
        im = Image.open(p).convert('RGB')
        if title_area_clean(im):
            base = p
            break
        print('    右上题款区被画入内容，弃用重试', flush=True)
        shutil.move(p, os.path.join(
            DRAFTS, '02-无字底图-r%d%s' % (att, os.path.splitext(p)[1])))
    if not base:
        print('三次底图题款区均不干净，退出（exit 2）')
        return 2

    im = Image.open(base).convert('RGB')
    font = load_font(68)
    print('题款字体:', font.getname()[0], flush=True)
    d = ImageDraw.Draw(im)
    draw_col(d, COL1, 1878, 130, 88, font, INK)
    draw_col(d, COL2, 1758, 130, 88, font, INK)
    draw_seal(d, load_font(40))
    im.save(FINAL, 'JPEG', quality=92)
    print('合成完成 ->', FINAL, '|', os.path.getsize(FINAL), 'bytes', flush=True)

    shutil.move(base, os.path.join(
        DRAFTS, '02-无字底图' + os.path.splitext(base)[1]))
    print('底图归档 drafts/')
    return 0


if __name__ == '__main__':
    sys.exit(main())
