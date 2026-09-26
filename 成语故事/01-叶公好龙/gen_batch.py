# -*- coding: utf-8 -*-
"""叶公好龙 - 组画批量生成（2026-09-26 定标后重制版）。

规则 1：CHARACTER/DRAGON/SETTING 一致卡原样注入每一幕；
规则 3：无字底图，生成后自动调用 ../../compose_inscription.py 合成题款与印章；
规则 2：校验用 ../../check_inscription.py --crop（默认 aicloud-kimi，空回加
--max-tokens 5000，二意见 aicloud-qwen；01 幕四列题款校验需 --crop-w 700）。

用法:
    python3 gen_batch.py              # 生成全部 4 幕并自动合成题款
    python3 gen_batch.py 02           # 只处理 02（重生成底图 + 重合成）

产出：NN-幕名-底图.jpg（无字底图）→ NN-幕名.jpg（合成题款成片）
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'gen_image.py')
COMPOSE = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'compose_inscription.py')

# —— 系列常量（勿改，保证跨故事风格一致）——
STYLE = ('中国传统水墨画，宣纸质感，浓墨勾勒轮廓，淡墨渲染云雾层次，大面积留白，'
         '构图空灵，全画黑白灰为主，意境悠远')
NOTEXT = ('画面中不得出现任何文字、任何汉字、任何印章印鉴，'
          '右上角区域大面积留白，什么都不画。')

# —— 一致卡（规则 1：同一字符串注入每一幕）——
CHARACTER = '同一位叶公：身着绛红锦袍，头戴乌纱高冠，须发花白，体态丰腴，三绺短须。'
DRAGON = '同一条天龙：鹿角高耸，龙目圆睁，须髯飘动，鳞甲细密，五爪苍劲。'
SETTING = '同一座叶府：朱漆木构厅堂，雕花格窗，青瓦坡顶，庭院青石板。'
SEAL = '叶公好龙'

SCENES = [
    ('01-叶府饰龙',
     '叶府豪华厅堂之中，' + SETTING + CHARACTER +
     '他端坐太师椅上，眉开眼笑地欣赏手中雕着龙纹的玉钩；身后梁柱盘绕浮雕金龙，'
     '四壁悬挂多幅水墨龙轴，案几器皿皆饰龙纹，一派痴迷之态。'
     + STYLE + '。画面主体集中在左半幅与下半幅，右上角完全留白。' + NOTEXT),
    ('02-天龙下凡',
     '风云突变，' + DRAGON + '真龙自天而降来到叶府，' + SETTING +
     '巨大的龙头从窗户探进屋内，龙须飘动，长长的龙尾绕过厅堂摆动，'
     '云雾在屋宇间翻腾涌动。' + STYLE + '。画面主体集中在左半幅与下半幅，右上角完全留白。' + NOTEXT),
    ('03-弃而还走',
     '叶公惊见真龙魂飞魄散，' + CHARACTER +
     '他发冠歪斜，面色惨白，丢下手中画轴仓皇转身奔逃，一只鞋跑掉了也顾不上，'
     '回望的面孔满是恐惧；' + DRAGON +
     '真龙从画面左侧的雕花木窗探首下望，神情疑惑；人物与龙全部位于画面左半幅与下半幅，'
     '画面右上方为空无一物的天空留白。' + STYLE + '。' + NOTEXT),
    ('04-似龙非龙',
     '真龙怅然若失，' + DRAGON + '它盘身回首，腾云缓缓离去，一爪仍搭在叶府檐角；'
     + SETTING + '厅内' + CHARACTER +
     '他躲在屏风后探出半个脑袋偷看，怀中仍紧紧抱着一卷画着假龙的画轴。'
     + STYLE + '。画面主体集中在左半幅与下半幅，右上角完全留白。' + NOTEXT),
]

# 每幕题款（右起列序、去标点）——生成后自动合成用
INSCRIPTIONS = [
    ('01-叶府饰龙', ['叶公子高好龙', '钩以写龙', '凿以写龙', '屋室雕文以写龙']),
    ('02-天龙下凡', ['于是天龙闻而下之', '窥头于牖施尾于堂']),
    ('03-弃而还走', ['叶公见之弃而还走', '失其魂魄五色无主']),
    ('04-似龙非龙', ['是叶公非好龙也', '好夫似龙而非龙者也']),
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
    print('下一步：../../check_inscription.py --crop 0*.jpg 逐字校验'
          '（01 幕四列题款加 --crop-w 700）', flush=True)
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
