# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 11 白登之围（卷十一 · 汉纪三 · 高帝七年（公元前200年））批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
四幕：白登被围 / 厚遗阏氏 / 解围一角 / 曲逆之封。
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

CHAR_GZ = '同一人：汉高祖刘邦，四十七岁的帝王，隆准长颈，蓄三绺黑须，头戴皮弁，身着赭黄色绵袍外罩玄色铁甲，肩披玄色大氅，神情坚忍。'
CHAR_MD = '同一人：匈奴冒顿单于，身材魁梧的草原雄主，披发戴皮帽，耳悬金环，身着棕色狼裘，腰束革带佩弯刀，面容剽悍沉鸷。'
CHAR_YZ = '阏氏：冒顿单于之妻，体态丰腴的贵妇，头戴貂皮风帽，身着朱红色狐裘，神情矜持。'
CHAR_CP = '陈平：三十多岁的汉廷谋士，面容白皙清瘦，颏下短须，头戴进贤冠，身着玄色深衣，神情机敏沉静。'
CHAR_LJ = '刘敬：出使匈奴归来的汉使，风尘仆仆的中年官员，皮帽破旧，玄色使节袍沾满雪泥。'
SET_BD = '白登山：寒冬雪岭，山顶上汉军营垒被围，鹿角拒马环绕，四色匈奴骑兵黑压压布满四面山坡，积雪皑皑，寒云沉沉。'
SET_YZT = '阏氏毡帐：匈奴王帐，穹庐毡幕，帐内铺兽皮，铜灯昏黄。'

SCENES = [
    ('01-白登被围',
     '白登山顶：汉高祖立于营垒高处远眺，神情坚忍，身边甲士持盾肃立；四面山坡上匈奴铁骑层层合围，四色战马（西面白马、东面青龙马、北面黑马、南面赤黄马）漫山遍野，匈奴骑弓拉满遥指山顶。汉高祖与营垒位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无山石、无云烟、无旗帜、无飞鸟，空无一物。' + CHAR_GZ + SET_BD + '。' + STYLE + '。' + NOTEXT),
    ('02-厚遗阏氏',
     '匈奴王帐内：阏氏端坐兽皮主位，汉使躬身捧金帛珠宝进献，帐外隐约风雪扑帘。阏氏抬手示意，若有所思。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无毡幕垂纹、无器物，空无一物。' + CHAR_YZ + SET_YZT + '。' + STYLE + '。' + NOTEXT),
    ('03-解围一角',
     '白登山下：会天大雾，浓雾横贯山腰，汉军强弩手两矢外向结阵而行，从雾中解围一角鱼贯而出，高祖乘马徐行；远处匈奴骑兵队列若隐若现。行军队伍集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无雾气、无山影、无骑兵，空无一物。' + CHAR_GZ + CHAR_CP + SET_BD + '。' + STYLE + '。' + NOTEXT),
    ('04-曲逆之封',
     '汉军归营大帐：高祖坐于案后解颜而笑，亲手向陈平授予封侯诏册，陈平跪拜受封，群臣侍立，案上摆酒爵。二人在画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无柱无幔，空无一物。' + CHAR_GZ + CHAR_CP + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-白登被围', ['帝先至平城兵未尽到',
                      '冒顿纵精兵四十万骑',
                      '围帝于白登七日',
                      '汉兵中外不得相救饷']),
    ('02-厚遗阏氏', ['帝用陈平秘计',
                      '使使间厚遗阏氏',
                      '阏氏谓冒顿曰两主不相困',
                      '今得汉地而单于终非能居之也',
                      '且汉主亦有神灵单于察之']),
    ('03-解围一角', ['与王黄赵利期而黄利兵不来',
                      '疑其与汉有谋乃解围之一角',
                      '会天大雾汉使人往来匈奴不觉',
                      '陈平请令强弩傅两矢',
                      '外乡从解角直出']),
    ('04-曲逆之封', ['帝出围欲驱太仆滕公固徐行',
                      '至平城汉大军亦到胡骑遂解去',
                      '吾不用公言以困平城',
                      '吾皆已斩前使十辈矣',
                      '乃更封陈平为曲逆侯尽食之',
                      '平从帝征伐凡六出奇计']),
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
    print('下一步：../../verify_batch.py 白登 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
