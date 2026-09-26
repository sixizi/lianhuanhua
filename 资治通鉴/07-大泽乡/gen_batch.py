# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 07 大泽乡（卷七 · 秦纪二 · 二世皇帝元年）批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
四幕：失期当斩 / 坛盟誓师 / 攻拔蕲陈 / 张楚立国。
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

CHAR_CS = '同一人：陈胜，三十岁上下的戍卒屯长，方面大耳，浓眉阔口，粗布短褐束腰，头裹布巾，目光炯炯如炬。'
CHAR_WG = '吴广：与陈胜同龄的戍卒屯长，憨厚壮实，络腮短须，粗布短褐。'
SET_YU = '大泽乡雨营：滂沱大雨中的戍卒营地，泥泞旷野，破旧军帐歪斜，戍卒衣褐蜷缩。'
SET_TAN = '盟誓土坛：旷野中夯土高坛，柴薪烈焰，旌旗猎猎。'
SET_CHENG = '楚地城邑：夯土城墙巍然，里巷门户，市井烟火。'

SCENES = [
    ('01-失期当斩',
     '大泽乡雨营：滂沱大雨倾盆，道路泥泞不通，九百戍卒困守破帐，陈胜与吴广立于雨中仰望天色，神情决绝。人物在画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无雨丝无云，空无一物。' + CHAR_CS + CHAR_WG + SET_YU + '。' + STYLE + '。' + NOTEXT),
    ('02-坛盟誓师',
     '旷野土坛上：篝火熊熊，陈胜立于坛顶振臂高呼，吴广按剑立于侧，戍卒们举臂盟誓怒形于色，坛下人群如潮。人群集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无火光无旗，空无一物。' + CHAR_CS + CHAR_WG + SET_TAN + '。' + STYLE + '。' + NOTEXT),
    ('03-攻拔蕲陈',
     '行军途中：起义队伍执木棒农械浩荡前进，攻破的城门在侧后敞开，民众箪食相迎，旌旗招展。队伍沿画面左侧向远景推进，画面右半幅自上而下保持纯宣纸留白，空无一物。' + CHAR_CS + SET_CHENG + '。' + STYLE + '。' + NOTEXT),
    ('04-张楚立国',
     '陈县城头：陈胜按剑立于城头，披风扬起，身后大旗猎猎，城下军民拜贺声势如潮。人物集中在画面左半幅，城楼在左侧，画面右半幅自上而下保持纯宣纸留白，空无一物。' + CHAR_CS + SET_CHENG + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-失期当斩', ['发闾左戍渔阳九百人屯大泽乡',
                      '会天大雨道不通度已失期',
                      '失期法皆斩']),
    ('02-坛盟誓师', ['乃杀将尉召令徒属曰',
                      '且壮士不死则已死则举大名耳',
                      '王侯将相宁有种乎']),
    ('03-攻拔蕲陈', ['攻大泽乡拔之收而攻蕲',
                      '行收兵比至陈卒数万人',
                      '陈胜乃入据陈']),
    ('04-张楚立国', ['豪杰父老请立涉为楚王',
                      '遂自立为王号张楚',
                      '诸郡县苦秦法争杀长吏以应涉']),
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
    print('下一步：../../verify_batch.py 大泽乡 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
