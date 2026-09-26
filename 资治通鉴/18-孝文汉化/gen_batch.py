# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 18 孝文汉化（卷一三八至一四〇 · 齐纪四至六 · 永明十一年至建武三年（493-496））批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
四幕：戎服执鞭 / 南迁定计 / 断诸北语 / 改姓元氏。
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

CHAR_XW = '同一人：魏孝文帝元宏，二十七岁的鲜卑帝王，俊朗威严，束发戴通天冠，身着赭黄衮袍，气度沉雄刚断。'
CHAR_LC = '李冲：中年汉臣，头戴进贤冠，青色朝服，神情恳切。'
CHAR_XT = '安定王休：年长的鲜卑宗室王公，白须垂胸，皮裘朝服，面容悲切。'
SET_LY = '洛阳郊野：霖雨初歇，泥泞御道，魏主戎服乘马立于阵前，群臣跪伏马前，銮驾仪仗肃列。'
SET_CT = '平城/洛阳朝堂：木构大殿，立柱帷幔，臣工序立。'

SCENES = [
    ('01-戎服执鞭',
     '洛阳郊野：魏主戎服执鞭乘马而出，群臣稽颡跪伏马前泣谏，仪仗銮驾肃列雨后泥泞的御道旁。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无旌旗、无云烟、无飞鸟，空无一物。' + CHAR_XW + CHAR_LC + CHAR_XT + SET_LY + '。' + STYLE + '。' + NOTEXT),
    ('02-南迁定计',
     '朝堂议事：魏主按案而立决意南迁，群臣分列左右；李冲出班进言，安定王休等老臣相顾失色。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无柱无幔，空无一物。' + CHAR_XW + CHAR_LC + CHAR_XT + SET_CT + '。' + STYLE + '。' + NOTEXT),
    ('03-断诸北语',
     '大殿颁诏：魏主立于御座前朗声宣诏，群臣俯首听命，殿中汉臣鲜卑大臣分列。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无柱无幔无器物，空无一物。' + CHAR_XW + SET_CT + '。' + STYLE + '。' + NOTEXT),
    ('04-改姓元氏',
     '宗庙颁册：魏主手捧册命立于案前，案上展开氏族简册；鲜卑贵族依序列班，垂首受命。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无柱无幔，空无一物。' + CHAR_XW + SET_CT + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-戎服执鞭', ['魏主自发平城至洛阳霖雨不止',
                      '帝戎服执鞭乘马而出',
                      '群臣稽颡于马前',
                      '帝曰庙算已定大军将进诸公更欲何云']),
    ('02-南迁定计', ['吾方经营天下期于混壹',
                      '而卿等儒生屡疑大计',
                      '斧钺有常卿勿复言',
                      '今者兴发不小动而无成何以示后',
                      '欲迁者左不欲者右',
                      '遂定迁都之计']),
    ('03-断诸北语', ['今欲断诸北语一从正音',
                      '其年三十已上习性已久容不可猝革',
                      '三十已下见在朝廷之人语音不听仍旧',
                      '若有故为当加降黜各宜深戒']),
    ('04-改姓元氏', ['北人谓土为拓后为跋',
                      '魏之先出于黄帝以土德王故为拓跋氏',
                      '宜改姓元氏',
                      '始改拔拔氏为长孙氏',
                      '独孤氏为刘氏']),
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
    print('下一步：../../verify_batch.py 汉化 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
