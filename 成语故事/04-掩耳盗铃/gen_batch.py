# -*- coding: utf-8 -*-
"""04-掩耳盗铃 - 组画批量生成（定标流程，见 story-painting-series 技能）。

原文出处：《吕氏春秋·自知》（原文为"盗钟"，后世演化为成语"掩耳盗铃"）：
范氏之亡也，百姓有得钟者，欲负而走，钟大不可负，以椎毁之，钟况然有音，
恐人闻之而夺己也，遽掩其耳。恶人闻之可也，恶己自闻之，悖也。

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

THIEF = '同一位盗钟人：灰褐短打，头缠布巾，体格壮实，神情惶急。'
RUIN = '同一座荒废庭院：断墙残垣，断柱荒草，庭中一口巨大的青铜古钟。'
SEAL = '掩耳盗铃'

SCENES = [
    ('01-得钟欲负',
     '范氏败亡后的荒宅，' + RUIN + THIEF +
     '他欣喜若狂地发现庭中青铜大钟，钟在画面下半幅，他弯腰去背，'
     '涨得面红耳赤也背不动。' + STYLE + '。' + NOTEXT),
    ('02-以椎毁之',
     THIEF + RUIN +
     '他抡起木椎奋力砸钟，钟身在画面左下方，钟体纹丝不动，他双臂被震得发麻，'
     '踉跄后退。' + STYLE + '。' + NOTEXT),
    ('03-遽掩其耳',
     '钟声况然大响，以一圈圈淡墨涟漪纹样自钟口向四周扩散；' + THIEF +
     '他惊慌失措地双手死死捂住自己的耳朵，缩在画面左侧钟旁。'
     + STYLE + '。' + NOTEXT),
    ('04-恶己自闻',
     '荒宅断墙之外，两名路人循声张望而来，在画面左侧墙外探头；' + THIEF +
     '他在画面下半幅仍捂着耳朵卖力砸钟，对来人浑然不觉。'
     + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-得钟欲负', ['范氏之亡也', '百姓有得钟者', '欲负而走钟大不可负']),
    ('02-以椎毁之', ['以椎毁之', '钟况然有音']),
    ('03-遽掩其耳', ['恐人闻之而夺己也', '遽掩其耳']),
    ('04-恶己自闻', ['恶人闻之可也', '恶己自闻之悖也']),
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
