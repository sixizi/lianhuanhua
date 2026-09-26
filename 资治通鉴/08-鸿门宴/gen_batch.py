# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 08 鸿门宴（卷九 · 汉纪一 · 高帝元年）批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
五幕：项伯夜告 / 谢罪鸿门 / 项庄舞剑 / 樊哙闯帐 / 间道归营。
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

CHAR_LB = '同一人：刘邦，四十六七岁，高额长颈，蓄短须，头戴皮弁，身着素色布袍，神情谦卑机警。'
CHAR_XY = '项羽：年未三旬的霸王，身高八尺，力能扛鼎，双目炯炯，虬髯浓密，顶盔贯甲，黑色大氅，不怒自威。'
CHAR_FZ = '范增：七十岁老者，须发皆白，形容枯瘦，目光如炬，深色袍服。'
CHAR_FK = '樊哙：屠狗出身的壮士，豹头环眼，满脸虬髯，披甲拥盾，声若洪钟。'
CHAR_XB = '项伯：项羽季父，长须长者，着深色长袍；项庄：年轻武士，按剑而起。'
CHAR_ZL = '张良：温文儒雅的中年谋士，面目清秀，纶巾博带。'
SET_HM = '鸿门军帐：牛皮大帐内宴席对设，樽俎罗列，火盆暖帐，帐外卫戟林立。'
SET_YEZHANG = '军营夜帐：牛皮小帐，一灯如豆，烛火摇曳。'
SET_YESHAN = '夜山小径：坡道蜿蜒，荒草掩径，远处帐火一点。'

SCENES = [
    ('01-项伯夜告',
     '夜色沛公军营小帐中：项伯与张良对坐密谈，刘邦在旁拱手相求，神情恳切。三人在画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，空无一物。' + CHAR_XB + CHAR_ZL + CHAR_LB + SET_YEZHANG + '。' + STYLE + '。' + NOTEXT),
    ('02-谢罪鸿门',
     '鸿门大帐宴席：项羽按剑坐于上席，刘邦躬身入帐长揖谢罪，姿态谦卑，张良随立于后，范增在项羽侧后目光阴沉。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，空无一物。' + CHAR_LB + CHAR_XY + CHAR_FZ + CHAR_ZL + SET_HM + '。' + STYLE + '。' + NOTEXT),
    ('03-项庄舞剑',
     '鸿门宴中：项庄拔剑起舞步步逼近刘邦席位，项伯亦拔剑对舞常以身翼蔽刘邦，刘邦强作镇定，项羽高坐饮观，范增在侧目举玉玦示意。人物集中于画面左半幅，画面右半幅自上而下保持纯宣纸留白，空无一物。' + CHAR_XB + CHAR_FZ + CHAR_LB + CHAR_XY + SET_HM + '。' + STYLE + '。' + NOTEXT),
    ('04-樊哙闯帐',
     '鸿门大帐：樊哙侧盾撞倒卫士破门而入，披帷而立怒目直视项羽，头发上指，项羽按剑而跽，帐中杯盘为之一震。樊哙在画面左侧，项羽在上席左侧，画面右半幅自上而下保持纯宣纸留白，空无一物。' + CHAR_FK + CHAR_XY + SET_HM + '。' + STYLE + '。' + NOTEXT),
    ('05-间道归营',
     '夜色骊山小道：刘邦脱身独骑疾驰，樊哙等四将持剑盾步行随后，山径崎岖夜色深沉，远处鸿门帐火光一点。骑者在画面左下，火光在远景左侧，画面右半幅自上而下保持纯宣纸留白，无月无云，空无一物。' + CHAR_LB + CHAR_FK + SET_YESHAN + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-项伯夜告', ['乃夜驰之沛公军私见张良',
                      '沛公奉卮酒为寿约为婚姻',
                      '旦日不可不蚤自来谢']),
    ('02-谢罪鸿门', ['沛公旦日从百余骑来见项羽',
                      '今者有小人之言令将军与臣有隙',
                      '项羽因留沛公与饮']),
    ('03-项庄舞剑', ['范增召项庄曰君王为人不忍',
                      '军中无以为乐请以剑舞',
                      '项庄拔剑起舞项伯亦拔剑起舞']),
    ('04-樊哙闯帐', ['樊哙侧其盾以撞卫士仆地',
                      '覆其盾于地加彘肩拔剑切而啖之',
                      '臣死且不避卮酒安足辞']),
    ('05-间道归营', ['如今人方为刀俎我方为鱼肉',
                      '沛公则置车骑脱身独骑',
                      '张良入谢奉白璧一双玉斗一双']),
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
    print('下一步：../../verify_batch.py 鸿门 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
