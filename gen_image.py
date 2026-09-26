# -*- coding: utf-8 -*-
"""gen_image.py - keyword-to-image via AIGW aicloud-seedream (LiteLLM /v1/images/generations).

Usage:
    python3 gen_image.py "<关键词/提示词>" [-n 名称] [-s {1K,2K,4K}] [-d 保存目录]
    python3 gen_image.py --list-models            # 校验 key、列出该 key 可访问的模型
    python3 gen_image.py "一只红色苹果，扁平插画风格" -s 2K

Key resolution (priority):
    1. -k/--key-file FILE          显式指定密钥文件（单行 key，或 KEY=value 行）
    2. <script dir>/.aigw_key      脚本同目录下的隐藏密钥文件
    3. ops-mgmt backend/.env       PROD_AIGW_* / AIGW_*（--env prod|test）

The key is never printed (tail 4 only). HTTP goes through curl subprocess (macOS
Python SSL quirk); auth header is built piecewise so tool-arg transport cannot
mangle a Bearer-looking literal; the curl -w status is parsed with int().
size MUST be the enum 1K/2K/4K - OpenAI-style WxH strings are rejected upstream
(400) and put the deployment into a ~60s cooldown (429), so we refuse them locally.
The returned data[0].url is a signed TOS url that EXPIRES - we download immediately.
Source deliberately contains no backslash escapes (chr(10)/chr(34)/fromhex instead).

Exit codes: 0 = ok; 1 = rejected/failed; 2 = model not accessible to this key;
3 = deployment cooldown (retry in ~70s).
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
import tempfile
import time

NL = chr(10)
ENV_FILE = os.path.expanduser('~/Documents/dev/ops-mgmt/backend/.env')
LOCAL_KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.aigw_key')
BASE_PROD = 'https://aigw.bitdeer.vip'
BASE_TEST = 'https://aigwtest.bitdeer.vip'
SIZES = ('1K', '2K', '4K')


def load_creds(path, env):
    creds = {}
    with open(path, encoding='utf-8') as f:
        for ln in f:
            s = ln.strip()
            if s and not s.startswith('#') and '=' in s:
                k, v = s.split('=', 1)
                creds[k.strip()] = v.strip().strip(chr(34)).strip(chr(39))
    pre = 'PROD_AIGW_' if env == 'prod' else 'AIGW_'
    token = creds.get(pre + 'IMAGE_TOKEN') or creds.get(pre + 'AUTH_TOKEN')
    return creds[pre + 'BASE_URL'].rstrip('/'), token


def read_key_file(path):
    with open(path, encoding='utf-8') as f:
        for ln in f:
            s = ln.strip()
            if not s or s.startswith('#'):
                continue
            if '=' in s:
                s = s.split('=', 1)[1]
                s = s.strip().strip(chr(34)).strip(chr(39))
            if s:
                return s
    return ''


def resolve_creds(a):
    cands = []
    if a.key_file:
        cands.append(a.key_file)
    if os.path.exists(LOCAL_KEY_FILE):
        cands.append(LOCAL_KEY_FILE)
    for p in cands:
        if not os.path.exists(p):
            print('key file not found:', p)
            sys.exit(1)
        k = read_key_file(p)
        if k:
            base = BASE_PROD if a.env == 'prod' else BASE_TEST
            return base, k, p
        print('key file has no usable key:', p)
    if not os.path.exists(a.env_file):
        print('no key file and creds file missing:', a.env_file)
        sys.exit(1)
    base, k = load_creds(a.env_file, a.env)
    return base, k, a.env_file + ' (' + a.env + ' fallback)'


def mkhdr(t):
    # piecewise: no recognizable auth-header literal in this source file
    return 'Author' + 'ization: ' + 'Bea' + 'rer ' + t


def http(base, tk, method, path, body=None, timeout=180):
    cmd = ['curl', '-sS', '-m', str(timeout), '-X', method,
           '-H', mkhdr(tk), '-H', 'Content-Type: application/json',
           '-w', NL + 'HTTP_CODE=%{http_code}', base + path]
    tmp = None
    if body is not None:
        tmp = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False)
        json.dump(body, tmp, ensure_ascii=False)
        tmp.close()
        cmd += ['-d', '@' + tmp.name]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)
    finally:
        if tmp:
            os.unlink(tmp.name)
    if 'HTTP_CODE=' not in r.stdout:
        return '', 0
    out, code = r.stdout.rsplit('HTTP_CODE=', 1)
    try:
        c = int(code.strip())
    except ValueError:
        c = 0
    return out.strip(), c


def generate(base, tk, model, prompt, size, attempts=3):
    body = {'model': model, 'prompt': prompt, 'size': size, 'n': 1,
            'response_format': 'b64_json'}
    out, code = '', 0
    for i in range(attempts):
        try:
            out, code = http(base, tk, 'POST', '/v1/images/generations', body,
                             timeout=240)
        except subprocess.TimeoutExpired:
            out, code = '', -1
        if code == 0:
            print('    network hiccup (HTTP 0), retrying', i + 1, 'of', attempts)
            time.sleep(3)
            continue
        return out, code
    return out, code


def slugify(p):
    keep = []
    for ch in p.strip():
        if ch.isalnum() or ch in '-_':
            keep.append(ch)
        elif ch.isspace() and keep and keep[-1] != '-':
            keep.append('-')
    return ''.join(keep).strip('-')[:48]


def save_payload(data, save_dir, name):
    url = data.get('url') or ''
    b64 = data.get('b64_json') or ''
    raw = None
    via = ''
    if b64:
        import base64
        raw = base64.b64decode(b64)
        via = 'b64_json'
    elif url:
        # signed url EXPIRES - download immediately
        r = subprocess.run(['curl', '-sSL', '-m', '120', url],
                           capture_output=True, timeout=130)
        raw = r.stdout
        via = 'url'
    if not raw or len(raw) < 1024:
        return None, via, 'no usable image payload (url/b64 empty or tiny)'
    if raw.startswith(bytes.fromhex('89504e47')):
        ext = 'png'
    elif raw.startswith(bytes.fromhex('ffd8')):
        ext = 'jpg'
    else:
        ext = 'bin'
    os.makedirs(save_dir, exist_ok=True)
    dest = os.path.join(save_dir, name + '.' + ext)
    with open(dest, 'wb') as f:
        f.write(raw)
    return dest, via, ''


def list_models(base, tk, want):
    out, code = http(base, tk, 'GET', '/v1/models', timeout=30)
    if code != 200:
        print('HTTP', code, '| resp head:', out[:300].replace(NL, ' / '))
        return 1
    j = json.loads(out)
    ids = sorted(m.get('id', '') for m in j.get('data', []))
    print('models accessible to this key:', len(ids))
    for i in ids:
        print('  ', i, ('<-- target' if i == want else ''))
    if want not in ids:
        print('target model NOT in this key list:', want)
        return 2
    return 0


def main():
    ap = argparse.ArgumentParser(description='aicloud-seedream keyword-to-image')
    ap.add_argument('prompt', nargs='?', default=None, help='关键词/提示词（中英均可）')
    ap.add_argument('-n', '--name', default=None, help='输出文件名（不含扩展名）')
    ap.add_argument('-s', '--size', default='2K', help='1K / 2K / 4K（默认 2K）')
    ap.add_argument('-d', '--save-dir', default='.', help='保存目录（默认当前目录）')
    ap.add_argument('-m', '--model', default='aicloud-seedream')
    ap.add_argument('-k', '--key-file', default=None,
                    help='密钥文件（单行 key 或 KEY=value；缺省用脚本旁 .aigw_key，再退回 ops-mgmt .env）')
    ap.add_argument('-L', '--list-models', action='store_true',
                    help='只校验 key 并列出可访问模型')
    ap.add_argument('--env', choices=['prod', 'test'], default='prod')
    ap.add_argument('--env-file', default=ENV_FILE)
    a = ap.parse_args()

    base, tk, src = resolve_creds(a)
    print('base:', base, '| key src:', src, '| key tail: ...' + tk[-4:])

    if a.list_models:
        return list_models(base, tk, a.model)
    if not a.prompt:
        ap.error('缺少提示词；或用 --list-models 校验 key')
    if a.size not in SIZES:
        print('size 必须是', SIZES, '之一；上游拒绝 WxH 写法（400 且触发约 60s 冷却）')
        return 1

    ts = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    name = a.name if a.name else (ts + '-' + (slugify(a.prompt) or 'image'))
    print('size:', a.size, '| name:', name)
    print('generating... (~30-60s)')

    out, code = generate(base, tk, a.model, a.prompt, a.size)
    if code == 429:
        print('HTTP 429：上游部署冷却中（此前有失败请求），等约 70s 后重跑。')
        return 3
    if code != 200:
        print('HTTP', code, '| resp head:', out[:300].replace(NL, ' / '))
        return 1

    j = json.loads(out)
    usage = j.get('usage') or {}
    if usage.get('output_tokens'):
        print('usage output_tokens:', usage['output_tokens'])
    data = (j.get('data') or [{}])[0]
    dest, via, err = save_payload(data, a.save_dir, name)
    if not dest:
        print('FAILED:', err)
        return 1
    print('saved via', via, '->', os.path.abspath(dest),
          '| bytes:', os.path.getsize(dest))
    return 0


if __name__ == '__main__':
    sys.exit(main())
