# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 19 玉壁之战（卷一百五十九 · 梁纪十五 · 大同十二年（公元546年））批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
四幕：昼夜不息 / 穿地取尔 / 缝布为幔 / 敕勒哀歌。
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

CHAR_GH = '同一人：东魏丞相高欢，五十一岁的枭雄统帅，壮硕苍髯，金甲外罩绛色大氅，神情焦躁威严。'
CHAR_WXK = '同一人：韦孝宽，三十八岁的西魏守将，清瘦坚毅，颏下短须，铁甲外罩青色战袍，神情沉静从容。'
CHAR_HLJ = '斛律金：敕勒族老将，深目虬髯，皮帽战袍，怀抱酒囊苍凉高歌。'
SET_YB = '玉壁城：黄土高原孤城，城墙因攻战残破，城外土山对峙，地道烟焰，营垒连绵；夜空下帐幕灯火。'
SET_XZ = '高欢牙帐：中军大帐，胡床毡毯，歌者苍凉，高欢倚坐和歌垂泪，诸将默然。'

SCENES = [
    ('01-昼夜不息',
     '玉壁城下：东魏大军昼夜猛攻，云梯冲车蚁附而上，韦孝宽在城头督守，守军木石俱下。城池与攻军集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无箭矢、无云烟、无旌旗，空无一物。' + CHAR_GH + CHAR_WXK + SET_YB + '。' + STYLE + '。' + NOTEXT),
    ('02-穿地取尔',
     '玉壁城攻防全景：城外东魏军起土山、掘地道，烟焰从地道口喷出；城上韦孝宽缚木接楼，长堑外积柴燃火，掘出的壕堑纵横。攻防工事集中于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无烟焰、无山影，空无一物。' + CHAR_WXK + SET_YB + '。' + STYLE + '。' + NOTEXT),
    ('03-缝布为幔',
     '玉壁城墙近景：东魏攻车撞城，韦孝宽命军士缝布为大幔悬空张之，攻车之力随幔而泄；魏军火竿烧幔，守军长钩遥割。城头人物与布幔位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无烟焰、无兵戈，空无一物。' + CHAR_WXK + SET_YB + '。' + STYLE + '。' + NOTEXT),
    ('04-敕勒哀歌',
     '高欢牙帐夜宴：斛律金苍凉高歌敕勒歌，高欢倚榻和之，老泪纵横，帐中诸将垂首默然，帐外寒风卷雪。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无灯焰、无帐纹、无烟尘，空无一物。' + CHAR_GH + CHAR_HLJ + SET_XZ + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-昼夜不息', ['东魏丞相欢攻玉壁昼夜不息',
                      '魏韦孝宽随机拒之',
                      '城中无水汲于汾欢使移汾一夕而毕']),
    ('02-穿地取尔', ['欢于城南起土山欲乘之以入',
                      '孝宽缚木接之令常高于土山以御之',
                      '虽尔缚楼至天我当穿地取尔',
                      '孝宽掘长堑邀其地道选战士屯堑上']),
    ('03-缝布为幔', ['每穿至堑战士辄擒杀之',
                      '又于堑外积柴贮火',
                      '塞柴投火以皮排吹之一鼓皆焦烂',
                      '孝宽缝布为幔随其所向张之',
                      '布既悬空车不能坏']),
    ('04-敕勒哀歌', ['东魏苦攻凡五十日',
                      '士卒战及病死者七万人共为一冢',
                      '欢智力皆困因而发疾',
                      '使斛律金作敕勒歌',
                      '欢自和之哀感流涕']),
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
    print('下一步：../../verify_batch.py 玉壁 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
