# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 16 却月阵（卷一百一十八 · 晋纪四十 · 义熙十三年（公元417年））批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
四幕：缘河杀略 / 却月布阵 / 白毦既举 / 断槊洞贯。
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

CHAR_LY = '同一人：刘裕，五十三岁的北府统帅，身材魁梧，短须如戟，铁甲外罩青黑色战袍，神情沉雄。'
CHAR_DW = '丁旿：健壮的北府队主，皮甲皂袍，臂力过人。'
CHAR_ZCS = '朱超石：骁勇的青年宁朔将军，银甲红氅，神情悍勇。'
CHAR_WR = '北魏骑兵：鲜卑劲骑，皮帽毡裘，弯弓纵马，成群驰突。'
SET_HN = '黄河北岸：河滩平旷，却月阵车阵弧形排列，两端抱河，白毦高竖；南岸晋军船队遥望，北岸魏骑四合如潮。'

SCENES = [
    ('01-缘河杀略',
     '黄河岸边：魏军数千骑沿岸随晋军西行驰突，南岸晋军牵百丈缆绳逆水行舟，有漂渡北岸者遭魏骑杀略。河岸与骑队位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无水波、无骑影、无飞鸟，空无一物。' + CHAR_WR + SET_HN + '。' + STYLE + '。' + NOTEXT),
    ('02-却月布阵',
     '黄河北岸滩地：丁旿率仗士七百人推车百乘布却月阵，弧形车阵两端抱河，每车置七仗士，阵后白毦高竖。刘裕在阵后督看。车阵与人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无水波、无云烟，空无一物。' + CHAR_LY + CHAR_DW + SET_HN + '。' + STYLE + '。' + NOTEXT),
    ('03-白毦既举',
     '北岸阵前：白毦既举，朱超石率二千步骑驰赴车阵，军士抬大弩百张入阵，设彭排于辕上；魏骑三万四面进围，箭如飞蝗。阵战集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无箭矢、无骑影，空无一物。' + CHAR_ZCS + CHAR_WR + SET_HN + '。' + STYLE + '。' + NOTEXT),
    ('04-断槊洞贯',
     '车阵内搏杀：晋军断槊为三四尺短槊，以大锤锤之，一槊洞贯三四人，魏兵一时奔溃死者相积。朱超石在阵中大呼督战。搏杀场面集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无血光、无兵戈、无骑影，空无一物。' + CHAR_ZCS + CHAR_WR + SET_HN + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-缘河杀略', ['魏人以数千骑缘河随裕军西行',
                      '有漂渡北岸者辄为魏人所杀略',
                      '裁登岸则走退则复来']),
    ('02-却月布阵', ['裕遣白直队主帅仗士七百人',
                      '车百乘渡北岸去水百馀步',
                      '为却月阵两端抱河',
                      '车置七仗士',
                      '魏人不解其意皆未动']),
    ('03-白毦既举', ['裕先命宁朔将军朱超石戒严',
                      '超石帅二千人驰往赴之',
                      '赍大弩百张',
                      '一车益二十人设彭排于辕上',
                      '魏人见营阵既立乃进围之']),
    ('04-断槊洞贯', ['长孙嵩帅三万骑助之四面肉薄攻营',
                      '弩不能制时超石别赍大锤乃槊千馀张',
                      '乃断槊长三四尺以锤锤之',
                      '一槊辄洞贯三四人魏兵不能当',
                      '一时奔溃死者相积']),
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
    print('下一步：../../verify_batch.py 却月 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
