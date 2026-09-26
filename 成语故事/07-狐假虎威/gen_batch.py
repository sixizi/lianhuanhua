# -*- coding: utf-8 -*-
"""07-狐假虎威 - 组画批量生成（定标流程，见 story-painting-series 技能）。

原文出处：《战国策·楚策一》：
虎求百兽而食之，得狐。狐曰：子无敢食我也，天帝使我长百兽，今子食我是
逆天帝命也。子以我为不信，吾为子先行，子随我后，观百兽之见我而敢不走乎。
虎以为然，故遂与之行。兽见之皆走。虎不知兽畏己而走也，以为畏狐也。

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

TIGER = '同一只猛虎：吊睛白额，黄黑条纹，体形雄壮，步伐沉稳。'
FOX = '同一只狐狸：赤褐毛皮，尖耳长尾，眼神狡黠。'
FOREST = '同一片山林：古树虬枝，山石错落，藤蔓垂挂。'
SEAL = '狐假虎威'

SCENES = [
    ('01-虎求百兽',
     TIGER + FOREST + '猛虎在画面左下方扑住一只狐狸，利爪按住狐背，'
     '张口欲食；' + FOX + '狐狸被按在爪下，仰面朝天。'
     + STYLE + '。' + NOTEXT),
    ('02-天帝使命',
     FOX + '狐狸挣起身来，在画面左侧昂首挺胸，一本正经振振有词；'
     + TIGER + '猛虎瞪目迟疑，慢慢收起利爪，俯身听它说。'
     + FOREST + STYLE + '。' + NOTEXT),
    ('03-随行验兽',
     FOX + '在前昂首迈步领路，' + TIGER + '紧随其后；'
     '林中百兽——鹿、兔、野猪、猿猴——在画面下半幅见之纷纷惊逃四散。'
     + FOREST + STYLE + '。' + NOTEXT),
    ('04-以为畏狐',
     TIGER + '望着四散奔逃的百兽目瞪口呆，神情愕然，'
     '以为它们都害怕前面那只小小的狐狸；' + FOX +
     '在画面左下角得意洋洋地翘着尾巴。' + FOREST + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-虎求百兽', ['虎求百兽而食之', '得狐']),
    ('02-天帝使命', ['狐曰子无敢食我也', '天帝使我长百兽', '今子食我是逆天帝命也']),
    ('03-随行验兽', ['吾为子先行子随我后', '观百兽之见我', '而敢不走乎虎以为然',
                     '故遂与之行兽见之皆走']),
    ('04-以为畏狐', ['虎不知兽畏己而走也', '以为畏狐也']),
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
