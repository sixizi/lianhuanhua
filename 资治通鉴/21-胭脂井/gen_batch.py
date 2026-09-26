# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 21 胭脂井（卷一七七 · 隋纪一 · 开皇九年（公元589年））批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
四幕：夜济采石 / 陈主避匿 / 窥井引绳 / 斩于青溪。
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

CHAR_SSB = '同一人：陈后主叔宝，三十六岁的亡国之君，面容白皙丰腴，头戴小冠，身着绛色文袍，神情惶遽狼狈。'
CHAR_YX = '袁宪：忠直的老臣，须发斑白，朝服整齐，神情悲愤恳切。'
CHAR_XHG = '夏侯公韵：年轻的殿前舍人，青色官服，俯身以身蔽井。'
CHAR_HQH = '韩擒虎：隋军猛将，虎背熊腰，铁甲玄袍，虬髯戟张。'
CHAR_ZLH = '张丽华：陈主张贵妃，云鬓高髻，身着素淡宫装，容色艳丽而神色惊惶。'
CHAR_GY = '高颎：隋朝宰相，清瘦严正，头戴进贤冠，赭色官袍。'
SET_CS = '采石江面：夜色大雾横江，隋军千骑衔枚渡江，江雾弥漫，战船列影。'
SET_JY = '景阳殿后堂：宫室幽深，井栏石井一口，井畔花木，殿外火光隐隐。'
SET_QX = '青溪岸边：溪水潺潺，隋军刀斧手押跪犯妇，旌旗森然。'

SCENES = [
    ('01-夜济采石',
     '采石江面夜色：大雾横江，隋军将卒千骑衔枚登舟夜济，战船破雾而行，江面只闻桨声。船队集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无雾气、无江波、无船影，空无一物。' + CHAR_HQH + SET_CS + '。' + STYLE + '。' + NOTEXT),
    ('02-陈主避匿',
     '景阳殿后堂：陈主下榻欲奔，袁宪正色拦阻苦谏，夏侯公韵俯身以身体遮蔽井口，陈主与之争抢，宫人十馀环侍。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无帷幔、无器物，空无一物。' + CHAR_SSB + CHAR_YX + CHAR_XHG + SET_JY + '。' + STYLE + '。' + NOTEXT),
    ('03-窥井引绳',
     '景阳殿井畔：隋军军士俯身窥井呼喊欲下石，井中传出叫声；军士以绳引之，惊其太重，及出乃陈主与张贵妃孔贵嫔同束而上。井与人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无绳影、无器物，空无一物。' + CHAR_HQH + CHAR_SSB + CHAR_ZLH + SET_JY + '。' + STYLE + '。' + NOTEXT),
    ('04-斩于青溪',
     '青溪岸边：高颎按剑而立严词拒绝晋王令旨，刀斧手押张丽华跪于溪畔，溪水映寒光。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无兵戈、无旌旗、无水波，空无一物。' + CHAR_GY + CHAR_ZLH + SET_QX + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-夜济采石', ['韩擒虎将五百人自横江宵济采石',
                      '守者皆醉遂克之',
                      '丙寅采石戍主徐子建驰启告变']),
    ('02-陈主避匿', ['陈主遑遽将避匿',
                      '宪正色曰北兵之入必无所犯',
                      '陛下去欲安之',
                      '后阁舍人夏侯公韵以身蔽井',
                      '陈主与争久之乃得入']),
    ('03-窥井引绳', ['既而军人窥井呼之不应',
                      '欲下石乃闻叫声',
                      '以绳引之惊其太重',
                      '及出乃与张贵妃孔贵嫔同束而上',
                      '沈后居处如常']),
    ('04-斩于青溪', ['令留张丽华',
                      '昔太公蒙面以斩妲己',
                      '今岂可留丽华乃斩之于青溪',
                      '昔人云无德不报',
                      '我必有以报高公矣']),
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
    print('下一步：../../verify_batch.py 胭脂 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
