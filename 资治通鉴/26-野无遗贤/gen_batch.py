# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 26 野无遗贤（卷二一五 · 唐纪三十一 · 天宝六载（公元747年））批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
四幕：明诏求士 / 恐其讪上 / 无一人及第 / 上表称贺。
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

CHAR_XZ2 = '同一人：唐玄宗，六十二年的天子，体态丰盈，头戴翼善冠，赭黄袍，神情倦怠而自负。'
CHAR_LLF2 = '同一人：李林甫，老奸宰相，面白丰腴，绛紫袍，笑容谦卑而目光深藏。'
CHAR_KS = '应试士子：布衣士人，青衫旧履，风尘满面，执卷而立。'
SET_DN = '大明宫丹凤门：宫门巍峨，士子成群捧卷候试，礼官点检。'
SET_KS = '考场廊院：长廊席位，士子伏案为诗赋论，烛炬成行，考官巡视。'
SET_BZ = '中书省奏堂：李林甫执表跪奏，玄宗倚案览奏，近侍屏息。'

SCENES = [
    ('01-明诏求士',
     '丹凤门前：求士诏下，四方士子负笈而来，宫门前人群攒动，礼官点检名册。人群位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无宫墙、无旌旗、无飞鸟，空无一物。' + CHAR_KS + SET_DN + '。' + STYLE + '。' + NOTEXT),
    ('02-恐其讪上',
     '中书省内：李林甫独对皇帝躬身建言，言辞恭谨而目光闪烁，玄宗坐听。二人位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无柱无幔无器物，空无一物。' + CHAR_LLF2 + CHAR_XZ2 + SET_BZ + '。' + STYLE + '。' + NOTEXT),
    ('03-无一人及第',
     '考场廊院：士子们伏案疾书诗赋论，烛炬燃尽，考官收卷唱名，众士子惶惶相顾。场景集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无烛焰、无席案，空无一物。' + CHAR_KS + SET_KS + '。' + STYLE + '。' + NOTEXT),
    ('04-上表称贺',
     '奏堂之上：李林甫捧表跪贺，玄宗抚案而笑，近侍相顾，堂外落雪无声。二人位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无幔帐、无器物、无灯焰，空无一物。' + CHAR_LLF2 + CHAR_XZ2 + SET_BZ + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-明诏求士', ['上欲广求天下之士',
                      '命通一艺以上皆诣京师']),
    ('02-恐其讪上', ['李林甫恐草野之士对策斥言其奸恶',
                      '举人多卑贱愚聩恐有俚言污浊圣听',
                      '乃令郡县长官精加试练',
                      '取名实相副者闻奏']),
    ('03-无一人及第', ['既而至者皆试以诗赋论',
                      '遂无一人及第者']),
    ('04-上表称贺', ['林甫乃上表贺野无遗贤']),
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
    print('下一步：../../verify_batch.py 遗贤 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
