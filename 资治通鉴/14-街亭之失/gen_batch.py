# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 14 街亭之失（卷七十一 · 魏纪三 · 太和二年（公元228年））批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
四幕：舍水上山 / 绝其汲道 / 挥泪斩谡 / 自贬三等。
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

CHAR_KM = '同一人：诸葛亮，四十七岁的汉丞相，面容清癯，头戴纶巾，身着素色鹤氅，手执白羽扇，神情肃穆深沉。'
CHAR_MS = '同一人：马谡，三十八岁的汉军先锋，面有傲气，短须，亮银甲外罩青色战袍，神态自负。'
CHAR_WP = '王平：沉稳老成的裨将，面色黧黑，虬髯，玄甲皂袍，神情恳切。'
CHAR_ZH = '张郃：魏国宿将，年过五旬，白髯垂胸，金甲绛袍，用兵老辣沉毅。'
SET_JT = '街亭山地：孤山耸峙，马谡军舍水上山列于山脊，山下汲道蜿蜒，魏军铁骑自谷口展开。'
SET_HZ = '汉中丞相行辕：木构厅堂，案上摊地图，简册堆叠，武士肃立。'

SCENES = [
    ('01-舍水上山',
     '街亭山脊：马谡按剑立于山顶指挥，蜀军舍水上山列阵，旌旗布满山脊；王平在山坡下拱手力谏，神情恳切。山体与人物集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无山石、无云烟、无旌旗，空无一物。' + CHAR_MS + CHAR_WP + SET_JT + '。' + STYLE + '。' + NOTEXT),
    ('02-绝其汲道',
     '街亭山下：张郃率魏军铁骑截断汲水之道，山谷间蜀军取水兵士被驱散；山脊上蜀军大乱旗帜歪斜，惟王平所领千人鸣鼓自守阵脚不乱。战事集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无山影、无兵戈、无飞鸟，空无一物。' + CHAR_ZH + CHAR_WP + SET_JT + '。' + STYLE + '。' + NOTEXT),
    ('03-挥泪斩谡',
     '汉中行辕阶前：马谡蓬发戴罪跪于阶下，诸葛亮端坐案后执羽扇垂泪，监斩武士按刀肃立，群臣莫敢仰视。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无柱无幔无兵器，空无一物。' + CHAR_KM + CHAR_MS + SET_HZ + '。' + STYLE + '。' + NOTEXT),
    ('04-自贬三等',
     '行辕堂内：诸葛亮伏案上疏，案上简册摊开，印绶置于案角；堂下蒋琬等大臣肃立，神情叹惋。诸葛亮在画面左半幅中景，画面右半幅自上而下保持纯宣纸留白，无柱无幔，空无一物。' + CHAR_KM + SET_HZ + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-舍水上山', ['马谡言过其实不可大用',
                      '谡违亮节度举措烦扰',
                      '舍水上山不下据城']),
    ('02-绝其汲道', ['绝其汲道击大破之',
                      '惟平所领千人鸣鼓自守',
                      '疑其有伏兵不往逼也',
                      '亮进无所据乃拔西县千馀家还汉中']),
    ('03-挥泪斩谡', ['收谡下狱杀之',
                      '亮自临祭为之流涕',
                      '抚其遗孤恩若平生',
                      '四海分裂兵交方始',
                      '若复废法何用讨贼邪']),
    ('04-自贬三等', ['昔楚杀得臣文公喜可知也',
                      '天下未定而戮智计之士岂不惜乎',
                      '亮上疏请自贬三等',
                      '汉主以亮为右将军行丞相事']),
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
    print('下一步：../../verify_batch.py 街亭 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
