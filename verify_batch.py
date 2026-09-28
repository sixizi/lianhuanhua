# -*- coding: utf-8 -*-
"""verify_batch.py - 批量逐字校验（规则 2 自动化，2026-09-26 v2）。

直接加载各故事 gen_batch.py 与 笑林广记/jokes_batch.py 的 INSCRIPTIONS/SEAL
作为标准答案，逐幅在原生分辨率裁剪（右半幅 1000x1500）上 OCR，去空白后与
期望题款做包含比对（列序右起=阅读序）。

校验阶梯（v2，按 2026-09-26 批次教训加固）：
  1) aicloud-kimi 读（5000→9000 重试思考吃空）
  2) 不过 → aicloud-qwen + Q_EXACT 原样字形指令（kimi 偶发繁体口音/空回）

用法:
    python3 verify_batch.py [story-substring ...]   # 无参数 = 全部系列
    python3 verify_batch.py 三家分晋                 # 只校验该故事
系列扫描：成语故事（STORIES 硬清单）+ 笑林广记（jokes_batch）+ 资治通鉴（*/gen_batch.py glob）
"""
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_inscription as ci  # noqa: E402
import gen_image as g  # noqa: E402

CHENGYU = os.path.join(HERE, '成语故事')
STORIES = ['02-守株待兔', '03-刻舟求剑', '04-掩耳盗铃', '05-滥竽充数',
           '06-画蛇添足', '07-狐假虎威', '08-揠苗助长', '09-自相矛盾',
           '10-南辕北辙', '11-塞翁失马']
JOKES_SCRIPT = os.path.join(HERE, '笑林广记', 'jokes_batch.py')

Q_EXACT = ('严格按图中字形逐字转写全部文字（图中是简体字形，请原样输出每个字，'
           '不要转换成繁体，不要解释，不要补充）。')


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def norm(t):
    return re.sub(r'\s+', '', t or '')


def ocr_crop(base, tk, final, model='aicloud-kimi', question=None,
             mts=(5000, 9000)):
    crop = ci.crop_top(final, 1000, 1500, 'right')
    got = ''
    try:
        for mt in mts:
            got = ci.ocr(base, tk, model, crop, question or ci.Q_CROP, mt)
            if got and '(empty' not in got and not got.startswith('HTTP '):
                break
    finally:
        if os.path.exists(crop):
            os.unlink(crop)
    return got


def verify_one(base, tk, final, cols, seal):
    if not os.path.exists(final):
        return 'MISSING', ''
    got = ocr_crop(base, tk, final)
    n = norm(got)
    expect = norm(''.join(cols))
    if expect and expect in n:
        return ('PASS' if norm(seal) in n else 'PASS-无印读数'), got
    # 二意见（规则 2）：qwen + 原样字形指令
    got2 = ocr_crop(base, tk, final, model='aicloud-qwen',
                    question=Q_EXACT, mts=(8000,))
    n2 = norm(got2)
    if expect in n2:
        return ('PASS' if norm(seal) in n2 else 'PASS-无印读数'), got2
    return 'FAIL', (got + ' | qwen: ' + got2)


def main():
    only = sys.argv[1:]
    base, tk, src = g.resolve_creds(type('A', (), {
        'key_file': None, 'env': 'prod'})())
    print('base:', base, '| key src:', src, '| vlm: kimi→qwen 阶梯', flush=True)
    tasks = []
    for st in STORIES:
        if only and not any(s in st for s in only):
            continue
        script = os.path.join(CHENGYU, st, 'gen_batch.py')
        m = load_module(script, 'spec_' + st[:2])
        folder = os.path.join(CHENGYU, st)
        for name, cols in m.INSCRIPTIONS:
            tasks.append((st, os.path.join(folder, name + '.jpg'), cols,
                          m.SEAL))
    if not only or '笑' in only or any(
            os.path.isdir(os.path.join(HERE, '笑林广记', j)) and
            any(s in j for s in only)
            for j in os.listdir(os.path.join(HERE, '笑林广记'))):
        mj = load_module(JOKES_SCRIPT, 'spec_jokes')
        for jname, scenes in mj.JOKES:
            if only and not any(s in jname for s in only):
                continue
            for sname, prompt, cols in scenes:
                tasks.append(('笑林广记',
                              os.path.join(HERE, '笑林广记', jname,
                                           sname + '.jpg'),
                              cols, mj.SEAL))

    for series_dir, series_tag in ((os.path.join(HERE, '资治通鉴'), 'spec_tj_'),
                                    (os.path.join(HERE, '论语'), 'spec_ly_')):
        if not os.path.isdir(series_dir):
            continue
        for d in sorted(os.listdir(series_dir)):
            script = os.path.join(series_dir, d, 'gen_batch.py')
            if not os.path.isfile(script):
                continue
            if only and not any(s in d for s in only):
                continue
            mt = load_module(script, series_tag + d[:2])
            for name, cols in mt.INSCRIPTIONS:
                tasks.append((d,
                              os.path.join(series_dir, d, name + '.jpg'),
                              cols, mt.SEAL))

    ok, bad = [], []
    for story, final, cols, seal in tasks:
        status, got = verify_one(base, tk, final, cols, seal)
        tag = story + '/' + os.path.basename(final)
        print('--- ' + tag + ' : ' + status, flush=True)
        if status.startswith('PASS'):
            ok.append(tag)
        else:
            print('    读数: ' + norm(got)[:160], flush=True)
            print('    期望: ' + norm(''.join(cols)), flush=True)
            bad.append(tag + ' -> ' + status)
    print('SUMMARY pass=' + str(len(ok)) + ' bad=' + str(bad), flush=True)
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())
