# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 10 淝水之战（卷一〇五 · 晋纪二十七 · 孝武帝太元八年）批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
五幕：投鞭断流 / 八公草木 / 半渡决战 / 风声鹤唳 / 围棋赌墅。
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

CHAR_FJ = '同一人：苻坚，四十余岁的秦王，面容雄毅，冠冕赭黄王袍，前期倨傲自负，登城远望后始有惧色。'
CHAR_FR = '阳平公苻融：年轻英武的秦军统帅，顶盔贯甲，绛色披风。'
CHAR_XA = '谢安：六十岁的东晋名相，气度冲和，须发花白，宽袖深衣，神情渊渟岳峙。'
CHAR_XX = '谢玄：年轻的晋军前锋统帅，俊朗挺拔，白袍银甲。'
CHAR_SHIYUE = '老臣石越：须发斑白的谏臣，拱手而立。'
SET_CT = '秦国朝堂：帷幔层叠，百官分列，殿宇高深。'
SET_SY = '寿阳城头：夯土城垛，远山苍茫，八公山影林木森森。'
SET_FS = '肥水岸畔：秋冬之际的宽阔河流，对岸营阵隐约，芦荻苍苍。'
SET_HYE = '寒夜荒原：霜草枯木，残夜无月。'
SET_JK = '建康园林：冬日庭院，松竹掩映，围棋枰上棋子疏落。'

SCENES = [
    ('01-投鞭断流',
     '秦国朝堂：苻坚立于王座前扬言南征，须髯戟张志得意满，阶下石越拱手进谏，群臣分列或谏或默。苻坚与群臣位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，空无一物。' + CHAR_FJ + CHAR_SHIYUE + SET_CT + '。' + STYLE + '。' + NOTEXT),
    ('02-八公草木',
     '寿阳城头：苻坚与苻融登城远眺，苻坚扶垛而望面露惧色，远处八公山草木摇曳森然如列阵之兵，晋兵营垒部阵严整隐约可辨。城头二人在画面左侧，八公山影在远景左侧，画面右半幅自上而下保持纯宣纸留白，空无一物。' + CHAR_FJ + CHAR_FR + SET_SY + '。' + STYLE + '。' + NOTEXT),
    ('03-半渡决战',
     '肥水岸畔：秦军阵形后移尘土飞扬，晋军前锋渡河急进，苻融纵马驰掠阵前欲止退兵而马倒于地，秦军自相惊乱溃不可止。战事集中于画面左半幅与下半幅，河面横在左下，画面右半幅自上而下保持纯宣纸留白，空无一物。' + CHAR_FR + CHAR_XX + SET_FS + '。' + STYLE + '。' + NOTEXT),
    ('04-风声鹤唳',
     '寒夜溃道：秦军残兵丢盔弃甲连夜奔逃，闻风声惊惶回望，夜鸟掠过寒林，霜草苍茫，有人仆倒道旁。溃兵队伍沿画面左侧向远景延伸，画面右半幅自上而下保持纯宣纸留白，空无一物。' + SET_HYE + '。' + STYLE + '。' + NOTEXT),
    ('05-围棋赌墅',
     '建康园林亭中：谢安与宾客对坐弈棋，神色平静手落一子，案上驿书方函半开，客俯身探问。二人在画面左半幅与下半幅，庭院松枝一角在左上，画面右半幅自上而下保持纯宣纸留白，空无一物。' + CHAR_XA + SET_JK + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-投鞭断流', ['今以吾之众投鞭于江足断其流',
                      '又何险之足恃乎']),
    ('02-八公草木', ['望见八公山上草木皆以为晋兵',
                      '顾谓融曰此亦劲敌何谓弱也',
                      '怃然始有惧色']),
    ('03-半渡决战', ['但引兵少却使之半渡',
                      '朱序在陈后呼曰秦兵败矣',
                      '融驰骑略陈马倒为晋兵所杀']),
    ('04-风声鹤唳', ['其走者闻风声鹤唳皆以为晋兵且至',
                      '昼夜不敢息草行露宿',
                      '重以饥冻死者什七八']),
    ('05-围棋赌墅', ['谢安得驿书知秦兵已败',
                      '时方与客围棋了无喜色',
                      '徐答曰小儿辈遂已破贼']),
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
    print('下一步：../../verify_batch.py 淝水 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
