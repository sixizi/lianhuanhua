# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 04 完璧归赵（卷三 · 周纪三 · 赧王三十二年）批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
四幕：秦王求璧 / 奉璧入秦 / 间行归璧 / 廷对全节。
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

CHAR_XR = '同一人：蔺相如，三十岁上下的赵国使臣，面容端正儒雅，三绺短须，束发戴高冠，身着月白色使臣礼服，神情从容坚毅。'
CHAR_QW = '同一人：秦昭王，三十余岁的秦国之王，面容雄鸷，冠冕玄袍，坐于高台之上。'
CHAR_ZW = '赵惠文王：年轻的赵国国君，眉目温润，头戴高冠，身着绛红色王袍。'
SET_ZHAOGONG = '赵国王宫：暖色调木构殿堂，侍者捧匣侍立。'
SET_QINDIAN = '秦国大殿：高台巍峨，深殿立柱，群臣肃立分列，案几上礼器森然。'
SET_GUANDAO = '战国官道：黄土道旁驿亭孤柳，远山如黛。'
SET_YEYUAN = '夜晚原野：荒径草色，远处城郭灯火一点。'

SCENES = [
    ('01-秦王求璧',
     '赵国王宫中：赵惠文王双手捧着和氏璧细看，眉头深锁进退两难，侍臣分立，蔺相如立于阶下从容进言。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，空无一物。' + CHAR_XR + CHAR_ZW + SET_ZHAOGONG + '。' + STYLE + '。' + NOTEXT),
    ('02-奉璧入秦',
     '官道之上：蔺相如捧璧匣乘轺车西行入秦，身后赵国城郭渐远，前路秦地群山苍莽。车马在画面左下半幅，山道蜿蜒向左侧远景，画面右半幅自上而下保持纯宣纸留白，无山无云，空无一物。' + CHAR_XR + SET_GUANDAO + '。' + STYLE + '。' + NOTEXT),
    ('03-间行归璧',
     '夜色原野小径：相如的随从怀揣宝匣纵马疾驰抄小路归赵，回望远处咸阳城灯火一点，马蹄扬尘。骑士在画面左下半幅，城郭灯火在远景左侧，画面右半幅自上而下保持纯宣纸留白，无月无云，空无一物。' + SET_YEYUAN + '。' + STYLE + '。' + NOTEXT),
    ('04-廷对全节',
     '秦国大殿上：蔺相如昂然拱手立于殿中，气度凛然无惧；秦昭王坐于高台俯视，神色复杂，群臣怒目而不敢动。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，空无一物。' + CHAR_XR + CHAR_QW + SET_QINDIAN + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-秦王求璧', ['赵王得楚和氏璧',
                      '秦昭王欲之请易以十五城',
                      '欲与之恐见欺']),
    ('02-奉璧入秦', ['均之二策宁许以负秦',
                      '臣愿奉璧而往',
                      '使秦城不入臣请完璧而归之']),
    ('03-间行归璧', ['秦王无意偿赵城',
                      '相如乃以诈绐秦王复取璧',
                      '遣从者怀之间行归赵']),
    ('04-廷对全节', ['而以身待命于秦',
                      '秦王以为贤而弗诛',
                      '礼而归之']),
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
    print('下一步：../../verify_batch.py 完璧 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
