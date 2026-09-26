# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 02 商鞅变法（卷二 · 周纪二 · 显王十年）批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
四幕：廷辩定法 / 南门立木 / 法行于上 / 乡邑大治。
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

CHAR_YW = '同一人：卫鞅，三十岁上下的青年官员，面容清瘦坚毅，短须，束发戴高冠，身着玄色官袍，腰束革带，神情锐利自信。'
CHAR_XG = '同一人：秦孝公，二十余岁的年轻国君，浓眉朗目，蓄短须，头戴冕旒，身着赭黄色王袍，端坐主位，神态沉稳专注。'
CHAR_GL = '老臣甘龙：须发花白的老大夫，颏下白须，身着灰绿色朝服，神情凝重。'
SET_HALL = '秦国朝堂：夯土高台上的木构大殿，立柱粗梁，帷幔深沉。'
SET_NANMEN = '咸阳南市：夯土城墙高耸，南门外集市棚摊错落，人群围观。'
SET_VILLAGE = '关中田野：阡陌纵横，农人荷锄往来，远处粮仓谷堆。'

SCENES = [
    ('01-廷辩定法',
     '秦国朝堂上：卫鞅立于殿中慷慨陈词，侃侃而谈；老臣甘龙拄杖力争，面露忧色；秦孝公坐于主位倾听，微微颔首。三人位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无柱无幔无人物，空无一物。' + CHAR_YW + CHAR_XG + CHAR_GL + SET_HALL + '。' + STYLE + '。' + NOTEXT),
    ('02-南门立木',
     '咸阳城南门外：一根三丈高的木柱立在空地，围观百姓议论纷纷面面相觑，一名壮汉扛木而行，官吏捧金奉赏，城门楼在远景左侧。人物聚集于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无物无云，空无一物。' + SET_NANMEN + '。' + STYLE + '。' + NOTEXT),
    ('03-法行于上',
     '朝堂阶前：两名戴罪的宗室师傅被武士押立于阶下，卫鞅立于阶上手执简册高声宣令，甲士肃立，秦孝公坐于殿上神情凝重。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，空无一物。' + CHAR_YW + CHAR_XG + SET_HALL + '。' + STYLE + '。' + NOTEXT),
    ('04-乡邑大治',
     '关中田野：农人荷锄往来于阡陌，牛车运粮，村邑里门安然，一名行旅者对路旁遗物视若无睹径直走过，仓廪谷堆饱满。景物集中于画面左半幅与下半幅，天空的云气只铺在画面左上，画面右半幅自上而下保持纯宣纸留白，空无一物。' + SET_VILLAGE + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-廷辩定法', ['卫鞅欲变法秦人不悦',
                      '民不可与虑始而可与乐成',
                      '公曰善卒定变法之令']),
    ('02-南门立木', ['令既具未布恐民之不信',
                      '立三丈之木于国都市南门',
                      '能徙者予五十金有一人徙之']),
    ('03-法行于上', ['法之不行自上犯之',
                      '太子君嗣也不可施刑',
                      '刑其傅公子虔黥其师公孙贾']),
    ('04-乡邑大治', ['行之十年秦国道不拾遗',
                      '山无盗贼民勇于公战',
                      '怯于私斗乡邑大治']),
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
    print('下一步：../../verify_batch.py 商鞅 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
