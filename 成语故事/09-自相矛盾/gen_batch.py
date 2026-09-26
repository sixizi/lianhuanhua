# -*- coding: utf-8 -*-
"""09-自相矛盾 - 组画批量生成（定标流程，见 story-painting-series 技能）。

原文出处：《韩非子·难一》：
楚人有鬻盾与矛者，誉之曰：吾盾之坚，物莫能陷也。又誉其矛曰：吾矛之利，
于物无不陷也。或曰：以子之矛陷子之盾，何如。其人弗能应也。

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

SELLER = '同一位楚国商贩：赭色短袍，络腮胡，嗓门洪亮，表情夸张。'
MARKET = '同一处楚国市集：木摊支起，摊上插着一柄长矛、立着一面圆盾，行人往来。'
SEAL = '自相矛盾'

SCENES = [
    ('01-鬻矛与盾',
     MARKET + SELLER +
     '他在画面下半幅守着摊子，一手举矛一手按盾，吆喝叫卖，唾沫横飞。'
     + STYLE + '。' + NOTEXT),
    ('02-誉盾誉矛',
     MARKET + SELLER +
     '他先拍着画面左下方的圆盾夸口其坚，又转身高举长矛吹嘘其利，'
     '围观行人越聚越多。' + STYLE + '。' + NOTEXT),
    ('03-何如',
     MARKET +
     '一位路人在画面左侧含笑抬手指向矛与盾发问；' + SELLER +
     '他张着嘴，一时语塞，笑容僵在脸上。' + STYLE + '。' + NOTEXT),
    ('04-弗能应',
     MARKET + SELLER +
     '他挠头结舌，面红耳赤，手里的矛和盾都举不起来，摊在身前；'
     '围观者掩口哄笑。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-鬻矛与盾', ['楚人有鬻盾与矛者']),
    ('02-誉盾誉矛', ['誉之曰吾盾之坚', '物莫能陷也', '又誉其矛曰',
                     '吾矛之利于物无不陷也']),
    ('03-何如', ['或曰以子之矛', '陷子之盾何如']),
    ('04-弗能应', ['其人弗能应也']),
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
