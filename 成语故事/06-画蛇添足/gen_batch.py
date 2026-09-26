# -*- coding: utf-8 -*-
"""06-画蛇添足 - 组画批量生成（定标流程，见 story-painting-series 技能）。

原文出处：《战国策·齐策二》：
楚有祠者，赐其舍人卮酒。舍人相谓曰：数人饮之不足，一人饮之有余。
请画地为蛇，先成者饮酒。一人蛇先成，引酒且饮之，乃左手持卮，右手画蛇，
曰：吾能为之足。未成，一人之蛇成，夺其卮曰：蛇固无足，子安能为之足。
遂饮其酒。为蛇足者，终亡其酒。

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

PAINTER = '同一位楚国舍人甲：土黄长衫，方巾束发，颧骨高耸，神情自得。'
RIVAL = '同一位楚国舍人乙：青灰短衫，眉目精明，动作利落。'
SHRINE = '同一座楚地祠堂院落：青砖祭台，香案一角，院中一片平整土地。'
SEAL = '画蛇添足'

SCENES = [
    ('01-赐卮相谓',
     '祭祀方毕，' + SHRINE + '主人赐下的一卮酒摆在画面下半幅祭台上，'
     '众舍人围拢商议如何分这杯酒，指指点点，各出主意。'
     + STYLE + '。' + NOTEXT),
    ('02-画地为蛇',
     '众舍人蹲在画面下半幅的院中土地上，各执树枝画蛇比赛；'
     + PAINTER + '与' + RIVAL + '同场竞技，各画各的蛇，地上蛇形渐成。'
     + STYLE + '。' + NOTEXT),
    ('03-吾能为之足',
     PAINTER + '他的蛇先画成，在画面左下方左手举起酒卮欲饮，'
     '右手却继续用树枝蘸酒在地上给蛇添脚，一脸得意忘形；'
     + RIVAL + '在旁疾笔画蛇。' + STYLE + '。' + NOTEXT),
    ('04-终亡其酒',
     RIVAL + '他的蛇已画成，在画面左下方一把夺过酒卮，'
     '指着地上那条多脚的蛇斥问，仰头欲饮；' + PAINTER +
     '张口结舌，懊恼不已；地上两条蛇，一条无脚，一条却被添了四只小脚。'
     + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-赐卮相谓', ['楚有祠者赐其舍人卮酒', '舍人相谓曰', '数人饮之不足一人饮之有余']),
    ('02-画地为蛇', ['请画地为蛇', '先成者饮酒']),
    ('03-吾能为之足', ['一人蛇先成', '引酒且饮之', '乃左手持卮右手画蛇', '曰吾能为之足未成']),
    ('04-终亡其酒', ['一人之蛇成', '夺其卮曰蛇固无足', '子安能为之足', '遂饮其酒为蛇足者终亡其酒']),
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
