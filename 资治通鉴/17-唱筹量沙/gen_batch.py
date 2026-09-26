# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 17 唱筹量沙（卷一百二十二 · 宋纪四 · 元嘉八年（公元431年））批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
四幕：食尽引还 / 唱筹量沙 / 白服乘舆 / 全军而还。
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

CHAR_TDJ = '同一人：檀道济，年过五旬的刘宋老将，苍髯虎目，铁甲外罩玄色战袍，神情从容镇定。'
CHAR_WR = '魏军：北魏轻骑，皮帽毡裘，纵马追蹑。'
SET_YK = '历城郊野：官道蜿蜒，齐军营地连绵，土囤粮堆陈列，夜色沉沉。'
SET_EK = '营地夜场：油灯昏黄，沙囤成行，军士以斗量沙唱筹，白米覆于沙上。'

SCENES = [
    ('01-食尽引还',
     '历城郊野暮色：檀道济率军自历城引还，队伍衔枚而行；旷野上魏军轻骑远远追蹑。行军队伍位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无烟尘、无骑影、无云烟，空无一物。' + CHAR_TDJ + CHAR_WR + SET_YK + '。' + STYLE + '。' + NOTEXT),
    ('02-唱筹量沙',
     '营地深夜：军士以斗量沙，一人执筹高声唱数，所馀白米覆于沙囤之上；檀道济按剑立于囤间督看，灯影幢幢。人物与粮囤位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无灯焰、无器物，空无一物。' + CHAR_TDJ + SET_EK + '。' + STYLE + '。' + NOTEXT),
    ('03-白服乘舆',
     '清晨营地外：军士皆被甲执兵列阵，檀道济白服乘舆，引兵徐徐而出，神色闲定；远处魏骑斥候窥望。队伍位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无烟尘、无骑影，空无一物。' + CHAR_TDJ + CHAR_WR + SET_YK + '。' + STYLE + '。' + NOTEXT),
    ('04-全军而还',
     '归途官道：魏军以为有伏兵不敢逼，稍稍引退；檀道济大军整队而还，旌旗严整，队尾衔前。行军队列沿画面左半幅延伸，画面右半幅自上而下保持纯宣纸留白，无烟尘、无云影，空无一物。' + CHAR_TDJ + SET_YK + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-食尽引还', ['檀道济等食尽自历城引还',
                      '军士有亡降魏者具告之',
                      '魏人追之将溃']),
    ('02-唱筹量沙', ['道济夜唱筹量沙',
                      '以所馀少米覆其上',
                      '及旦魏军见之谓道济资粮有馀',
                      '以降者为妄而斩之']),
    ('03-白服乘舆', ['时道济兵少魏兵甚盛骑士四合',
                      '道济命军士皆被甲',
                      '己白服乘舆引兵徐出']),
    ('04-全军而还', ['魏人以为有伏兵不敢逼',
                      '稍稍引退道济全军而返']),
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
    print('下一步：../../verify_batch.py 量沙 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
