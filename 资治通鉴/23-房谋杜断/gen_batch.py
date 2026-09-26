# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 23 房谋杜断（卷一九三 · 唐纪九 · 贞观三年（公元629年））批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
三幕：军门谒见 / 玄龄善谋 / 唐世推房杜。
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

CHAR_FXL = '同一人：房玄龄，五十岁的宰相，面容清朗温煦，三绺长须，头戴进贤冠，身着青色宰相袍服，目光深思。'
CHAR_DRH = '同一人：杜如晦，四十六岁的宰相，面容刚毅果断，短须如戟，头戴进贤冠，身着赭色宰相袍服，眉宇英决。'
CHAR_LSM = '同一人：李世民，年轻英武的秦王/天子，隆准朗目，束发戴弁，戎袍玉带。'
SET_JM = '渭北军门：辕门旌旗，甲士夹道，李世民立马门中受谒。'
SET_CT = '唐廷政事堂：大殿公座，案上文卷堆叠，臣工序立议政。'

SCENES = [
    ('01-军门谒见',
     '渭北军门：房玄龄布衣谒于马前，长揖进策；李世民立马辕门俯身相顾，一见如旧识，甲士夹道。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无旌旗、无甲士、无云烟，空无一物。' + CHAR_FXL + CHAR_LSM + SET_JM + '。' + STYLE + '。' + NOTEXT),
    ('02-玄龄善谋',
     '政事堂中：房玄龄执笔伏案草拟方略，杜如晦立于案侧朗声剖断，案上文卷累累，烛光映照。二人位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无柱无幔无烛焰，空无一物。' + CHAR_FXL + CHAR_DRH + SET_CT + '。' + STYLE + '。' + NOTEXT),
    ('03-唐世推房杜',
     '大殿议政：李世民坐于御案，房玄龄杜如晦并立阶前进奏，群臣肃立，殿宇庄重。三人位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无柱无幔无器物，空无一物。' + CHAR_LSM + CHAR_FXL + CHAR_DRH + SET_CT + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-军门谒见', ['隰城尉房玄龄谒世民于军门',
                      '世民一见如旧识署记室参军',
                      '引为谋主玄龄亦自以遇知己',
                      '罄竭心力知无不为']),
    ('02-玄龄善谋', ['上每与玄龄谋事必曰非如晦不能决',
                      '及如晦至卒用玄龄之策',
                      '盖玄龄善谋如晦能断故也',
                      '二人深相得同心徇国']),
    ('03-唐世推房杜', ['玄龄监修国史上语之曰',
                      '比见汉书载子虚上林赋',
                      '浮华无用',
                      '玄龄虽蒙宠待或以事被谴',
                      '辄累日诣朝堂稽颡请罪',
                      '故唐世称贤相者推房杜焉']),
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
    print('下一步：../../verify_batch.py 房杜 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
