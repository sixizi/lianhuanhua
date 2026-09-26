# -*- coding: utf-8 -*-
"""run_tongjian_batch.py - 资治通鉴连环画 02-10 回总调度（2026-09-26）。

串行依次执行 资治通鉴/02..10 各回 gen_batch.py（底图 + 合成题款），
失败场景解析 DONE 行 fail=[...] 自动重试一次（同提示词随机重摇）。
串行执行避免打爆 seedream 部署触发 429 冷却（与笑话批次并行时偶发
429 属预期，exit 3 的场景由重试收口）。

用法: python3 run_tongjian_batch.py [回目子串 ...]   # 无参数 = 全部九回
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SERIES = os.path.join(HERE, '资治通鉴')
STORIES = ['02-商鞅变法', '03-马陵道', '04-完璧归赵', '05-负荆请罪',
           '06-荆轲刺秦', '07-大泽乡', '08-鸿门宴', '09-背水一战',
           '10-淝水之战']


def run_script(script, only=None):
    cmd = [sys.executable, script] + (only or [])
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True)
    buf = []
    for ln in p.stdout:
        print(ln, end='', flush=True)
        buf.append(ln)
    p.wait()
    return p.returncode, ''.join(buf)


def failed_scenes(out):
    tail = out.split('DONE')[-1]
    names = re.findall(r"'([^']+)'", tail)
    return sorted(set(n.rsplit('-', 1)[0] for n in names if n))


def process(script, label, only=None):
    code, out = run_script(script, only)
    if code == 0:
        return []
    scenes = failed_scenes(out)
    print('### ' + label + ' FAILED scenes: ' + str(scenes), flush=True)
    still = []
    for s in scenes:
        print('### RETRY ' + label + ' / ' + s, flush=True)
        c2, _ = run_script(script, [s])
        if c2 != 0:
            still.append(label + '/' + s)
    return still


def main():
    only = sys.argv[1:]
    all_failed = []
    for st in STORIES:
        if only and not any(s in st for s in only):
            continue
        script = os.path.join(SERIES, st, 'gen_batch.py')
        if not os.path.exists(script):
            continue
        print('##### 第' + st.split('-')[0] + '回 ' + st.split('-')[1], flush=True)
        all_failed += process(script, st)
    print('SUMMARY failed=' + str(all_failed), flush=True)
    return 1 if all_failed else 0


if __name__ == '__main__':
    sys.exit(main())
