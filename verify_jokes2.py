# -*- coding: utf-8 -*-
"""verify_jokes2.py - jokes_batch2.py 系列逐字校验。

用法:
    python3 verify_jokes2.py                                  # 全量校验
    python3 verify_jokes2.py 71-射虎/03-兜脚射来 57-刚执 ...    # 只验指定幕/册（过滤参数）

裁剪策略（绕开视觉入口按长边降采样，长边须 <=1500）:
  - 题款最长列 <=15 字: 单次右上裁剪 1000x1500 原生送检
  - 单列 >=16 字: 上下两段裁剪（0..1054 / 1054..2048）分别送检后拼接
  - 多列布局要求每列 <=15 字（jokes_batch2.py 拆列后不变式），超限即断言报错
模型: aicloud-kimi 一读（max_tokens 9000 思考余量），不合再 aicloud-qwen 二读。
"""
import os
import re
import sys
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import check_inscription as ci
import gen_image as g

ns = {'__file__': os.path.join(BASE, 'jokes_batch2.py')}
exec(compile(open(os.path.join(BASE, 'jokes_batch2.py'), encoding='utf-8').read(),
             'j2', 'exec'), ns)
JOKES = ns['JOKES']
SEAL = ns['SEAL']

holder = type('A', (), {'key_file': None, 'env': 'prod'})()
base_url, tk, src = g.resolve_creds(holder)
print('base:', base_url, '| vlm: kimi->qwen', flush=True)

only = sys.argv[1:]


def norm(t):
    return re.sub(r'\s+', '', t or '')


def read_ocr(final, cols, model, mt):
    """按列布局裁剪并 OCR，返回拼接后的规范化读数。"""
    maxcol = max(len(c) for c in cols)
    if len(cols) > 1:
        # 多列布局不变式：每列须完全落进 1000x1500 单次裁剪
        assert 130 + maxcol * 88 <= 1500, ('多列超长，请拆列', cols)
    if 130 + maxcol * 88 <= 1500:
        crop = ci.crop_top(final, 1000, 1500, 'right')
        got = ci.ocr(base_url, tk, model, crop, ci.Q_CROP, mt)
        os.unlink(crop)
        return norm(got)
    # 单列长题款：上下两段（切点在字10/11之间的行距中点）
    im = Image.open(final)
    w, h = im.size
    x0 = w - 1000
    p1 = final + '-c1.png'
    p2 = final + '-c2.png'
    im.crop((x0, 0, w, 1054)).save(p1)
    im.crop((x0, 1054, w, h)).save(p2)
    n1 = norm(ci.ocr(base_url, tk, model, p1, ci.Q_CROP, mt))
    n2 = norm(ci.ocr(base_url, tk, model, p2, ci.Q_CROP, mt))
    os.unlink(p1)
    os.unlink(p2)
    return n1 + n2


ok, bad = [], []
total = 0
for jname, scenes in JOKES:
    folder = os.path.join(BASE, '笑林广记', jname)
    for sname, prompt, cols in scenes:
        sid = jname + '/' + sname
        if only and not any(t == sid or t == jname or t == sname for t in only):
            continue
        total += 1
        final = os.path.join(folder, sname + '.jpg')
        if not os.path.exists(final):
            bad.append(sid + ': MISSING')
            print(sid + ': MISSING', flush=True)
            continue
        expect = norm(''.join(cols))
        n = read_ocr(final, cols, 'aicloud-kimi', 9000)
        if expect in n:
            status = 'PASS' if norm(SEAL) in n else 'PASS-无印'
            ok.append(sid)
        else:
            n2 = read_ocr(final, cols, 'aicloud-qwen', 8000)
            if expect in n2:
                status = 'PASS(qwen)' if norm(SEAL) in n2 else 'PASS-无印'
                ok.append(sid)
            else:
                status = 'FAIL'
                bad.append(sid + ': FAIL')
        print(sid + ': ' + status, flush=True)

print('SUMMARY total=%d pass=%d fail=%d' % (total, len(ok), len(bad)), flush=True)
for b in bad:
    print('  BAD:', b, flush=True)
