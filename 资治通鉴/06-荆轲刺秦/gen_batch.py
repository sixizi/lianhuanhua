# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 06 荆轲刺秦（卷六末 · 秦纪二 · 始皇帝二十年）批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
四幕：樊督之献 / 奉图入秦 / 图穷匕见 / 中柱而诛。
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

CHAR_JK = '同一人：荆轲，三十岁上下的燕国刺客，身形挺拔，剑眉朗目，三绺长髯，束发劲装，外罩灰褐色披风，神情沉毅决绝。'
CHAR_FAN = '樊於期：四五十岁的落魄秦将，须发斑白，颧骨高峻，身着素色旧袍，神情悲怆。'
CHAR_QW2 = '秦王嬴政：三旬上下的雄主，眉骨高峻，目光冷锐，冠冕玄袍。'
SET_KE = '燕国客舍：木屋一间，油灯昏光，席案对坐。'
SET_QINDIAN2 = '秦国大殿：幽深高殿，两侧群臣分列皆无兵刃，殿中铜柱巍然矗立，光从殿门斜入。'

SCENES = [
    ('01-樊督之献',
     '燕国客舍夜：荆轲与樊於期对席而坐，荆轲俯身低语陈说，樊於期握拳切齿，泪光闪动，案上油灯摇曳。二人在画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，空无一物。' + CHAR_JK + CHAR_FAN + SET_KE + '。' + STYLE + '。' + NOTEXT),
    ('02-奉图入秦',
     '秦国大殿：秦王朝服端坐上首，设九宾之礼，荆轲捧图轴趋步向前，群臣肃立，殿中气象森严。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，空无一物。' + CHAR_JK + CHAR_QW2 + SET_QINDIAN2 + '。' + STYLE + '。' + NOTEXT),
    ('03-图穷匕见',
     '秦国大殿惊变：荆轲抓住秦王衣袖，秦王惊起挣断衣袖绕柱而逃，群臣惊愕失措以手共搏，殿中铜柱高耸。追逐集中在画面左半幅，铜柱在左中，画面右半幅自上而下保持纯宣纸留白，空无一物。' + CHAR_JK + CHAR_QW2 + SET_QINDIAN2 + '。' + STYLE + '。' + NOTEXT),
    ('04-中柱而诛',
     '秦国大殿稍定：秦王负剑拔剑立于铜柱之侧，荆轲断股伤重倚柱而坐，犹自张口怒骂，掷出的匕首钉在铜柱上，殿上狼藉。人物集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，空无一物。' + CHAR_JK + CHAR_QW2 + SET_QINDIAN2 + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-樊督之献', ['秦之遇将军可谓深矣',
                      '愿得将军之首以献秦王',
                      '此臣之日夜切齿腐心也遂自刎']),
    ('02-奉图入秦', ['荆轲至咸阳',
                      '王大喜朝服设九宾而见之',
                      '荆轲奉图以进于王']),
    ('03-图穷匕见', ['图穷而匕首见',
                      '王惊起袖绝荆轲逐王',
                      '王环柱而走群臣皆愕']),
    ('04-中柱而诛', ['王负剑遂拔以击荆轲',
                      '断其左股荆轲废',
                      '事所以不成者以欲生劫之']),
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
    print('下一步：../../verify_batch.py 荆轲 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
