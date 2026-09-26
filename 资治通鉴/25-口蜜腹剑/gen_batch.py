# -*- coding: utf-8 -*-
"""资治通鉴连环画 · 25 口蜜腹剑（卷二一四至二一五 · 唐纪三十至三十一 · 天宝元年（公元742年））批量驱动。

系列：资治通鉴 · 白描敷彩连环画 | 画幅：2K | 模型：aicloud-seedream
四幕：甘言阴陷 / 勤政楼下 / 卢绚自请 / 腹有剑。
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

CHAR_LLF = '同一人：李林甫，五十九岁的奸相，面白微须，体态丰腴，头戴进贤冠，身着绛紫宰相袍，笑容可掬而目光阴鸷。'
CHAR_LX = '卢绚：风标清粹的兵部侍郎，仪表堂堂，绯袍玉带，垂鞭按辔。'
CHAR_YT = '严挺之：清介的老臣，须发花白，青色朝服，神情落寞。'
CHAR_XZ = '唐玄宗：中年天子，头戴翼善冠，赭黄常服，凭栏观乐。'
SET_QZ = '勤政楼下：宫楼高耸，帘垂乐陈，楼下驰道，百官骑从往来。'
SET_XS = '李林甫私第书房：锦帐低垂，烛影摇红，案上密札，仆役屏息。'

SCENES = [
    ('01-甘言阴陷',
     '李林甫私第书房：李林甫微笑执盏与一位文士对坐言欢，笑容温煦而眼底阴沉，案上密札半掩。二人位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无烛焰、无帐纹，空无一物。' + CHAR_LLF + SET_XS + '。' + STYLE + '。' + NOTEXT),
    ('02-勤政楼下',
     '勤政楼下：唐玄宗垂帘观乐于楼上，卢绚垂鞭按辔横过楼下，风标清粹；帘后目光遥送。楼观与骑者位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无楼影、无旗幡，空无一物。' + CHAR_XZ + CHAR_LX + SET_QZ + '。' + STYLE + '。' + NOTEXT),
    ('03-卢绚自请',
     '宰相直房：李林甫坐于案后温言相商，卢绚长揖自请外任，神情惶惑；仆从侍立。二人位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无柱无幔无器物，空无一物。' + CHAR_LLF + CHAR_LX + SET_XS + '。' + STYLE + '。' + NOTEXT),
    ('04-腹有剑',
     '朝堂一隅：李林甫独倚廊柱，笑容未敛，袖中密札隐现；廊外百官趋行背影。人物位于画面左半幅与下半幅，画面右半幅自上而下保持纯宣纸留白，无柱影、无幔帐，空无一物。' + CHAR_LLF + SET_QZ + '。' + STYLE + '。' + NOTEXT),
]

INSCRIPTIONS = [
    ('01-甘言阴陷', ['李林甫为相凡才望功业出己右',
                      '及为上所厚势位将逼己者',
                      '必百计去之',
                      '尤忌文学之士或阳与之善',
                      '啖以甘言而阴陷之']),
    ('02-勤政楼下', ['上尝陈乐于勤政楼下垂帘观之',
                      '兵部侍郎卢绚谓上已起',
                      '垂鞭按辔横过楼下',
                      '绚风标清粹上目送之',
                      '深叹其蕴藉']),
    ('03-卢绚自请', ['林甫常厚以金帛赂上左右',
                      '上举动必知之',
                      '乃召绚子弟谓曰尊君素望清崇',
                      '若惮远行则当左迁',
                      '绚惧以宾詹为请']),
    ('04-腹有剑', ['世谓李林甫口有蜜腹有剑']),
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
    print('下一步：../../verify_batch.py 口蜜 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())
