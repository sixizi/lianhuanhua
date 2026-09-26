# -*- coding: utf-8 -*-
"""check_inscription.py - 用网关视觉模型转写/描述水墨画，校验生成图里的题款文字。

用法:
    python3 check_inscription.py <图片> ...                     # 全图：转写文字+简述画面
    python3 check_inscription.py --crop <图片> ...               # 裁右上角题款区（原生分辨率）逐字转写
    python3 check_inscription.py --describe <图片> ...           # 只描述画面内容/构图/风格
    可选: -m aicloud-kimi  -k 密钥文件  --crop-w 1000 --crop-h 1500
    系列规则（2026-09-26）：校验模型只用 aicloud-*。aicloud-kimi 视觉可用，设为默认；
    aicloud-glm 实测 400 不收图（chat-only）；claude 系列勿再用于校验。

原理: 整幅 2K 画直送会触发视觉入口降采样（claude 实测长边压到 1568px），竖排小字必糊。
--crop 裁出长边<=1500 的题款局部，原像素送检，绕过降采样。密钥解析与 gen_image 相同。
"""
import argparse
import base64
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_image as g

Q_FULL = ('请先逐字转写这幅水墨画中的全部文字（题款、印章、落款），'
          '严格按画中书写的原文输出，无法辨认的字用□标出，不要猜；'
          '然后用一两句话描述画面内容。')
Q_CROP = ('这是水墨画题款区域的裁剪截图。题款为竖排文字，从右往左逐列阅读。'
          '请逐字转写截图中的全部文字，无法辨认的字用□标出，不要猜，不要解释；'
          '图中为简体字形时请原样输出简体，不要转换成繁体。')
Q_DESC = ('用三句话描述这幅水墨画的画面内容、构图与风格。不要转写文字。')


def ocr(base, tk, model, path, question, mt):
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('ascii')
    mime = 'image/png' if path.lower().endswith('.png') else 'image/jpeg'
    body = {'model': model, 'max_tokens': mt, 'messages': [
        {'role': 'user', 'content': [
            {'type': 'text', 'text': question},
            {'type': 'image_url',
             'image_url': {'url': 'data:' + mime + ';base64,' + b64}}]}]}
    out, code = g.http(base, tk, 'POST', '/v1/chat/completions', body, timeout=120)
    if code != 200:
        return 'HTTP ' + str(code) + ' | ' + out[:200]
    j = json.loads(out)
    ch = (j.get('choices') or [{}])[0]
    msg = ch.get('message') or {}
    content = msg.get('content')
    if not content:
        content = '(empty content; finish=' + str(ch.get('finish_reason')) + ')'
    return content.strip()


def crop_top(path, cw, ch, side):
    from PIL import Image
    im = Image.open(path).convert('RGB')
    w, h = im.size
    x0 = max(0, w - cw) if side == 'right' else 0
    box = (x0, 0, x0 + min(cw, w), min(h, ch))
    out = path.rsplit('.', 1)[0] + '-crop.png'
    im.crop(box).save(out)
    return out


def main():
    ap = argparse.ArgumentParser(description='校验水墨画中题跋文字')
    ap.add_argument('images', nargs='+', help='要校验的图片路径')
    ap.add_argument('-m', '--model', default='aicloud-kimi',
                    help='校验模型（系列规则只用 aicloud-*；默认 kimi，二意见 qwen；glm 不收图、glm-flash 认不出字）')
    ap.add_argument('-k', '--key-file', default=None,
                    help='密钥文件（缺省用脚本旁 .aigw_key）')
    ap.add_argument('--crop', action='store_true',
                    help='裁顶部题款区（原生分辨率）送检')
    ap.add_argument('--crop-side', choices=['right', 'left'], default='right',
                    help='裁左半还是右半（默认 right）')
    ap.add_argument('--crop-w', type=int, default=1000)
    ap.add_argument('--crop-h', type=int, default=1500)
    ap.add_argument('--describe', action='store_true', help='只描述画面')
    ap.add_argument('--max-tokens', type=int, default=4000,
                    help='max_tokens（思考型模型如 kimi 需 4000+，小了会被思考吃空）')
    ap.add_argument('--question', default=None, help='覆盖默认提问文本')
    ap.add_argument('--env', choices=['prod', 'test'], default='prod')
    a = ap.parse_args()

    base, tk, src = g.resolve_creds(a)
    print('base:', base, '| key src:', src, '| vlm:', a.model)
    if a.crop:
        try:
            import PIL  # noqa: F401
        except ImportError:
            print('PIL 不可用，请先: pip3 install --user pillow')
            return 1
    for p in a.images:
        print('--- ' + os.path.basename(p))
        if a.crop:
            c = crop_top(p, a.crop_w, a.crop_h, a.crop_side)
            print('    [crop-' + a.crop_side + ' ' + str(a.crop_w) + 'x' + str(a.crop_h) + ']')
            print(ocr(base, tk, a.model, c, a.question or Q_CROP, a.max_tokens))
            os.unlink(c)
        elif a.describe:
            print(ocr(base, tk, a.model, p, a.question or Q_DESC, a.max_tokens))
        else:
            print(ocr(base, tk, a.model, p, a.question or Q_FULL, a.max_tokens))
    return 0


if __name__ == '__main__':
    sys.exit(main())
