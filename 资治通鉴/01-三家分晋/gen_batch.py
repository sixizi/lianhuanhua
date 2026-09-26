# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 01 三家分晋（周纪一 · 威烈王二十三年）批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
四幕：智伯索地 / 走保晋阳 / 水灌孤城 / 夜决灭智。
定标三条：人物场景一致卡逐幕注入；底图无字、题款程序合成；校验 aicloud-kimi→qwen。
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

# —— 本回人物卡/场景卡（规则 1：同一字符串注入每一幕）——
CHAR_ZHIBO = ('同一人：智伯智瑶，身材十分高大的中年男子，鬓发乌黑浓密，蓄三绺长髯，'
              '头戴高耸玉冠，身着绛紫色宽袖锦袍，神态倨傲睥睨。')
CHAR_XIANGZI = ('同一人：赵襄子无恤，二十多岁的年轻国君，面容清瘦坚毅，颔下短须，'
                '束发戴小冠，身着月白色深衣，腰间佩长剑。')
CHAR_HANWEI = ('魏桓子：体态壮硕的中年卿大夫，络腮短须，戴高梁冠，身着玄色袍服，神情隐忍；'
               '韩康子：清瘦的中年卿大夫，颏下山羊胡，戴小梁冠，身着青灰色袍服，神情忧惧。')
SET_HALL = '晋国朝堂：木构高堂，立柱粗梁，帷幔垂落，案几上陈简册地图。'
SET_JY = '晋阳城：厚重的夯土城墙，简朴的城门楼，城外群山苍茫。'
SET_FLOOD = '大水围困的晋阳：洪水淹没城外原野，城墙只露出上半截，水面漂浮木盆，堤坝横亘水中。'
SET_NIGHT = '夜色中的河堤与军营：火把点点，黑水翻涌，兵戈林立，营帐连绵。'

SCENES = [
    ('01-智伯索地',
     '战国晋国朝堂内：智伯昂首踞坐在主位席上，韩地使者双手捧着卷起的地图躬身进献，'
     '谋士段规在旁拱手侍立，智伯神色倨傲含笑。智伯位于画面下半幅。'
     + CHAR_ZHIBO + SET_HALL + '。' + STYLE + '。' + NOTEXT),
    ('02-走保晋阳',
     '原野上：赵襄子一行数骑快马奔赴远方的晋阳城，城门开启，城头吏民守望。'
     '全部景物集中在画面左半幅与下半幅：赵襄子在左下前景，晋阳城与城门楼在远景左侧，'
     '天空的暮色云气只铺在画面左上与中上；画面右半幅自上而下保持纯宣纸留白，'
     '无山、无云、无飞鸟、无任何景物，空无一物。'
     + CHAR_XIANGZI + SET_JY + '。' + STYLE + '。' + NOTEXT),
    ('03-水灌孤城',
     '大水围困的晋阳城外，横亘水面的堤坝上停着一辆辇车：智伯端坐车中，抬手指向远处'
     '被洪水围困的孤城，魏桓子立于车前执辔驾车，韩康子立于车侧，二人暗中交换眼色，'
     '远处晋阳城只剩上半截城墙露出水面，城头士兵持戈坚守。'
     '全部景物集中于画面左半幅与下半幅：辇车与三人在左下，晋阳孤城在远景左侧，'
     '堤坝与水面不超过画面高度的三分之二；画面右上角四分之一区域是纯净的宣纸留白，'
     '无任何山石、云、水纹、旗帜、飞鸟，空无一物。'
     + CHAR_ZHIBO + CHAR_HANWEI + SET_FLOOD + '。' + STYLE + '。' + NOTEXT),
    ('04-夜决灭智',
     '深夜河堤上：赵襄子挥剑率军夜袭，士兵斩杀守堤之吏，河水决开堤坝倒灌智伯军营，'
     '营中军士在黑水中挣扎大乱，远处左侧韩魏两军火把成列从两翼掩杀。'
     '全部战事、火把、营帐、水浪都集中在画面左半幅与下半幅；画面右半幅自上而下'
     '只有淡淡的夜雾与纯宣纸留白，不画营帐、不画水浪、不画火把、不画人物、不画云烟，'
     '空无一物。'
     + CHAR_XIANGZI + SET_NIGHT + '。' + STYLE + '。' + NOTEXT),
]

# 每幕题款（右起列序、去标点；简体规范字，底本异写见故事.md 注）
INSCRIPTIONS = [
    ('01-智伯索地', ['智伯请地于韩康子',
                      '又求蔡皋狼之地于赵襄子',
                      '襄子弗与智伯怒']),
    ('02-走保晋阳', ['其晋阳乎先主之所属也尹铎之所宽也',
                      '民必和矣乃走晋阳']),
    ('03-水灌孤城', ['城不浸者三版沉灶产蛙民无叛意',
                      '智伯曰吾乃今知水可以亡人国也']),
    ('04-夜决灭智', ['襄子夜使人杀守堤之吏',
                      '决水灌智伯军大败智伯之众',
                      '遂杀智伯尽灭智氏之族']),
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
            print('SKIP ' + name + '（已被合成方案取代）', flush=True)
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
    print('下一步：../../check_inscription.py --crop NN-幕名.jpg 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
