# -*- coding: utf-8 -*-
"""poll_batch.py - 阻塞等待通鉴批量收尾（每次调用盯 ~9.5 分钟）。
退出码 0 = 全部收尾；1 = 仍在运行（再调一次）；打印进度一行。
"""
import os
import subprocess
import sys
import time

ROOT = '/Users/qirong.liu/Library/CloudStorage/OneDrive-Personal/vibe/Hermes/imagefact/资治通鉴'
STORIES = ['02-商鞅变法', '03-马陵道', '04-完璧归赵', '05-负荆请罪',
           '06-荆轲刺秦', '07-大泽乡', '08-鸿门宴', '09-背水一战', '10-淝水之战']


def count(kind):
    n = 0
    for st in STORIES:
        d = os.path.join(ROOT, st)
        for f in os.listdir(d):
            if kind == 'final' and f.endswith('.jpg') and '底图' not in f and not f.startswith('drafts'):
                n += 1
            elif kind == 'base' and f.endswith('-底图.jpg'):
                n += 1
    return n


def alive():
    r = subprocess.run(['pgrep', '-f', 'run_tongjian_batch'], capture_output=True, text=True)
    return bool(r.stdout.strip())


deadline = time.time() + 575
while time.time() < deadline:
    fins, bases = count('final'), count('base')
    run = alive()
    print('finals=%d/38 bases=%d runner=%s' % (fins, bases, 'ON' if run else 'OFF'), flush=True)
    if not run:
        print('RUNNER_EXITED', flush=True)
        sys.exit(0)
    time.sleep(30)
print('STILL_RUNNING', flush=True)
sys.exit(1)
