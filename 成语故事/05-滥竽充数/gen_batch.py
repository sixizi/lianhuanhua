# -*- coding: utf-8 -*-
"""05-滥竽充数 - 组画批量生成（定标流程，见 story-painting-series 技能）。

原文出处：《韩非子·内储说上》：
齐宣王使人吹竽，必三百人。南郭处士请为王吹竽，宣王说之，廪食以数百人。
宣王死，湣王立，好一一听之，处士逃。

规则 1：一致卡注入每一幕；规则 3：无字底图 + 自动合成题款；
规则 2：校验用 ../../check_inscription.py --crop（默认 aicloud-kimi）。

用法:
    python3 gen_batch.py              # 生成全部 4 幕并自动合成题款
    python3 gen_batch.py 02           # 只处理 02（重生成底图 + 重合成）
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'gen_image.py')
COMPOSE = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'compose_inscription.py')

STYLE = ('中国传统水墨画，宣纸质感，浓墨勾勒轮廓，淡墨渲染云雾层次，大面积留白，'
         '构图空灵，全画黑白灰为主，意境悠远')
NOTEXT = ('画面中不得出现任何文字、任何汉字、任何印章印鉴，'
          '画面主体集中在左半幅与下半幅，右上角区域大面积留白，什么都不画。')

NANGUO = '同一位南郭处士：米白领袍，头戴小冠，面皮白净，怀抱一支竹竽，神情心虚。'
KING = '同一位齐宣王：绛紫锦袍，冕旒王冠，坐于高台王座，神情威严。'
COURT = '同一座齐国王庭：朱红立柱，高台帷幕，两侧编钟乐架。'
SEAL = '滥竽充数'

SCENES = [
    ('01-三百人吹竽',
     COURT + KING + '三百乐工齐奏竹竽，声势浩大，乐工在画面下半幅横向排开，'
     '竽管参差如林。' + STYLE + '。' + NOTEXT),
    ('02-处士请吹',
     NANGUO + '他拱手立于画面左侧高台之下，一脸自信地请求加入吹竽乐队；'
     + COURT + KING + '在上方含笑应允。' + STYLE + '。' + NOTEXT),
    ('03-廪食数百',
     NANGUO + '他混站在画面下半幅的乐工列中，把竹竽凑到嘴边鼓着腮帮'
     '假装吹奏，手指虚按竽眼，眼珠却四下瞟动；身边乐工人人卖力。'
     + COURT + STYLE + '。' + NOTEXT),
    ('04-处士逃',
     '新即位的齐湣王身着玄色王袍，坐在画面左侧高台上一一听乐工独奏；'
     + NANGUO + '他抱着竹竽蹑手蹑脚溜出王庭侧门，一步三回头，神色仓皇。'
     + COURT + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-三百人吹竽', ['齐宣王使人吹竽', '必三百人']),
    ('02-处士请吹', ['南郭处士请为王吹竽', '宣王说之']),
    ('03-廪食数百', ['廪食以数百人']),
    ('04-处士逃', ['宣王死愍王立', '好一一听之处士逃']),
]

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
        r = subprocess.run(cmd)
        print('    exit ' + str(r.returncode), flush=True)
        (ok if r.returncode == 0 else fail).append(name + '-合成')

    print('DONE ok=' + str(len(ok)) + ' fail=' + str(fail), flush=True)
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
