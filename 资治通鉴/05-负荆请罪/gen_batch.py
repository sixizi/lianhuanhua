# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 05 负荆请罪（卷四 · 周纪四 · 赧王三十六年）批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
四幕：渑池之会 / 引车避匿 / 先国后私 / 负荆谢罪。
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

CHAR_XR = '同一人：蔺相如，三十岁上下的赵国上卿，面容端正儒雅，三绺短须，束发戴高冠，身着月白色朝服，神情从容坚毅。'
CHAR_LP = '同一人：廉颇，五十余岁的赵国宿将，虬髯如戟，须发花白，体格魁伟，出行时着绛色官袍。'
CHAR_QW = '同一人：秦昭王，三十余岁的秦国之王，面容雄鸷，冠冕玄袍，坐于宴席上首。'
CHAR_ZW = '赵惠文王：年轻的赵国国君，眉目温润，头戴高冠，身着绛红色王袍。'
SET_MIANCHI = '渑池会盟大帐：秦赵两王对坐，樽俎罗列，甲士分立帐侧，帐外风旗猎猎。'
SET_STREET = '邯郸街市：夯土里墙，车马道分岔，路旁槐柳。'
SET_TINGYUAN = '庭院：席案对设，廊柱一角，盆栽松影。'
SET_FUMEN = '蔺相如府门：黑漆大门，台阶高起，府前空地。'

SCENES = [
    ('01-渑池之会',
     '渑池盟帐中：秦王与赵王对坐宴饮，蔺相如立于赵王身后，昂然趋前一步直视秦王，秦王拂然变色，两侧甲士按剑欲动。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，空无一物。' + CHAR_XR + CHAR_QW + CHAR_ZW + SET_MIANCHI + '。' + STYLE + '。' + NOTEXT),
    ('02-引车避匿',
     '邯郸街市：廉颇的车马仪仗昂然直行于大道，蔺相如的车驾悄然退避入侧巷，驭者小心引缰，相如端坐车中神色平和。两驾车马都在画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，空无一物。' + CHAR_LP + CHAR_XR + SET_STREET + '。' + STYLE + '。' + NOTEXT),
    ('03-先国后私',
     '蔺相如府中庭院：相如与舍人对坐言谈，舍人愤然起身欲去，相如抬手挽留从容解释，神情恳切。二人在画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，空无一物。' + CHAR_XR + SET_TINGYUAN + '。' + STYLE + '。' + NOTEXT),
    ('04-负荆谢罪',
     '蔺相如府门前：廉颇袒露一肩背负荆条，跪于门前请罪；蔺相如快步出府俯身搀扶，二人相视动容。二人在画面左半幅与下半幅，府门在左侧，画面右半幅自上而下保持纯宣纸留白，空无一物。' + CHAR_LP + CHAR_XR + SET_FUMEN + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-渑池之会', ['秦王请赵王鼓瑟赵王鼓之',
                      '蔺相如复请秦王击缶',
                      '五步之内臣请得以颈血溅大王矣']),
    ('02-引车避匿', ['以蔺相如为上卿位在廉颇之右',
                      '我见相如必辱之',
                      '出而望见辄引车避匿']),
    ('03-先国后私', ['今两虎共斗其势不俱生',
                      '先国家之急而后私仇也']),
    ('04-负荆谢罪', ['廉颇闻之肉袒负荆至门',
                      '遂为刎颈之交']),
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
    print('下一步：../../verify_batch.py 负荆 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
