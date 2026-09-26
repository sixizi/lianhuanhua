# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 20 台城之陷（卷一六一至一六二 · 梁纪十七至十八 · 太清二年至三年（548-549））批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
四幕：叱石珍 / 蔬茹皆绝 / 犹可一战 / 净居荷荷。
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

CHAR_LW = '同一人：梁武帝萧衍，八十六岁的老皇帝，清癯衰迈，须发皆白，身着素色旧帝袍，形容枯槁而神情不泯威严。'
CHAR_HJ = '侯景：跋扈枭将，虬髯深目，皮甲外罩半旧战袍，神情骄横。'
CHAR_ZSZ = '周石珍：惶恐的老侍臣，头戴獬豸冠? 此处改梁冠，青色官服，躬身屏息。'
SET_JM = '台城禁省宫道：宫墙斑驳，叛军驱驴马带弓刀出入，殿庭萧然。'
SET_GQ = '围城中御厨：冷灶残釜，士卒面有饥色，宫人捧空的食器。'
SET_NJ = '净居殿内室：昏暗卧帐，老皇帝卧于榻上，案上无蜜，孤灯如豆。'

SCENES = [
    ('01-叱石珍',
     '宫省廊道：叛军甲士驱驴马带弓刀穿行宫庭，梁武帝拄杖立于殿门怒视，周石珍躬身对答，驴群惊扰殿庭。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无兵器、无驴马、无器物，空无一物。' + CHAR_LW + CHAR_ZSZ + SET_JM + '。' + STYLE + '。' + NOTEXT),
    ('02-蔬茹皆绝',
     '围城御厨：梁武帝端坐食案前，案上只有一小盘鸡卵，宫人捧卵数百枚进上，老帝亲手料简，歔欷哽咽。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无器物、无帷幔，空无一物。' + CHAR_LW + SET_GQ + '。' + STYLE + '。' + NOTEXT),
    ('03-犹可一战',
     '寝殿之内：宫人趋入跪报城陷，梁武帝安卧榻上不动，垂问犹可一战乎，侍者垂首不能对。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无帷幔、无器物、无灯焰，空无一物。' + CHAR_LW + SET_NJ + '。' + STYLE + '。' + NOTEXT),
    ('04-净居荷荷',
     '净居殿内室：梁武帝卧于榻上，形容枯槁，张口索蜜而不得，案上空碗，孤灯摇曳，殿外无人。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无帐纹、无灯焰，空无一物。' + CHAR_LW + SET_NJ + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-叱石珍', ['景使其军士入直省中',
                      '或驱驴马带弓刀出入宫庭',
                      '周石珍对曰侯丞相甲士',
                      '上大怒叱石珍曰是侯景何谓丞相']),
    ('02-蔬茹皆绝', ['上常蔬食及围城日久',
                      '上厨蔬茹皆绝乃食鸡子',
                      '上手自料简哽咽']),
    ('03-犹可一战', ['乃排闼入启上云城已陷',
                      '上安卧不动曰犹可一战乎',
                      '上叹曰自我得之自我失之亦复何恨']),
    ('04-净居荷荷', ['上卧净居殿口苦索蜜不得',
                      '再曰荷荷遂殂年八十六']),
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
    print('下一步：../../verify_batch.py 台城 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
