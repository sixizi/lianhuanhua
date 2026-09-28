# -*- coding: utf-8 -*-
"""论语/05-川上之叹/gen_batch.py - 由 make_ly_drivers.py 自动生成。
印章：峄山碑篆体「论语」，全书统一。题款 verbatim 见底本。"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'gen_image.py')
COMPOSE = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'compose_inscription.py')

STYLE = '中国传统连环画风格，遒劲流畅的墨线勾勒人物与场景，线条细密工整，造型生动传神，如上海人民美术出版社经典工笔重彩连环画，在白描骨架上敷以明丽典雅的中国画色彩，朱砂石青石绿赭石点染，色彩饱满而透气，不腻不脏，宣纸底色，构图饱满，叙事清晰'
NOTEXT = '画面中不得出现任何文字、任何汉字、任何印章印鉴，画面主体集中在左半幅与下半幅，右上角区域大面积留白，什么都不画。'
WHITESIDE = '全部景物集中在画面左半幅与下半幅：画面右半幅从纸顶到纸底整条竖区保持纯净的宣纸留白（包括右下角），绝不画人物、树木、山石、云烟、水纹、飞鸟，空无一物。'
KONGZI = '同一人：孔子仲尼，身材高大的长者，须发花白整齐，蓄三绺长髯，头戴儒冠，身着月白色镶边深衣大袍，腰束宽带，仪态温良恭俭，神色安详。'
ZILU = '同一人：子路仲由，孔子的弟子，身材魁梧雄壮的中年男子，短发刚髯，神情率直勇猛，身着赭红色短袍束腰，腰间佩长剑。'
YANHUI = '同一人：颜回，孔子的弟子，清瘦的青年，眉目温润谦和，身着素色（灰白）布袍，衣衫简朴洗旧。'
ZENGDIAN = '同一人：曾点曾皙，孔子的弟子，洒脱的中年男子，束发布袍，怀抱一张古瑟，神态闲雅悠然。'
ZIGONG = '同一人：子贡，孔子的弟子，俊朗的中年男子，衣着整洁，能言善辩，神态从容精明。'
RANYOU = '同一人：冉有，孔子的弟子，谦慎的中年男子，布衣束发，神情恭谨。'
ZIXIA = '同一人：子夏，孔子的弟子，清秀的青年，布衣，神色认真。'
SET_XT = '杏坛：鲁国曲阜孔坛，土筑高台，台上老杏树数株，树冠如盖，弟子们列坐听讲。'
SET_TM = '太庙：鲁国太庙，木构高堂，立柱粗大，礼器鼎俎陈列，庄严肃穆。'
SET_LOU = '陋巷：低矮土墙夹峙的小巷，巷尾简陋茅屋，屋内木案竹席，窗外一株老树。'
SET_CHUAN = '河川：宽阔的河面，流水汤汤，岸边山石嶙峋，远处青山连绵，时值岁末寒天，岸边有松柏数株。'
SET_WU = '暮春郊野：沂水河边，河水清缓，岸边舞雩台高台，柳树新绿，众人春服风雅。'
SET_CHEN = '陈国荒野：旷野之中，行旅断粮，弟子们面有饥色，荒草蔓生，远处山影苍茫。'
SET_WC = '武城：小城街市，城门低矮，街巷间百姓安居，隐隐有乐声传出。'
SET_TIAN = '田陌：农田阡陌之间，两位隐士并肩执耒耦耕，田埂土路，远处田水如镜。'
SET_LU = '车马大道：鲁国郊外官道，尘土飞扬，一辆牛车行于道中。'

SCENES = [
    ('01-逝者如斯',
     '河岸边：孔子立于河畔大石上，垂目望着滔滔流水，袖袍临风，神情深沉。全部景物集中在画面左半幅与下半幅：画面右半幅从纸顶到纸底整条竖区保持纯净的宣纸留白（包括右下角），绝不画人物、树木、山石、云烟、水纹、飞鸟，空无一物。同一人：孔子仲尼，身材高大的长者，须发花白整齐，蓄三绺长髯，头戴儒冠，身着月白色镶边深衣大袍，腰束宽带，仪态温良恭俭，神色安详。河川：宽阔的河面，流水汤汤，岸边山石嶙峋，远处青山连绵，时值岁末寒天，岸边有松柏数株。。中国传统连环画风格，遒劲流畅的墨线勾勒人物与场景，线条细密工整，造型生动传神，如上海人民美术出版社经典工笔重彩连环画，在白描骨架上敷以明丽典雅的中国画色彩，朱砂石青石绿赭石点染，色彩饱满而透气，不腻不脏，宣纸底色，构图饱满，叙事清晰。画面中不得出现任何文字、任何汉字、任何印章印鉴，画面主体集中在左半幅与下半幅，右上角区域大面积留白，什么都不画。'),
    ('02-岁寒松柏',
     '寒天山野：孔子行于山径，指点远处寒风中挺立的松柏，弟子随行仰望。全部景物集中在画面左半幅与下半幅：画面右半幅从纸顶到纸底整条竖区保持纯净的宣纸留白（包括右下角），绝不画人物、树木、山石、云烟、水纹、飞鸟，空无一物。同一人：孔子仲尼，身材高大的长者，须发花白整齐，蓄三绺长髯，头戴儒冠，身着月白色镶边深衣大袍，腰束宽带，仪态温良恭俭，神色安详。河川：宽阔的河面，流水汤汤，岸边山石嶙峋，远处青山连绵，时值岁末寒天，岸边有松柏数株。。中国传统连环画风格，遒劲流畅的墨线勾勒人物与场景，线条细密工整，造型生动传神，如上海人民美术出版社经典工笔重彩连环画，在白描骨架上敷以明丽典雅的中国画色彩，朱砂石青石绿赭石点染，色彩饱满而透气，不腻不脏，宣纸底色，构图饱满，叙事清晰。画面中不得出现任何文字、任何汉字、任何印章印鉴，画面主体集中在左半幅与下半幅，右上角区域大面积留白，什么都不画。'),
    ('03-匹夫夺志',
     '原野上：子路按剑而立，目光坚定，孔子在旁嘉许地望着他，远处军阵旌旗隐约。全部景物集中在画面左半幅与下半幅：画面右半幅从纸顶到纸底整条竖区保持纯净的宣纸留白（包括右下角），绝不画人物、树木、山石、云烟、水纹、飞鸟，空无一物。同一人：孔子仲尼，身材高大的长者，须发花白整齐，蓄三绺长髯，头戴儒冠，身着月白色镶边深衣大袍，腰束宽带，仪态温良恭俭，神色安详。同一人：子路仲由，孔子的弟子，身材魁梧雄壮的中年男子，短发刚髯，神情率直勇猛，身着赭红色短袍束腰，腰间佩长剑。。中国传统连环画风格，遒劲流畅的墨线勾勒人物与场景，线条细密工整，造型生动传神，如上海人民美术出版社经典工笔重彩连环画，在白描骨架上敷以明丽典雅的中国画色彩，朱砂石青石绿赭石点染，色彩饱满而透气，不腻不脏，宣纸底色，构图饱满，叙事清晰。画面中不得出现任何文字、任何汉字、任何印章印鉴，画面主体集中在左半幅与下半幅，右上角区域大面积留白，什么都不画。'),
]

INSCRIPTIONS = [
    ('01-逝者如斯', ['子在川上曰', '逝者如斯夫', '不舍昼夜']),
    ('02-岁寒松柏', ['岁寒然后知松柏之后凋也']),
    ('03-匹夫夺志', ['三军可夺帅也', '匹夫不可夺志也']),
]

SEAL = '论语'
SEAL_FONT = os.path.join(os.path.dirname(os.path.dirname(HERE)),
                         'fonts', 'YiShanBeiZhuanTi.ttf')
SEAL_SIZE = 46
SUPERSEDED = set()

def run():
    only = sys.argv[1:]
    ok, fail = [], []
    for name, prompt in SCENES:
        if name in SUPERSEDED and not only:
            print('SKIP ' + name + '（已被合成方案取代）', flush=True)
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
    print('下一步：../../check_inscription.py --crop NN-幕名.jpg 逐字校验（规则 2）')
    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(run())

