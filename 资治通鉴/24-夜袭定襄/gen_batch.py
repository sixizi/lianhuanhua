# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 24 夜袭定襄（卷一九三 · 唐纪九 · 贞观四年（公元630年））批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
四幕：夜袭定襄 / 一日数惊 / 乘雾袭牙帐 / 漠南遂空。
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

CHAR_LJ = '同一人：李靖，五十九岁的老统帅，身材魁健，长髯戟张，铁甲外罩玄色战氅，用兵沉狠果决。'
CHAR_XD = '颉利可汗：突厥之主，体壮多须，金冠皮裘，坐狼头纛下，神情骄慢。'
CHAR_SDF = '苏定方：矫健的青年前锋骁骑，皮甲轻裘，挟弓纵马。'
CHAR_TJ = '唐俭：持节的唐朝使臣，博带高冠，神情镇定。'
SET_EY = '恶阳岭夜色：山岭月黑，唐军骁骑三千衔枚疾进，火把皆熄。'
SET_YZ = '突厥牙帐：穹庐毡帐连绵，狼头大纛高竖，帐中歌舞正酣。'
SET_WM = '大雾牙帐：黎明大雾弥漫，唐军二百骑前锋乘雾而行，去牙帐七里虏乃觉之。'
SET_DN = '阴山北漠：大漠风沙，突厥残众溃散，唐军斥候四出。'

SCENES = [
    ('01-夜袭定襄',
     '恶阳岭夜行：李靖率骁骑三千夜袭定襄，骑兵衔枚疾进山道，月黑风高。骑兵队列沿画面左半幅延伸，画面右半幅自上而下保持纯宣纸留白，无山影、无云烟、无火光，空无一物。' + CHAR_LJ + SET_EY + '。' + STYLE + '。' + NOTEXT),
    ('02-一日数惊',
     '突厥牙帐内：颉利可汗据坐主帐惊闻警讯，帐外穹庐间突厥部众惶惶奔走，一日数惊。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无毡帐纹、无纛旗，空无一物。' + CHAR_XD + SET_YZ + '。' + STYLE + '。' + NOTEXT),
    ('03-乘雾袭牙帐',
     '大雾黎明：苏定方率二百骑前锋乘雾而行直逼牙帐，雾中穹庐轮廓隐现，颉利乘千里马先走。骑队与毡帐集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无雾气、无骑影，空无一物。' + CHAR_SDF + CHAR_XD + SET_WM + '。' + STYLE + '。' + NOTEXT),
    ('04-漠南遂空',
     '阴山北漠：唐军大阵追亡逐北，突厥溃众散入大漠，斥候骑四合收捕，风沙低回。战场景象集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无风沙、无骑影、无飞鸟，空无一物。' + CHAR_LJ + SET_DN + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-夜袭定襄', ['李靖帅骁骑三千自马邑进屯恶阳岭',
                      '夜袭定襄破之',
                      '突厥颉利可汗不意靖猝至',
                      '唐不倾国而来靖何敢孤军至此']),
    ('02-一日数惊', ['其从一日数惊乃徙牙于碛口',
                      '靖复遣谍离其心腹',
                      '靖复遣谍离其心腹',
                      '颉利所亲康苏密以隋萧后',
                      '及炀帝之孙政道来降']),
    ('03-乘雾袭牙帐', ['靖使武邑苏定方帅二百骑为前锋',
                      '乘雾而行去牙帐七里虏乃觉之',
                      '颉利乘千里马先走',
                      '靖斩首万馀级俘男女十馀万',
                      '杀隋义成公主']),
    ('04-漠南遂空', ['颉利至不得度其大酋长皆帅众降',
                      '苏尼失惧驰追获之',
                      '俘颉利送京师苏尼失举众来降',
                      '漠南之地遂空']),
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
    print('下一步：../../verify_batch.py 定襄 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
