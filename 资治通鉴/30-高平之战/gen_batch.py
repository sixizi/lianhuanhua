# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 30 高平之战（卷二九一 · 后周纪二 · 显德元年（公元954年））批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
五幕：帝介马督战 / 元徽马倒 / 太祖奋击 / 斩爱能等 / 肃军法立。
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

CHAR_CZ = '同一人：周世宗柴荣，三十四岁的少年天子，英武锐气，金甲绛袍，亲挽弧矢督战。'
CHAR_TZ = '赵匡胤：殿前宿卫将，身材魁伟，紫面大耳，铁甲皂袍，身先士卒。'
CHAR_ZYH = '张元徽：北汉骁将，铁骑先锋，纵马突阵，骄悍轻敌。'
CHAR_FA = '樊爱能：周军右军主将，神情怯懦，引骑南遁。'
CHAR_ZYD = '张永德：殿前都指挥使，沉毅有谋，按辔观阵。'
SET_BGY = '巴公原战场：平原大风，东北风转南风，两军对垒，尘沙漫天。'
SET_JZ = '晋阳城下：周军旗帜环城四十里，城头矢石交下。'
SET_XW = '周军行宫帐：昼卧行宫，帝掷枕而起，帐中诸将肃立。'

SCENES = [
    ('01-帝介马督战',
     '巴公原战场：北汉东军旌旗先进，周军右军未战先溃，世宗介马自临阵督战，亲兵犯矢石而进。战阵集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无旌旗、无烟尘、无飞鸟，空无一物。' + CHAR_CZ + SET_BGY + '。' + STYLE + '。' + NOTEXT),
    ('02-元徽马倒',
     '阵前驰突：张元徽纵骑略阵，战马中箭轰然而倒，周兵乘势斫杀，北军夺气。搏杀集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无兵戈、无烟尘，空无一物。' + CHAR_ZYH + SET_BGY + '。' + STYLE + '。' + NOTEXT),
    ('03-太祖奋击',
     '左翼冲阵：赵匡胤身先士卒，驰犯敌锋，马仁瑀跃马引弓大呼连毙数十人，周兵争奋。冲杀集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无箭矢、无旌旗，空无一物。' + CHAR_TZ + SET_BGY + '。' + STYLE + '。' + NOTEXT),
    ('04-斩爱能等',
     '阵后军门：樊爱能等被缚于旗杆之下，世宗亲自数罪，刀斧手环立，诸军屏息。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无兵戈、无旌旗、无刑具，空无一物。' + CHAR_CZ + CHAR_FA + SET_XW + '。' + STYLE + '。' + NOTEXT),
    ('05-肃军法立',
     '行宫帐中：世宗掷枕而起大呼称善，张永德侍侧进言，帐外新军操练严整。二人位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无帐纹、无兵器，空无一物。' + CHAR_CZ + CHAR_ZYD + SET_XW + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-帝介马督战', ['北汉主以中军陈于巴公原',
                      '帝介马自临陈督战',
                      '谓诸将曰吾自用汉军可破也何必契丹',
                      '合战未几樊爱能何徽引骑兵先遁',
                      '右军溃步兵千余人解甲呼万岁']),
    ('02-元徽马倒', ['北汉主知帝自临陈',
                      '褒赏张元徽趣使乘胜进兵',
                      '元徽前略陈马倒为周兵所杀',
                      '元徽北汉之骁将也北军由是夺气',
                      '时南风益盛周兵争奋北汉兵大败']),
    ('03-太祖奋击', ['太祖皇帝时为宿卫将谓同列曰',
                      '主危如此吾属何得不致死',
                      '太祖皇帝身先士卒驰犯其锋',
                      '士卒死战无不一当百北汉兵披靡',
                      '跃马引弓大呼连毙数十人士气益振']),
    ('04-斩爱能等', ['帝欲诛樊爱能等以肃军政犹豫未决',
                      '爱能等素无大功忝冒节钺',
                      '望敌先逃死未塞责',
                      '即收爱能徽及所部军使以上七十余人',
                      '汝曹皆累朝宿将非不能战']),
    ('05-肃军法立', ['且陛下方欲削平四海',
                      '苟军法不立',
                      '虽有熊罴之士百万之众安得而用之',
                      '帝掷枕于地大呼称善',
                      '自是骄将惰卒始知所惧',
                      '不行姑息之政矣']),
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
    print('下一步：../../verify_batch.py 高平 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
