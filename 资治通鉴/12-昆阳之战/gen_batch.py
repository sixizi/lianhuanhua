# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 12 昆阳之战（卷三十九 · 汉纪三十一 · 更始元年（公元23年））批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
四幕：十三骑出城 / 围城数十重 / 敢死者三千 / 屋瓦皆飞。
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

CHAR_LX = '同一人：刘秀，二十八岁的青年将军，隆准日角，面容沉毅清朗，束发皮弁，身着玄色皮甲外罩绛红披风，身姿挺拔。'
CHAR_WF = '王凤：守城的更始将领，浓眉虬髯的中年武将，铁甲皂袍，神情惶急。'
CHAR_WY = '王邑：王莽的统帅，骄悍的中年大司马，头戴武冠，金甲锦袍，神情倨傲。'
CHAR_JMB = '巨毋霸：身高丈余的巨人垒尉，体型魁伟如塔，兽皮战袍，手牵猛兽。'
CHAR_WX = '王寻：王莽大将，白面短须，金甲红袍。'
SET_KY = '昆阳城：小型夯土城池，城小而坚，城头旌旗杂色；城外王莽大军列营百数，钲鼓连天，云车高架，猛兽（虎豹犀象）随军。'
SET_YE = '城外旷野战场：溃兵奔走，伏尸百余里，滍川泛滥，风雨雷电大作，屋瓦乱飞。'

SCENES = [
    ('01-十三骑出城',
     '昆阳城南门夜色：刘秀率十二骑衔枚而出，城门缝隙间透出火光，城头守将王凤凭堞目送，远处莽军营火连绵如星海。夜骑队伍位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无火光、无云烟、无飞鸟，空无一物。' + CHAR_LX + CHAR_WF + SET_KY + '。' + STYLE + '。' + NOTEXT),
    ('02-围城数十重',
     '昆阳城全景：王莽大军围之数十重，列营百数，云车高耸，钲鼓旌旗漫野；巨毋霸驱虎豹犀象在阵前助威，王邑金甲立于将台倨傲指挥。城池与军阵集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无营垒、无旌旗、无猛兽，空无一物。' + CHAR_WY + CHAR_JMB + SET_KY + '。' + STYLE + '。' + NOTEXT),
    ('03-敢死者三千',
     '昆阳城西水畔：刘秀一马当先，率敢死者三千人从城西水上冲击莽军中坚，王寻在阵中仓皇应对，莽军大阵骚然溃乱，汉兵无不以一当百。冲杀场面集中于画面左半幅与下半幅，水纹横在左下，画面右半幅自上而下保持纯宣纸留白，无兵戈、无旗帜、无飞鸟，空无一物。' + CHAR_LX + CHAR_WX + SET_YE + '。' + STYLE + '。' + NOTEXT),
    ('04-屋瓦皆飞',
     '溃战风雨旷野：莽兵大溃自相腾践，伏尸蔽野；天空雷电大作，屋瓦皆飞，雨下如注，滍川盛溢，虎豹股战，士卒赴水溺死者以万数。溃兵与洪水集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无雨脚、无雷电、无云烟，空无一物。' + CHAR_JMB + SET_YE + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-十三骑出城', ['今兵谷既少而外寇强大',
                      '并力御之功庶可立',
                      '时城中唯有八九千人',
                      '夜与五威将军李轶等十三骑出城南门']),
    ('02-围城数十重', ['时莽兵到城下者且十万',
                      '今将百万之众',
                      '遇城而不能下非所以示威也',
                      '遂围之数十重列营百数',
                      '钲鼓之声闻数十里']),
    ('03-敢死者三千', ['诸将胆气益壮无不一当百',
                      '秀乃与敢死者三千人',
                      '从城西水上冲其中坚',
                      '寻邑易之自将万馀人行陈',
                      '汉兵乘锐崩之遂杀王寻']),
    ('04-屋瓦皆飞', ['城中亦鼓噪而出',
                      '中外合势震呼动天地',
                      '莽兵大溃走者相腾践伏尸百馀里',
                      '会大雷风屋瓦皆飞雨下如注',
                      '虎豹皆股战士卒赴水溺死者以万数',
                      '水为不流']),
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
    print('下一步：../../verify_batch.py 昆阳 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
