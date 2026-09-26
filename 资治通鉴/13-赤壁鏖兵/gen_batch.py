# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 13 赤壁鏖兵（卷六十五 · 汉纪五十七 · 建安十三年（公元208年））批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
五幕：斫案明志 / 蒙冲斗舰 / 中江举帆 / 烟炎张天 / 华容道。
印章：峄山碑篆体「资治通鉴」，全书统一（fonts/YiShanBeiZhuanTi.ttf）。

用法:
    python3 gen_batch.py              # 生成全部幕并自动合成题款
    python3 gen_batch.py 03           # 只处理文件名含 03 的幕
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'gen_image.py')
COMPOSE = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'compose_inscription.py')

# —— 系列常量（资治通鉴全系列逐字复用，保证跨回风格一致）——
STYLE = ('中国传统连环画风格，遒劲流畅的墨线勾勒人物与场景，线条细密工整，'
         '造型生动传神，如上海人民美术出版社经典工笔重彩连环画，'
         '在白描骨架上敷以明丽典雅的中国画色彩，朱砂石青石绿赭石点染，'
         '色彩饱满而透气，不腻不脏，宣纸底色，构图饱满，叙事清晰')
NOTEXT = ('画面中不得出现任何文字、任何汉字、任何印章印鉴，'
          '画面主体集中在左半幅与下半幅，右上角区域大面积留白，'
          '什么都不画。')

CHAR_SQ = '同一人：孙权，二十六岁的江东之主，碧目紫髯，仪表雄伟，头戴束发金冠，身着玄色王袍，神态果决刚断。'
CHAR_ZY = '同一人：周瑜，三十三岁的江左儒将，姿容英伟，束发铁盔，银甲罩青色战袍，气度从容。'
CHAR_HG = '黄盖：须发花白的老将，霜鬓铁甲，神情刚毅决绝。'
CHAR_CC = '同一人：曹操，五十四岁的中原雄主，身量不高而气概威严，头戴武弁，黑袍玄甲，短须，神情焦灼。'
SET_WT = '吴军殿堂：江东宫室，木构大殿，案几陈地图文书，佩剑悬柱。'
SET_JM = '江畔船坞：蒙冲斗舰列泊，军士扛燥荻枯柴上船，油瓮堆叠，帷幕裹船，江风猎猎。'
SET_HZ = '大江赤壁：南岸山崖赤壁耸立，江面开阔，东南风急，旌旗东指，北军连船首尾相接。'
SET_HR = '华容道：泥泞沼泽小道，羸兵负草填道，人马陷泥，枯枝寒林，暮色沉沉。'

SCENES = [
    ('01-斫案明志',
     '吴军殿堂内：孙权按剑立于案前，拔刀猛斫前奏案，刀锋入木，案角崩裂；周瑜披甲立于阶下侃侃而陈，众将肃立屏息。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无柱无幔无兵器，空无一物。' + CHAR_SQ + CHAR_ZY + SET_WT + '。' + STYLE + '。' + NOTEXT),
    ('02-蒙冲斗舰',
     '江畔船坞：黄盖拄剑督看军士将燥荻枯柴装载入十艘蒙冲斗舰，灌油其中，帷幕裹船，上建旌旗，船尾系走舸。船坞与人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无帆影、无江波，空无一物。' + CHAR_HG + SET_JM + '。' + STYLE + '。' + NOTEXT),
    ('03-中江举帆',
     '大江江心：东南风急，黄盖十舰最著前，中江举帆，馀船以次俱进；北岸曹军官兵出营立观指点。火船队列自画面左下向远景延伸，画面右半幅自上而下保持纯宣纸留白，无江波、无帆影、无飞鸟，空无一物。' + CHAR_HG + SET_HZ + '。' + STYLE + '。' + NOTEXT),
    ('04-烟炎张天',
     '赤壁江面：火烈风猛，船往如箭，北船尽烧，火光映红江水，烟炎张天；北军人马烧溺，南岸周瑜轻锐雷鼓大进。火场集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无火光、无烟炎、无云烟，空无一物。' + CHAR_ZY + SET_HZ + '。' + STYLE + '。' + NOTEXT),
    ('05-华容道',
     '华容泥泞小道：曹操引军步走，遇泥泞道不通，羸兵负草填道，骑兵踏草而过，陷泥者相藉，天色昏黑大风。曹操在画面左侧中景，溃兵队列沿左半幅向远处延伸，画面右半幅自上而下保持纯宣纸留白，无树木、无云烟、无飞鸟，空无一物。' + CHAR_CC + SET_HR + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-斫案明志', ['孤与老贼势不两立',
                      '君言当击甚与孤合此天以君授孤也',
                      '因拔刀斫前奏案曰',
                      '诸将吏敢复有言当迎操者与此案同']),
    ('02-蒙冲斗舰', ['瑜部将黄盖曰今寇众我寡难与持久',
                      '操军方连船舰首尾相接可烧而走也',
                      '乃取蒙冲斗舰十艘',
                      '载燥荻枯柴灌油其中',
                      '裹以帷幕上建旌旗',
                      '先以书遗操诈云欲降']),
    ('03-中江举帆', ['时东南风急盖以十舰最著前中江举帆',
                      '馀船以次俱进操军吏士皆出营立观',
                      '指言盖降去北军二里馀同时发火',
                      '火烈风猛船往如箭烧尽北船']),
    ('04-烟炎张天', ['延及岸上营落顷之烟炎张天',
                      '人马烧溺死者甚众',
                      '瑜等率轻锐继其后雷鼓大进',
                      '北军大坏']),
    ('05-华容道', ['操引军从华容道步走遇泥泞道不通',
                      '天又大风悉使羸兵负草填之骑乃得过',
                      '羸兵为人马所蹈藉陷泥中死者甚众']),
]

SEAL = '资治通鉴'
SEAL_FONT = os.path.join(os.path.dirname(os.path.dirname(HERE)),
                         'fonts', 'YiShanBeiZhuanTi.ttf')
SEAL_SIZE = 46
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

    if not SEAL:
        print('未配置 SEAL 印文，跳过合成阶段', flush=True)
    else:
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
            if os.path.exists(SEAL_FONT):
                cmd += ['--seal-font', SEAL_FONT, '--seal-size', str(SEAL_SIZE)]
            r = subprocess.run(cmd)
            print('    exit ' + str(r.returncode), flush=True)
            (ok if r.returncode == 0 else fail).append(name + '-合成')

    print('DONE ok=' + str(len(ok)) + ' fail=' + str(fail), flush=True)
    print('下一步：../../verify_batch.py 赤壁 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
