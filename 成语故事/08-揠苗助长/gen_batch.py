# -*- coding: utf-8 -*-
"""08-揠苗助长 - 组画批量生成（定标流程，见 story-painting-series 技能）。

原文出处：《孟子·公孙丑上》：
宋人有闵其苗之不长而揠之者，芒芒然归，谓其人曰：今日病矣，予助苗长矣。
其子趋而往视之，苗则槁矣。

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

FARMER = '同一位宋国农夫：粗布短衣，卷着裤腿，草绳束腰，面带愁容，性情急躁。'
SON = '同一位农家少年：青布短打，眉眼机灵，步履匆匆。'
FIELD = '同一片禾田：嫩绿秧苗成行，田埂土路，田头一座篱笆农舍。'
SEAL = '揠苗助长'

SCENES = [
    ('01-闵其苗',
     FIELD + FARMER +
     '他蹲在画面左下方田头，愁眉苦脸地望着矮小的秧苗，抓耳挠腮，心急如焚。'
     + STYLE + '。' + NOTEXT),
    ('02-揠苗',
     FIELD + FARMER +
     '他弯腰在画面下半幅的田垄间把禾苗一棵棵用力往上拔高，'
     '秧苗被连根拔起东倒西歪，他满头大汗，得意卖力。'
     + STYLE + '。' + NOTEXT),
    ('03-予助苗长',
     '篱笆农舍前，' + FARMER +
     '他疲惫归来，却拍着胸口眉飞色舞地向家人夸功，'
     '一名家人在画面左侧捧碗惊讶聆听。' + STYLE + '。' + NOTEXT),
    ('04-苗则槁矣',
     FIELD + SON +
     '少年急匆匆奔到画面左下方田头，俯身查看——满田秧苗尽数枯黄蔫倒，'
     '他瞠目结舌。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-闵其苗', ['宋人有闵其苗之不长']),
    ('02-揠苗', ['而揠之者芒芒然归']),
    ('03-予助苗长', ['谓其人曰', '今日病矣予助苗长矣']),
    ('04-苗则槁矣', ['其子趋而往视之', '苗则槁矣']),
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
