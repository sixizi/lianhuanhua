# -*- coding: utf-8 -*-
"""02-守株待兔 - 组画批量生成（定标流程，见 story-painting-series 技能）。

原文出处：《韩非子·五蠹》：
宋人有耕者，田中有株，兔走触株，折颈而死。因释其耒而守株，冀复得兔。
兔不可复得，而身为宋国笑。

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

FARMER = '同一位宋国农夫：粗布短褐，头戴斗笠，脚蹬草鞋，面色黝黑，体形精瘦。'
FIELD = '同一片宋国田野：黄土田垄，田边一截虬曲的黑色老树桩，远处几间茅舍。'
SEAL = '守株待兔'

SCENES = [
    ('01-兔走触株',
     '田野间，' + FARMER + FIELD +
     '他扶着耒在田垄间劳作，位于画面左下方；一只野兔从右侧草丛疾奔而来，'
     '一头撞在老树桩上折颈而倒，四脚朝天；农夫回头惊望。'
     + STYLE + '。' + NOTEXT),
    ('02-释耒守株',
     '农夫见兔撞死，' + FARMER + FIELD +
     '他放下耒具，盘坐到老树桩旁，位于画面左下方，双目紧盯树桩；'
     '野兔僵躺在树桩边。' + STYLE + '。' + NOTEXT),
    ('03-冀复得兔',
     '日复一日，' + FARMER + FIELD +
     '他仍守在画面左侧的树桩旁，衣衫渐皱，神色痴执，身旁以淡墨虚影绘出一只'
     '若隐若现的兔子，象征他脑中的妄念；四周田垄渐生荒草。'
     + STYLE + '。' + NOTEXT),
    ('04-身为宋笑',
     '一群乡邻路过田埂，在画面左侧指着他哄笑议论；' + FARMER + FIELD +
     '他仍呆坐树桩旁在画面中下方，身后田地荒芜，杂草丛生。'
     + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-兔走触株', ['宋人有耕者田中有株', '兔走触株折颈而死']),
    ('02-释耒守株', ['因释其耒而守株']),
    ('03-冀复得兔', ['冀复得兔']),
    ('04-身为宋笑', ['兔不可复得', '而身为宋国笑']),
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
