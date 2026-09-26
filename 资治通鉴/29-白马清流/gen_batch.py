# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 29 白马清流（卷二六五 · 唐纪八十一 · 天佑二年（公元905年））批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
四幕：缙绅之祸 / 集于白马驿 / 一夕尽杀 / 投尸于河。
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

CHAR_QZ = '裴枢：白须垂胸的老宰相，朝服端正，神情傲骨凛然。'
CHAR_LZ = '李振：落魄文吏出身的中年谋士，青袍纶巾，面带讥诮，心怀怨毒。'
CHAR_ZQZ = '朱全忠：宣武节度使，虎背熊腰，络腮短须，戾气逼人。'
SET_GY = '洛阳宫省：宫署廊院，朝士贬官络绎出京，胥吏点检名册。'
SET_BM = '白马驿：黄河岸边驿站，暮色苍茫，河声隐隐，驿亭孤峙。'
SET_HH = '黄河岸边之夜：夜色深沉，尸积如柴，浊浪排空，寒鸦惊起。'

SCENES = [
    ('01-缙绅之祸',
     '洛阳宫省廊院：贬官朝士数十人被军士押出宫门，裴枢白须朝服行于队首，胥吏持册点名。人群位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无兵戈、无旌旗、无飞鸟，空无一物。' + CHAR_QZ + SET_GY + '。' + STYLE + '。' + NOTEXT),
    ('02-集于白马驿',
     '白马驿暮色：朝士三十余人被驱集于驿亭之前，驿卒闭门，暮云低垂黄河声远。人群位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无驿墙、无暮云、无飞鸟，空无一物。' + CHAR_QZ + SET_BM + '。' + STYLE + '。' + NOTEXT),
    ('03-一夕尽杀',
     '驿中夜变：夜色中军士环逼朝士，刀光隐约，李振立于驿门阴影中冷眼旁观。人群位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无刀光、无驿影，空无一物。' + CHAR_LZ + SET_BM + '。' + STYLE + '。' + NOTEXT),
    ('04-投尸于河',
     '黄河岸边之夜：朱全忠按刀立于河堤冷笑，李振在旁进言，浊流滚滚东去。二人位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无水波、无尸影、无飞鸟，空无一物。' + CHAR_ZQZ + CHAR_LZ + SET_HH + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-缙绅之祸', ['柳璨及第不四年为宰相性倾巧轻佻',
                      '时天子左右皆朱全忠腹心',
                      '同列裴枢崔远独孤损',
                      '皆朝廷宿望意轻之',
                      '璨以为憾']),
    ('02-集于白马驿', ['敕裴枢独孤损崔远王溥',
                      '赵崇王赞等并所在赐自尽',
                      '时全忠聚枢等及朝士贬官者',
                      '三十余人于白马驿']),
    ('03-一夕尽杀', ['一夕尽杀之投尸于河',
                      '李振屡举进士竟不中第',
                      '故深疾缙绅之士']),
    ('04-投尸于河', ['此辈常自谓清流宜投之黄河使为浊流',
                      '全忠笑而从之',
                      '振每自汴至洛朝廷必有窜逐者',
                      '时人谓之鸱枭']),
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
    print('下一步：../../verify_batch.py 白马 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
