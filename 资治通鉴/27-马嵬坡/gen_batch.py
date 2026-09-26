# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 27 马嵬坡（卷二一八 · 唐纪三十四 · 至德元年（公元756年））批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
五幕：将士皆怒 / 追杀国忠 / 割恩正法 / 佛堂缢贵妃 / 父老遮道。
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

CHAR_TXZ = '同一人：唐玄宗李隆基，七十一岁的出逃天子，须发皆白，头戴折上巾，身着赭黄便袍外罩素色氅，形容疲惫苍凉。'
CHAR_YGB = '杨国忠：宰相，体态臃肿，紫袍金带，中箭奔逃，狼狈惊惶。'
CHAR_YGF = '杨贵妃：云鬓花颜的贵妃，素白宫装，神情凄婉决绝。'
CHAR_GLS = '高力士：白发的老宦者，紫衣供奉，垂首奉命。'
CHAR_CXL = '陈玄礼：龙武大将军，铁甲白须，神情悲壮。'
SET_MW = '马嵬驿：荒驿土墙，驿门狭窄，将士围驿，旌旗歪斜，晨光惨淡。'
SET_FT = '驿中佛堂：佛龛昏暗，帐幔低垂，香烟一缕，静寂无声。'
SET_GD = '官道父老：黄土官道，父老数千人跪伏遮道，尘土飞扬。'

SCENES = [
    ('01-将士皆怒',
     '马嵬驿前：将士饥疲皆愤怒，甲士列队围驿鼓噪，陈玄礼按剑晓谕军士，驿门内灯影摇曳。人群位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无旌旗、无烟尘、无飞鸟，空无一物。' + CHAR_CXL + SET_MW + '。' + STYLE + '。' + NOTEXT),
    ('02-追杀国忠',
     '驿前骚乱：军士呼喊追杀杨国忠，杨国忠中鞍坠逃，吐蕃使者遮马陈诉，乱兵四合。骚乱集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无兵戈、无烟尘，空无一物。' + CHAR_YGB + SET_MW + '。' + STYLE + '。' + NOTEXT),
    ('03-割恩正法',
     '驿门内外：玄宗倚杖立于驿门，倾首而立神情苍凉，军士免胄释甲顿首请罪，韦谔叩头流血。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无兵戈、无旌旗，空无一物。' + CHAR_TXZ + CHAR_CXL + SET_MW + '。' + STYLE + '。' + NOTEXT),
    ('04-佛堂缢贵妃',
     '驿中佛堂：高力士引贵妃入佛堂，佛龛香烟一缕，贵妃素装回望，帐幔低垂，玄宗门外掩面。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无帐幔纹、无香烟、无器物，空无一物。' + CHAR_YGF + CHAR_GLS + SET_FT + '。' + STYLE + '。' + NOTEXT),
    ('05-父老遮道',
     '官道之上：父老数千遮道跪请，攀援车驾，玄宗按辔久之，太子于后宣慰。人群车驾集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无烟尘、无旌旗、无飞鸟，空无一物。' + CHAR_TXZ + SET_GD + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-将士皆怒', ['至马嵬驿将士饥疲皆愤怒',
                      '陈玄礼以祸由杨国忠欲诛之',
                      '会吐蕃使者二十余人遮国忠马',
                      '诉以无食',
                      '国忠未及对军士呼曰国忠与胡虏谋反']),
    ('02-追杀国忠', ['或射之中鞍国忠走至西门内',
                      '军士追杀之屠割支体',
                      '以枪揭其首于驿门外']),
    ('03-割恩正法', ['上杖屦出驿门慰劳军士',
                      '令收队军士不应',
                      '国忠谋反贵妃不宜供奉',
                      '愿陛下割恩正法',
                      '上曰朕当自处之入门倚杖倾首而立']),
    ('04-佛堂缢贵妃', ['贵妃诚无罪然将士已杀国忠',
                      '而贵妃在陛下左右岂敢自安',
                      '上乃命力士引贵妃于佛堂',
                      '缢杀之舆尸置驿庭',
                      '舆尸置驿庭召玄礼等入视之']),
    ('05-父老遮道', ['及行父老皆遮道请留曰',
                      '宫阙陛下家居陵寝陛下坟墓',
                      '今舍此欲何之',
                      '上为之按辔久之',
                      '乃命太子于后宣慰父老']),
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
    print('下一步：../../verify_batch.py 马嵬 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
