# -*- coding: utf-8 -*-
"""03-刻舟求剑 - 组画批量生成（定标流程，见 story-painting-series 技能）。

原文出处：《吕氏春秋·察今》：
楚人有涉江者，其剑自舟中坠于水，遽契其舟，曰：是吾剑之所从坠。
舟止，从其所契者入水求之。舟已行矣，而剑不行，求剑若此，不亦惑乎。

规则 1：一致卡注入每一幕；规则 3：无字底图 + 自动合成题款；
规则 2：校验用 ../../check_inscription.py --crop（默认 aicloud-kimi）。

用法:
    python3 gen_batch.py              # 生成全部 4 幕并自动合成题款
    python3 gen_batch.py 02           # 只处理 02（重生成底图 + 重合成）
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'gen_image.py')
COMPOSE = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'compose_inscription.py')

STYLE = ('中国传统水墨画，宣纸质感，浓墨勾勒轮廓，淡墨渲染云雾层次，大面积留白，'
         '构图空灵，全画黑白灰为主，意境悠远')
NOTEXT = ('画面中不得出现任何文字、任何汉字、任何印章印鉴，'
          '画面主体集中在左半幅与下半幅，右上角区域大面积留白，什么都不画。')

CHU = '同一位楚地渡客：深青布袍，束发小帻，面容清瘦，腰间佩一柄长剑。'
BOAT = '同一条渡江木船：平底木船，芦席船篷，老船夫执篙，江面辽阔。'
SEAL = '刻舟求剑'

SCENES = [
    ('01-剑坠于水',
     '江心之上，' + BOAT + CHU +
     '他立于船头，位于画面下半幅，腰间佩剑脱鞘坠入江中，水面溅起水花，'
     '他俯身惊呼；江面以淡墨留白。' + STYLE + '。' + NOTEXT),
    ('02-遽契其舟',
     CHU + BOAT +
     '他俯身在画面左下方的船舷边，用小刀急忙刻下一道记号，神情急切；'
     '船夫在船尾撑篙摇头。' + STYLE + '。' + NOTEXT),
    ('03-入水求之',
     '船靠岸停稳在画面下半幅，' + CHU +
     '他脱去外袍，从船舷刻记号处一头扎入水中摸索，江面泛起涟漪，'
     '水下一无所获；刻痕清晰可见。' + STYLE + '。' + NOTEXT),
    ('04-不亦惑乎',
     CHU +
     '他湿淋淋地从画面左下方的水面冒出头，满脸茫然；远处小船已行至画面左侧'
     '江心渐远，水下深处以淡墨隐约绘出沉在江底的宝剑，舟与剑相离甚远。'
     + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-剑坠于水', ['楚人有涉江者', '其剑自舟中坠于水']),
    ('02-遽契其舟', ['遽契其舟曰', '是吾剑之所从坠']),
    ('03-入水求之', ['舟止从其所契者', '入水求之']),
    ('04-不亦惑乎', ['舟已行矣而剑不行', '求剑若此不亦惑乎']),
]

SUPERSEDED = set()


def run():
    only = sys.argv[1:]
    ok, fail = [], []
    for name, prompt in SCENES:
        if name in SUPERSEDED and not only:
            print('SKIP ' + name, flush=True)
            continue
        if only and not any(s in name for s in only):
            continue
        print('=== ' + name + ' 底图', flush=True)
        r = subprocess.run([sys.executable, GEN, prompt, '-d', HERE,
                            '-n', name + '-底图'])
        print('    exit ' + str(r.returncode), flush=True)
        (ok if r.returncode == 0 else fail).append(name + '-底图')

    for name, cols in INSCRIPTIONS:
        if only and not any(s in name for s in only):
            continue
        base = None
        for ext in ('.jpg', '.jpeg', '.png'):
            p = os.path.join(HERE, name + '-底图' + ext)
            if os.path.exists(p):
                base = p
                break
        if not base:
            print('=== ' + name + ' 缺底图，跳过合成', flush=True)
            fail.append(name + '-合成')
            continue
        print('=== ' + name + ' 合成题款', flush=True)
        cmd = [sys.executable, COMPOSE, base,
               '-o', os.path.join(HERE, name + '.jpg')]
        for c in cols:
            cmd += ['-c', c]
        cmd += ['-s', SEAL]
        r = subprocess.run(cmd)
        print('    exit ' + str(r.returncode), flush=True)
        (ok if r.returncode == 0 else fail).append(name + '-合成')

    print('DONE ok=' + str(len(ok)) + ' fail=' + str(fail), flush=True)
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
