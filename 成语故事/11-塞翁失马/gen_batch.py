# -*- coding: utf-8 -*-
"""11-塞翁失马 - 组画批量生成（定标流程，见 story-painting-series 技能）。

原文出处：《淮南子·人间训》：
近塞上之人有善术者，马无故亡而入胡，人皆吊之。其父曰：此何遽不能为福乎。
居数月，其马将胡骏马而归，人皆贺之。其父曰：此何遽不能为祸乎。
家富良马，其子好骑，堕而折其髀，人皆吊之。其父曰：此何遽不能为福乎。
居一年，胡人大入塞，丁壮者引弦而战，死者十九，此独以跛之故，父子相保。

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

OLD = '同一位塞上老翁：灰白须发，皮裘毡帽，拄杖而立，神色安然。'
SON = '同一位塞上少年：短裘束带，好骑骏马；最后一幕跛足拄杖。'
BORDER = '同一处塞上边关：黄土长城烽燧，荒原草场，塞外远山。'
SEAL = '塞翁失马'

SCENES = [
    ('01-马亡入胡',
     BORDER + '马厩空空，一匹马的背影消失在画面左侧塞外远山方向；'
     + OLD + '他拄杖立于画面左下方安然自若；乡邻数人在旁吊慰摇头。'
     + STYLE + '。' + NOTEXT),
    ('02-将胡马归',
     BORDER + '数月后，走失的马领着一匹高大的胡地骏马归来，'
     '在画面下半幅扬蹄嘶鸣；' + OLD + '他拄杖而笑；乡邻拱手道贺。'
     + STYLE + '。' + NOTEXT),
    ('03-堕而折髀',
     BORDER + SON +
     '少年骑在画面下半幅飞奔的骏马上，缰绳脱手，正从马背跌落，'
     '摔在地上抱腿痛楚；' + OLD + '闻讯拄杖赶来，神情仍自安然。'
     + STYLE + '。' + NOTEXT),
    ('04-父子相保',
     BORDER + '一年后胡人入塞，画面左侧远处长城烽燧狼烟四起，'
     '丁壮持弓引弦奔赴战场；' + OLD + '与跛足拄杖的儿子在画面左下方相视而立，'
     '父子相保，安然无恙。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-马亡入胡', ['近塞上之人有善术者', '马无故亡而入胡', '人皆吊之']),
    ('02-将胡马归', ['其父曰此何遽不能为福乎', '居数月其马将胡骏马而归', '人皆贺之']),
    ('03-堕而折髀', ['家富良马其子好骑', '堕而折其髀', '人皆吊之']),
    ('04-父子相保', ['胡人大入塞', '丁壮者引弦而战', '死者十九',
                     '此独以跛之故父子相保']),
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
