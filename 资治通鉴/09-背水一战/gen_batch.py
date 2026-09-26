# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 09 背水一战（卷十 · 汉纪二 · 高帝三年）批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
四幕：夜传赤帜 / 背水列阵 / 拔旗易帜 / 泜水全胜。
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

CHAR_HX = '同一人：韩信，三十岁上下的汉军统帅，面容清朗，眉目疏朗，束发戴将冠，身着玄色将袍外披皮甲，按剑而立，气度从容。'
CHAR_ZE = '张耳：年长的汉军将佐，花白须发，甲胄在身。'
SET_YEJING = '夜半山道：暗色山径，松影幢幢，远处营火。'
SET_RIVER = '绵蔓水畔：河岸开阔，水色苍茫，军阵背水列开。'
SET_YING = '赵军营垒：木栅望楼，旗帜林立。'

SCENES = [
    ('01-夜传赤帜',
     '夜半井陉山中：两千轻骑各持一面红色旗帜沿山间小道潜行，暗中望向远处赵军营垒的火光；山道另一处篝火旁韩信传令军餐，众将面面相觑。轻骑队伍在画面左半幅蜿蜒，赵营火光在远景左侧，画面右半幅自上而下保持纯宣纸留白，空无一物。' + CHAR_HX + SET_YEJING + '。' + STYLE + '。' + NOTEXT),
    ('02-背水列阵',
     '绵蔓水畔晨光：汉军万人在河岸背水列阵，阵前旌旗戈戟如林，韩信建大将旗鼓立于阵前，对岸远处赵军营垒中赵兵凭壁观望而笑。汉军阵在画面左半幅与下半幅，赵营远在远景左侧，画面右半幅自上而下保持纯宣纸留白，空无一物。' + CHAR_HX + SET_RIVER + '。' + STYLE + '。' + NOTEXT),
    ('03-拔旗易帜',
     '赵军营垒突袭：营垒中汉军二千轻骑驰入，纷纷拔掉赵军旗帜换插红色汉旗，营中已无守卒，远处赵军主力正倾城而出。营垒与骑士在画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，空无一物。' + SET_YING + '。' + STYLE + '。' + NOTEXT),
    ('04-泜水全胜',
     '河畔战场：汉军前后夹击大破赵军，赵兵丢盔弃甲溃散，韩信立马高坡俯瞰战场，汉旗招展。战事集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，空无一物。' + CHAR_HX + SET_RIVER + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-夜传赤帜', ['夜半传发选轻骑二千人',
                      '赵见我走必空壁逐我',
                      '今日破赵会食']),
    ('02-背水列阵', ['乃使万人先行出背水陈',
                      '赵军望见而大笑',
                      '信建大将旗鼓鼓行出井陉口']),
    ('03-拔旗易帜', ['赵果空壁争汉旗鼓',
                      '驰入赵壁皆拔赵旗立汉赤帜',
                      '壁皆汉赤帜见而大惊']),
    ('04-泜水全胜', ['汉兵夹击大破赵军',
                      '大破赵军斩成安君禽赵王歇',
                      '陷之死地而后生置之亡地而后存']),
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
    print('下一步：../../verify_batch.py 背水 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
