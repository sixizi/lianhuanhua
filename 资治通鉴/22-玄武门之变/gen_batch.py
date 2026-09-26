# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 22 玄武门之变（卷一九一 · 唐纪七 · 武德九年（公元626年））批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
五幕：密奏变起 / 临湖觉变 / 射杀建成 / 敬德叱元吉 / 海池请见。
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

CHAR_LSM = '同一人：李世民，二十八岁的秦王，英武挺拔，浓眉朗目，束发铁盔，玄甲罩绛袍，挽弓挟箭，沉毅果决。'
CHAR_JC = '建成：太子，三十岁，白面短须，太子冠服（玄色衮衣金纹），神情惶遽。'
CHAR_YJ = '元吉：齐王，二十余岁，体壮性戾，齐王甲胄，张弓欲射。'
CHAR_YC = '尉迟敬德：黑面虬髯的猛将，玄甲皂袍，手持长矛，声若洪钟。'
CHAR_LSW = '长孙无忌：清瘦沉毅的秦府谋臣，儒服佩剑。'
CHAR_FXL = '房玄龄：秦府记室，面容清朗，头戴进贤冠，青色袍服，谋而后定。'
SET_LHD = '临湖殿前：宫道柳荫，晨光熹微，建成元吉勒马欲东归宫府。'
SET_XWM = '玄武门：宫城北门，城楼高耸，门道深邃，甲士伏兵林立。'
SET_HC = '海池：宫内水面，龙舟轻荡，老皇帝泛舟其上，波光潋滟。'

SCENES = [
    ('01-密奏变起',
     '秦王府深夜：房玄龄与长孙无忌对坐密谋，案上密奏文书半掩烛光；李世民按剑立于暗处沉思。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无烛焰、无帷幔，空无一物。' + CHAR_FXL + CHAR_LSW + CHAR_LSM + '。' + STYLE + '。' + NOTEXT),
    ('02-临湖觉变',
     '临湖殿前宫道：建成元吉并辔行至殿前，蓦然觉变，双双跋马欲东归；道旁柳荫下伏兵隐现。二骑位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无宫墙、无柳影、无伏兵，空无一物。' + CHAR_JC + CHAR_YJ + SET_LHD + '。' + STYLE + '。' + NOTEXT),
    ('03-射杀建成',
     '宫道驰射：元吉张弓再三不彀，慌乱纵马；李世民挽弓如满月，弦响箭出，建成应弦而坠。骑射场面集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无箭矢、无宫墙、无飞鸟，空无一物。' + CHAR_LSM + CHAR_YJ + CHAR_JC + SET_XWM + '。' + STYLE + '。' + NOTEXT),
    ('04-敬德叱元吉',
     '林间搏斗：李世民马逸入林坠地不起，元吉夺弓将扼，尉迟敬德跃马横矛叱之，元吉弃弓步走欲趣武德殿。搏斗场面集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无林木、无兵戈，空无一物。' + CHAR_LSM + CHAR_YJ + CHAR_YC + SET_XWM + '。' + STYLE + '。' + NOTEXT),
    ('05-海池请见',
     '海池舟上：老皇帝泛舟池上，尉迟敬德擐甲持矛立于岸畔请见，甲胄映水，舟上君臣相顾失色。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无水波、无舟影、无兵戈，空无一物。' + CHAR_YC + SET_HC + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-密奏变起', ['秦府僚属皆忧惧不知所出',
                      '存亡之机间不容发正在今日',
                      '世民召玄龄谋之玄龄曰大王功盖天地',
                      '乃与府属杜如晦共劝世民诛建成元吉']),
    ('02-临湖觉变', ['建成元吉至临湖殿觉变',
                      '即跋马东归宫府',
                      '建成曰兵备已严当与弟入参自问消息']),
    ('03-射杀建成', ['元吉张弓射世民再三不彀',
                      '世民射建成杀之',
                      '尉迟敬德将七十骑继至',
                      '左右射元吉坠马']),
    ('04-敬德叱元吉', ['世民马逸入林下',
                      '元吉遽至夺弓将扼之',
                      '敬德跃马叱之',
                      '元吉步欲趣武德殿敬德追射杀之']),
    ('05-海池请见', ['上方泛舟海池',
                      '世民使尉迟敬德入宿卫',
                      '敬德擐甲持矛直至上所',
                      '上大惊问曰今日乱者谁邪卿来此何为']),
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
    print('下一步：../../verify_batch.py 玄武门 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
