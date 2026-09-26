# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 03 马陵道（卷二 · 周纪二 · 显王二十八年）批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
四幕：魏韩相攻 / 减灶诱敌 / 马陵设伏 / 万弩齐发。
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

CHAR_SUN = '同一人：军师孙膑，清瘦的中年人，须发斑白，双腿不便，安坐于四轮木车之中，手抚简册，神情沉静而目光深邃。'
CHAR_TIAN = '上将军田忌：高大魁伟的中年将军，虬髯短须，顶盔贯甲，外罩深青色战袍。'
CHAR_PANG = '魏将庞涓：身材魁梧的中年将军，浓眉锐目，短髯，顶盔披甲，绛红色披风，神情骄悍急躁。'
SET_QITANG = '齐国朝堂：木构大殿，立柱帷幔，案几陈简。'
SET_CAMP = '行军营地：旷野中的连营，土灶成行，炊烟袅袅。'
SET_MALING = '马陵道：两山夹峙的狭窄隘道，古木参天，一株大树树干被剥皮刷白，暮色四合，山影沉沉。'

SCENES = [
    ('01-魏韩相攻',
     '齐国朝堂上：孙膑坐于木车中进言献策，田忌按剑立于车侧，齐王坐于上首倾听，案上摊着军情简册。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，空无一物。' + CHAR_SUN + CHAR_TIAN + SET_QITANG + '。' + STYLE + '。' + NOTEXT),
    ('02-减灶诱敌',
     '魏地旷野：齐军行军营地土灶由近及远渐次减少，近处灶坑密集、远处稀疏，军士拔营东行；庞涓率轻骑赶到灶坑前察看，抬须而笑志得意满。庞涓一行在画面左侧中景，灶群在左下方，画面右半幅自上而下保持纯宣纸留白，无烟无山，空无一物。' + CHAR_PANG + SET_CAMP + '。' + STYLE + '。' + NOTEXT),
    ('03-马陵设伏',
     '马陵道夜色中：狭窄隘道两侧山坡上万名弓弩手隐于草木间张弓待发，道旁一株大树树干剥皮刷白，山道蜿蜒没入黑暗。伏兵与树木集中在画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无山无树无兵，空无一物。' + SET_MALING + '。' + STYLE + '。' + NOTEXT),
    ('04-万弩齐发',
     '马陵道深夜：火光乍起，万弩齐发，箭如飞蝗自两侧山间射向隘道，庞涓在火光下拄剑立于刷白的大树旁，身被数创仰天长啸，魏军四散奔逃。战事集中于画面左半幅与下半幅，火光与弩箭不越过画面右侧三分之一，画面右半幅自上而下保持纯宣纸留白，空无一物。' + CHAR_PANG + SET_MALING + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-魏韩相攻', ['魏庞涓伐韩韩请救于齐',
                      '乃阴许韩使而遣之',
                      '孙子为师以救韩直走魏都']),
    ('02-减灶诱敌', ['乃使齐军入魏地为十万灶',
                      '明日为五万灶又明日为二万灶',
                      '庞涓大喜弃其步军倍日并行逐之']),
    ('03-马陵设伏', ['马陵道狭而旁多阻隘可伏兵',
                      '乃斫大树白而书之曰',
                      '庞涓死此树下']),
    ('04-万弩齐发', ['庞涓果夜到斫木下见白书',
                      '读未毕万弩俱发魏师大乱',
                      '庞涓自知智穷兵败乃自刭']),
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
    print('下一步：../../verify_batch.py 马陵 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
