# -*- coding: utf-8 -*-
"""run_series_batch.py - 20 故事总调度（2026-09-26 全量开跑版）。

串行依次执行：
  1. 成语故事/02..11 各故事 gen_batch.py（40 幕底图 + 合成）
  2. 笑林广记/jokes_batch.py（10 幅笑话底图 + 合成）
失败场景自动重试一次（同一提示词随机重摇；仍失败记入 SUMMARY 人工处理）。

用法: python3 run_series_batch.py [story-substring ...]   # 无参数 = 全部
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHENGYU = os.path.join(HERE, '成语故事')
STORIES = ['02-守株待兔', '03-刻舟求剑', '04-掩耳盗铃', '05-滥竽充数',
           '06-画蛇添足', '07-狐假虎威', '08-揠苗助长', '09-自相矛盾',
           '10-南辕北辙', '11-塞翁失马']
JOKES_SCRIPT = os.path.join(HERE, '笑林广记', 'jokes_batch.py')


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
    """运行并自动重试失败场景一次；返回仍失败的场景列表。"""
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
        script = os.path.join(CHENGYU, st, 'gen_batch.py')
        print('##### 故事 ' + st, flush=True)
        all_failed += process(script, st)
    if not only or '笑' in (only or []):
        print('##### 笑林广记 10 幅', flush=True)
        all_failed += process(JOKES_SCRIPT, '笑林广记')
    print('SUMMARY failed=' + str(all_failed), flush=True)
    return 1 if all_failed else 0


if __name__ == '__main__':
    sys.exit(main())
