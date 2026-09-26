# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 15 击楫中流（卷八十八 · 晋纪十 · 永嘉六年（公元312年））批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
四幕：闻鸡起舞 / 言于睿 / 击楫而誓 / 淮阴起冶。
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

CHAR_ZT = '同一人：祖逖，四十六岁的豪迈志士，虎目虬髯，束发扎巾，身着赭红色战袍，腰悬长剑，气概雄烈。'
CHAR_LK = '刘琨：清俊的青年文官，束发帻巾，青色吏服，睡眼惺忪。'
CHAR_RUI = '司马睿：年轻的琅邪王，面容白皙，头戴玄冕，身着绛紫王袍，神态温吞。'
SET_SB = '司州官舍：简朴木屋，土炕卧榻，窗棂透月色，案上残灯。'
SET_JK = '建康堂庑：江南宫署，木构敞堂，倚柱垂帷，案上文卷。'
SET_JS = '大江中流：江面开阔，孤舟载部曲渡江，浪涌拍舷，晨光熹微。'
SET_HY = '淮阴营冶：江边屯所，炉火熊熊，工匠锻铁铸兵，新募壮士列队。'

SCENES = [
    ('01-闻鸡起舞',
     '司州官舍深夜：祖逖与刘琨同榻而眠，中夜鸡鸣，祖逖蹴醒刘琨，披衣而起于庭中拔剑起舞，月光满庭。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无月轮、无树影，空无一物。' + CHAR_ZT + CHAR_LK + SET_SB + '。' + STYLE + '。' + NOTEXT),
    ('02-言于睿',
     '建康堂庑：祖逖立于阶下慷慨陈词，手指南北；司马睿坐于上首倾听，案上摊布三千匹文书。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无柱无帷，空无一物。' + CHAR_ZT + CHAR_RUI + SET_JK + '。' + STYLE + '。' + NOTEXT),
    ('03-击楫而誓',
     '大江中流：孤舟破浪，祖逖立于船头，手击船楫仰天而誓，须发怒张；部曲百余家肃立舟中。人物与舟船集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无江波、无云影、无飞鸟，空无一物。' + CHAR_ZT + SET_JS + '。' + STYLE + '。' + NOTEXT),
    ('04-淮阴起冶',
     '淮阴营冶：炉火映照，工匠抡锤锻兵，兵器架上新矛成列，祖逖按剑阅看新募的二千余人列队。营冶场景集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无火光、无烟炱、无云烟，空无一物。' + CHAR_ZT + SET_HY + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-闻鸡起舞', ['范阳祖逖少有大志',
                      '与刘琨俱为司州主簿',
                      '中夜闻鸡鸣蹴琨觉曰',
                      '此非恶声也因起舞']),
    ('02-言于睿', ['逖居京口纠合骁健',
                      '晋室之乱非上无道而下怨叛也',
                      '由宗室争权自相鱼肉',
                      '遂使戎狄乘隙毒流中土',
                      '今遗民既遭残贼人思自奋']),
    ('03-击楫而誓', ['睿素无北伐之志',
                      '逖将其部曲百馀家渡江中流',
                      '击楫而誓曰',
                      '祖逖不能清中原而复济者',
                      '有如大江']),
    ('04-淮阴起冶', ['给千人廪布三千匹不给铠仗使自召募',
                      '遂屯淮阴起冶铸兵',
                      '募得二千馀人而后进']),
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
    print('下一步：../../verify_batch.py 击楫 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
