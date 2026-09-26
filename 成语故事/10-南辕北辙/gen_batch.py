# -*- coding: utf-8 -*-
"""10-南辕北辙 - 组画批量生成（定标流程，见 story-painting-series 技能）。

原文出处：《战国策·魏策四》：
今者臣来，见人于大行，方北面而持其驾，告臣曰：我欲之楚。
臣曰：君之楚，将奚为北面。曰：吾马良。臣曰：马虽良，此非楚之路也。
曰：吾用多。臣曰：用虽多，此非楚之路也。曰：吾御者善。
此数者愈善，而离楚愈远耳。

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

DRIVER = '同一位北行驭客：华服高冠，扬鞭坐在车辕上，意气扬扬。'
ASKER = '同一位褐衣行者：布衣裹腿，肩挎行囊，面带疑惑。'
ROAD = '同一条坦荡大道：黄土官道自画面下方通向北方，道旁杨柳驿亭，南面远山隐约。'
SEAL = '南辕北辙'

SCENES = [
    ('01-欲之楚',
     ROAD + DRIVER +
     '他驱车北行，车轮滚滚扬起轻尘；' + ASKER +
     '在画面左下方道旁拱手拦问。' + STYLE + '。' + NOTEXT),
    ('02-吾马良',
     ROAD + ASKER + '他指向北方连声质疑；' + DRIVER +
     '他停车扬鞭，得意地拍着身旁高头大马，夸耀马匹精良。'
     + STYLE + '。' + NOTEXT),
    ('03-吾用多',
     ROAD + DRIVER +
     '他指向车后鼓鼓的行囊盘缠，下巴扬得老高；' + ASKER +
     '在画面左侧摇头叹气，摊手再劝。' + STYLE + '。' + NOTEXT),
    ('04-离楚愈远',
     ROAD + '马车在画面左下方向北扬尘而去，渐行渐远；' + ASKER +
     '他立在道旁望着远去的车影摇头；南面远山在画面左侧隐约，'
     '与车行方向背道而驰。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-欲之楚', ['见人于大行', '方北面而持其驾', '告臣曰我欲之楚']),
    ('02-吾马良', ['君之楚将奚为北面', '曰吾马良', '马虽良此非楚之路也']),
    ('03-吾用多', ['曰吾用多', '用虽多此非楚之路也', '曰吾御者善']),
    ('04-离楚愈远', ['此数者愈善', '而离楚愈远耳']),
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
