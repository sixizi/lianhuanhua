# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 28 雪夜入蔡州（卷二四〇 · 唐纪五十六 · 元和十二年（公元817年））批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
五幕：李佑归降 / 雪夜出兵 / 张柴东行 / 城下坎登 / 梯下元济。
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

CHAR_LS = '同一人：李诉，四十岁的唐随唐邓节度使，面容温和儒雅，短须，风帽轻裘，用兵深沉不测。'
CHAR_LYZ = '李佑：淮西降将，三十余岁，虬髯健壮，铁甲旧痕，感恩效死。'
CHAR_DSL = '丁士良：淮西骁将，三十余岁，虬髯悍勇，战袍染尘，被擒释缚后感恩戴德。'
CHAR_JC = '李进诚：部将，方正忠勇，铁甲红袍。'
CHAR_WYJ = '吴元济：淮西叛帅，体壮目骄，锦袍暖帽，倨傲贪眠。'
SET_ZC = '张柴村雪夜：风雪怒号，旌旗冻裂，军士衔枚，火把皆熄。'
SET_CZ = '蔡州城下：夜半雪愈甚，鹅鸭池畔军士坎城，城头柝声如故，城下云梯暗立。'
SET_YC = '蔡州牙城：内外城之间，雪止天明，牙城短垣，槛车陈列。'

SCENES = [
    ('01-士良归降',
     '军帐之内：丁士良解缚披袍立于案前，李诉亲执其手温言相慰，烛光下推心置腹。二人位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无烛焰、无帐纹，空无一物。' + CHAR_LS + CHAR_DSL + '。' + STYLE + '。' + NOTEXT),
    ('02-雪夜出兵',
     '雪夜军门：大军冒雪夜出，军士鼓旗冻裂，李诉风帽轻裘立马门旗之下，诸将请所之。军列沿画面左半幅延伸，画面右半幅自上而下保持纯宣纸留白，无雪片、无旌旗、无火光，空无一物。' + CHAR_LS + SET_ZC + '。' + STYLE + '。' + NOTEXT),
    ('03-张柴东行',
     '张柴村风雪道：军行六十里夜至张柴村，尽杀戍卒据栅，军士食干粮整羁靮，复夜引兵出门东行。队伍位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无雪片、无栅影，空无一物。' + CHAR_LS + CHAR_LYZ + SET_ZC + '。' + STYLE + '。' + NOTEXT),
    ('04-城下坎登',
     '蔡州城下雪夜：近城有鹅鸭池，军士惊鹅鸭以混军声，李佑李忠义鎌城为坎先登，壮士从之，守门卒熟寐。城垣与登城壮士集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无雪片、无城影、无飞禽，空无一物。' + CHAR_LYZ + SET_CZ + '。' + STYLE + '。' + NOTEXT),
    ('05-梯下元济',
     '蔡州牙城：晡时门坏，吴元济于城上请罪，李进诚以梯接之下城，槛车待缚，雪霁天青。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无兵器、无旌旗、无云影，空无一物。' + CHAR_WYJ + CHAR_JC + SET_YC + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-士良归降', ['诉曰真丈夫也命释其缚',
                      '昨日力屈复为公所擒亦分死矣',
                      '今公又生之',
                      '请尽死以报德',
                      '诉乃给其衣服器械署为捉生将']),
    ('02-雪夜出兵', ['命李佑李忠义帅突将三千为前驱',
                      '军出不知所之诉曰但东行',
                      '时大风雪旌旗裂人马冻死者相望',
                      '天阴黑自张柴村以东道路',
                      '皆官军所未尝行']),
    ('03-张柴东行', ['行六十里夜至张柴村',
                      '尽杀其戍卒及烽子',
                      '据其栅命士卒少休',
                      '留义成军五百人镇之以断朗山救兵',
                      '复夜引兵出门诸将请所之',
                      '诉曰入蔡州取吴元济',
                      '诸将皆失色']),
    ('04-城下坎登', ['夜半雪愈甚行七十里至州城',
                      '近城有鹅鸭池诉令惊之以混军声',
                      '守门卒方熟寐尽杀之',
                      '而留击柝者使击柝如故',
                      '遂开门纳众及里城亦然城中皆不之觉']),
    ('05-梯下元济', ['鸡鸣雪止诉入居元济外宅',
                      '又有告者曰城陷矣',
                      '元济曰此必洄曲子弟就吾求寒衣也',
                      '起听于廷闻诉军号令曰',
                      '常侍传语应者近万人',
                      '癸酉复攻之烧其南门民争负薪刍助之',
                      '晡时门坏元济于城上请罪',
                      '进诚梯而下之']),
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
    print('下一步：../../verify_batch.py 蔡州 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
