# -*- coding: utf-8 -*-
"""make_ly_drivers.py - 《论语》连环画十回批量驱动生成器。

系列：论语 · 白描敷彩连环画 | 画幅：2K | 底本：儒藏/四书/论语.txt（daizhigev20，简体白文）
印章：峄山碑篆体「论语」二字，全书统一（fonts/YiShanBeiZhuanTi.ttf）。
定标三条：人物场景一致卡逐幕注入；底图无字、题款程序合成；校验 aicloud-kimi→qwen。
题款切片：章句 verbatim（去标点），列长 4-16 字，列拆不改变原文连续性。

用法：python3 make_ly_drivers.py   # 落盘 论语/NN-回名/gen_batch.py 十份
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SERIES = '论语'

STYLE = ('中国传统连环画风格，遒劲流畅的墨线勾勒人物与场景，线条细密工整，'
         '造型生动传神，如上海人民美术出版社经典工笔重彩连环画，'
         '在白描骨架上敷以明丽典雅的中国画色彩，朱砂石青石绿赭石点染，'
         '色彩饱满而透气，不腻不脏，宣纸底色，构图饱满，叙事清晰')
NOTEXT = ('画面中不得出现任何文字、任何汉字、任何印章印鉴，'
          '画面主体集中在左半幅与下半幅，右上角区域大面积留白，'
          '什么都不画。')
WHITESIDE = ('全部景物集中在画面左半幅与下半幅：'
             '画面右半幅从纸顶到纸底整条竖区保持纯净的宣纸留白'
             '（包括右下角），绝不画人物、树木、山石、云烟、水纹、飞鸟，'
             '空无一物。')

# —— 人物卡（论语全书主卡，跨回逐字复用）——
KONGZI = ('同一人：孔子仲尼，身材高大的长者，须发花白整齐，蓄三绺长髯，'
          '头戴儒冠，身着月白色镶边深衣大袍，腰束宽带，仪态温良恭俭，神色安详。')
ZILU = ('同一人：子路仲由，孔子的弟子，身材魁梧雄壮的中年男子，短发刚髯，'
        '神情率直勇猛，身着赭红色短袍束腰，腰间佩长剑。')
YANHUI = ('同一人：颜回，孔子的弟子，清瘦的青年，眉目温润谦和，'
          '身着素色（灰白）布袍，衣衫简朴洗旧。')
ZENGDIAN = ('同一人：曾点曾皙，孔子的弟子，洒脱的中年男子，束发布袍，'
            '怀抱一张古瑟，神态闲雅悠然。')
ZIGONG = ('同一人：子贡，孔子的弟子，俊朗的中年男子，衣着整洁，'
          '能言善辩，神态从容精明。')
RANYOU = ('同一人：冉有，孔子的弟子，谦慎的中年男子，布衣束发，神情恭谨。')
ZIXIA = ('同一人：子夏，孔子的弟子，清秀的青年，布衣，神色认真。')

# —— 场景卡 ——
SET_XT = ('杏坛：鲁国曲阜孔坛，土筑高台，台上老杏树数株，'
          '树冠如盖，弟子们列坐听讲。')
SET_TM = ('太庙：鲁国太庙，木构高堂，立柱粗大，礼器鼎俎陈列，庄严肃穆。')
SET_LOU = ('陋巷：低矮土墙夹峙的小巷，巷尾简陋茅屋，屋内木案竹席，'
           '窗外一株老树。')
SET_CHUAN = ('河川：宽阔的河面，流水汤汤，岸边山石嶙峋，'
             '远处青山连绵，时值岁末寒天，岸边有松柏数株。')
SET_WU = ('暮春郊野：沂水河边，河水清缓，岸边舞雩台高台，'
          '柳树新绿，众人春服风雅。')
SET_CHEN = ('陈国荒野：旷野之中，行旅断粮，弟子们面有饥色，'
            '荒草蔓生，远处山影苍茫。')
SET_WC = ('武城：小城街市，城门低矮，街巷间百姓安居，'
          '隐隐有乐声传出。')
SET_TIAN = ('田陌：农田阡陌之间，两位隐士并肩执耒耦耕，'
            '田埂土路，远处田水如镜。')
SET_LU = ('车马大道：鲁国郊外官道，尘土飞扬，一辆牛车行于道中。')

BLANK = ''  # 预留

# STORIES[回名] = [(幕名, 提示词, [题款列...]), ...]
STORIES = {
    '01-杏坛讲学': [
        ('01-学而时习',
         '杏坛上：孔子端坐席上讲学，面前几案摆着展开的竹简，'
         '众弟子围坐听讲，一少年弟子捧简上前请教。'
         + WHITESIDE + KONGZI + SET_XT + '。' + STYLE + '。' + NOTEXT,
         ['子曰学而时习之', '不亦说乎', '有朋自远方来', '不亦乐乎']),
        ('02-人不知不愠',
         '杏坛边老杏树下：孔子抚须而立，神色温和坦然，'
         '一名弟子拱手立于侧，若有所悟。'
         + WHITESIDE + KONGZI + SET_XT + '。' + STYLE + '。' + NOTEXT,
         ['人不知而不愠', '不亦君子乎']),
        ('03-温良恭俭让',
         '杏坛前：子禽与子贡两位弟子立于一旁低声相语，'
         '远处孔子正与一位国使模样的来客拱手相见。'
         + WHITESIDE + KONGZI + ZIGONG + SET_XT + '。' + STYLE + '。' + NOTEXT,
         ['夫子温良恭俭让以得之', '夫子之求之也', '其诸异乎人之求之与']),
        ('04-三省吾身',
         '暮色中的学舍：曾子（可用泛称年轻弟子）独坐席上，'
         '面容沉静，双手拢袖垂目自省。'
         + WHITESIDE + SET_XT + '。' + STYLE + '。' + NOTEXT,
         ['曾子曰吾日三省吾身', '为人谋而不忠乎', '与朋友交而不信乎', '传不习乎']),
    ],
    '02-十五志学': [
        ('01-志学',
         '杏坛下的少年孔子：十五岁上下的少年，布衣短发，'
         '在几案前捧简夜读，神情专注。'
         + WHITESIDE + '同一人：少年时代的孔子，眉宇清朗的少年。'
         + '。' + STYLE + '。' + NOTEXT,
         ['子曰吾十有五而志于学']),
        ('02-而立',
         '三十岁的孔子：在学舍中向弟子们授业，神情沉稳自信，'
         '弟子们环立听讲。'
         + WHITESIDE + KONGZI + SET_XT + '。' + STYLE + '。' + NOTEXT,
         ['三十而立']),
        ('03-不惑知命',
         '四十岁的孔子：立于朝堂廊下，面对列国使节，神色从容明断。'
         + WHITESIDE + KONGZI + '。' + STYLE + '。' + NOTEXT,
         ['四十而不惑', '五十而知天命']),
        ('04-耳顺从心',
         '七十岁的孔子：白发老者坐于杏坛，倚杖而笑，神态安详自在，'
         '弟子们侍坐四周。'
         + WHITESIDE + KONGZI + SET_XT + '。' + STYLE + '。' + NOTEXT,
         ['六十而耳顺', '七十而从心所欲不逾矩']),
    ],
    '03-入太庙': [
        ('01-每事问',
         '太庙大堂内：孔子拱手向庙祝（司仪官）谦逊询问礼器规制，'
         '庙祝拱手回答，周围陈列鼎俎礼器。'
         + WHITESIDE + KONGZI + SET_TM + '。' + STYLE + '。' + NOTEXT,
         ['子入太庙每事问', '或曰孰谓鄹人之子知礼乎', '入太庙每事问']),
        ('02-是知礼',
         '太庙门前：孔子从容拱手而立，神色平和，'
         '身后弟子相随，闻言而笑。'
         + WHITESIDE + KONGZI + SET_TM + '。' + STYLE + '。' + NOTEXT,
         ['子闻之曰是礼也']),
        ('03-绘事后素',
         '太庙廊下：弟子子夏拱手请教，孔子抬手示意，'
         '指着廊柱上一幅未干的白色底子的彩绘。'
         + WHITESIDE + KONGZI + ZIXIA + SET_TM + '。' + STYLE + '。' + NOTEXT,
         ['子夏问曰巧笑倩兮', '美目盼兮素以为绚兮', '子曰绘事后素', '起予者商也']),
    ],
    '04-箪食瓢饮': [
        ('01-一箪食',
         '陋巷尽头茅屋内：颜回坐在竹席上，面前木案上一竹筐饭、'
         '一只瓢，神色安然自若。'
         + WHITESIDE + YANHUI + SET_LOU + '。' + STYLE + '。' + NOTEXT,
         ['子曰贤哉回也', '一箪食一瓢饮在陋巷', '人不堪其忧']),
        ('02-不改其乐',
         '同一茅屋外：颜回于门前老树下抱卷而读，面带微笑，'
         '衣衫简朴，巷中路人行色匆匆。'
         + WHITESIDE + YANHUI + SET_LOU + '。' + STYLE + '。' + NOTEXT,
         ['回也不改其乐', '贤哉回也']),
        ('03-安贫乐道',
         '陋巷：孔子拄杖来访，立在巷口望着远处读书的颜回，'
         '面露欣慰之色。'
         + WHITESIDE + KONGZI + YANHUI + SET_LOU + '。' + STYLE + '。' + NOTEXT,
         ['一箪食一瓢饮在陋巷', '人不堪其忧回也不改其乐']),
    ],
    '05-川上之叹': [
        ('01-逝者如斯',
         '河岸边：孔子立于河畔大石上，垂目望着滔滔流水，'
         '袖袍临风，神情深沉。'
         + WHITESIDE + KONGZI + SET_CHUAN + '。' + STYLE + '。' + NOTEXT,
         ['子在川上曰', '逝者如斯夫', '不舍昼夜']),
        ('02-岁寒松柏',
         '寒天山野：孔子行于山径，指点远处寒风中挺立的松柏，'
         '弟子随行仰望。'
         + WHITESIDE + KONGZI + SET_CHUAN + '。' + STYLE + '。' + NOTEXT,
         ['岁寒然后知松柏之后凋也']),
        ('03-匹夫夺志',
         '原野上：子路按剑而立，目光坚定，孔子在旁嘉许地望着他，'
         '远处军阵旌旗隐约。'
         + WHITESIDE + KONGZI + ZILU + '。' + STYLE + '。' + NOTEXT,
         ['三军可夺帅也', '匹夫不可夺志也']),
    ],
    '06-侍坐言志': [
        ('01-子路率尔',
         '学舍内：孔子环坐四弟子，子路挺身而起，拱手朗声而言，'
         '神情率直豪迈，众弟子注目。'
         + WHITESIDE + KONGZI + ZILU + '。' + STYLE + '。' + NOTEXT,
         ['子路率尔而对曰', '千乘之国摄乎大国之间', '加之以师旅因之以饥馑', '由也为之']),
        ('02-夫子哂之',
         '同一学舍：孔子听罢微微一笑，子路立于一侧摸不着头脑，'
         '其余弟子窃窃相视。'
         + WHITESIDE + KONGZI + ZILU + '。' + STYLE + '。' + NOTEXT,
         ['夫子哂之']),
        ('03-舍瑟而作',
         '同一学舍角落：曾点鼓瑟正酣，忽闻夫子垂问，'
         '铿然一声按瑟而起，瑟弦微颤。'
         + WHITESIDE + KONGZI + ZENGDIAN + '。' + STYLE + '。' + NOTEXT,
         ['鼓瑟希铿尔舍瑟而作', '对曰异乎三子者之撰']),
        ('04-沂水春风',
         '想象画面（春游之景）：暮春时节，沂水岸边，'
         '曾点与几位青年沐浴于河，登舞雩台迎风而立，咏歌而归。'
         + WHITESIDE + ZENGDIAN + SET_WU + '。' + STYLE + '。' + NOTEXT,
         ['莫春者春服既成', '浴乎沂风乎舞雩咏而归']),
        ('05-吾与点也',
         '学舍内：孔子长叹一声，满面欣然，曾点侍立，'
         '其余三弟子侍坐聆听。'
         + WHITESIDE + KONGZI + ZENGDIAN + '。' + STYLE + '。' + NOTEXT,
         ['夫子喟然叹曰', '吾与点也']),
    ],
    '07-在陈绝粮': [
        ('01-绝粮',
         '陈国旷野：行路的车马停歇，弟子们围坐荒草间，'
         '人人面有饥色，粮袋空瘪。'
         + WHITESIDE + KONGZI + SET_CHEN + '。' + STYLE + '。' + NOTEXT,
         ['在陈绝粮从者病莫能兴']),
        ('02-子路愠见',
         '旷野中：子路愤然而起，按剑（不拔）拱手质问，'
         '孔子端坐不动，神色平静。'
         + WHITESIDE + KONGZI + ZILU + SET_CHEN + '。' + STYLE + '。' + NOTEXT,
         ['子路愠见曰', '君子亦有穷乎']),
        ('03-君子固穷',
         '旷野黄昏：孔子抚琴（或垂目沉静），从容言道，'
         '弟子们闻言渐渐平复，若有所思。'
         + WHITESIDE + KONGZI + SET_CHEN + '。' + STYLE + '。' + NOTEXT,
         ['子曰君子固穷', '小人穷斯滥矣']),
    ],
    '08-弦歌武城': [
        ('01-闻弦歌',
         '武城街市：孔子乘车入城，侧耳倾听，'
         '街巷间百姓怡然，远处隐约有乐师奏乐之状。'
         + WHITESIDE + KONGZI + SET_WC + '。' + STYLE + '。' + NOTEXT,
         ['子之武城闻弦歌之声', '夫子莞尔而笑']),
        ('02-割鸡牛刀',
         '武城官署前：子游（武城宰，可用泛称邑宰）拱手迎候，'
         '孔子含笑打趣，子游神色认真对答。'
         + WHITESIDE + KONGZI + '。' + STYLE + '。' + NOTEXT,
         ['割鸡焉用牛刀']),
        ('03-前言戏之',
         '武城官署前：孔子转向随行弟子，朗声而笑，'
         '子游在旁拱手，气氛融洽。'
         + WHITESIDE + KONGZI + '。' + STYLE + '。' + NOTEXT,
         ['二三子偃之言是也', '前言戏之耳']),
    ],
    '09-问津于野': [
        ('01-长沮桀溺',
         '田陌间：两位隐士并肩执耒耦耕，子路拱手趋前问路，'
         '隐士耕作不辍，神色淡然。'
         + WHITESIDE + ZILU + SET_TIAN + '。' + STYLE + '。' + NOTEXT,
         ['长沮桀溺耦而耕', '孔子过之使子路问津焉']),
        ('02-滔滔天下',
         '田陌高处：桀溺停下耒耜，指点远方道路，子路拱手倾听，'
         '神色疑惑。'
         + WHITESIDE + ZILU + SET_TIAN + '。' + STYLE + '。' + NOTEXT,
         ['滔滔者天下皆是也', '而谁以易之']),
        ('03-鸟兽同群',
         '车马道旁：孔子下车负手而立，望着远方田园，神情怅然而坚定，'
         '子路侍立在旁回禀。'
         + WHITESIDE + KONGZI + ZILU + SET_LU + '。' + STYLE + '。' + NOTEXT,
         ['鸟兽不可与同群', '吾非斯人之徒与而谁与', '天下有道丘不与易也']),
    ],
    '10-接舆狂歌': [
        ('01-狂歌过车',
         '车马大道上：楚国狂士接舆披发散衣，边走边歌，'
         '经过孔子车前，姿态狂放不羁。'
         + WHITESIDE + KONGZI + SET_LU + '。' + STYLE + '。' + NOTEXT,
         ['楚狂接舆歌而过孔子曰', '凤兮凤兮何德之衰']),
        ('02-欲与言',
         '大道旁：孔子闻歌下车，拱手欲与接舆交谈，'
         '接舆趋步避开，头也不回。'
         + WHITESIDE + KONGZI + SET_LU + '。' + STYLE + '。' + NOTEXT,
         ['孔子下欲与之言', '趋而辟之不得与之言']),
        ('03-荷蓧丈人',
         '田头：一位担着竹制农具的老丈人立于田埂，植杖于土正俯身芸田，'
         '子路拱手拱立问询，老丈人神情淡漠。'
         + WHITESIDE + ZILU + SET_TIAN + '。' + STYLE + '。' + NOTEXT,
         ['子路从而后遇丈人', '四体不勤五谷不分', '植其杖而芸']),
    ],
}

SEAL = '论语'


def emit():
    total_scenes = 0
    for story, scenes in STORIES.items():
        d = os.path.join(HERE, SERIES, story)
        os.makedirs(d, exist_ok=True)
        lines = []
        lines.append('# -*- coding: utf-8 -*-')
        lines.append('"""%s/%s/gen_batch.py - 由 make_ly_drivers.py 自动生成。' % (SERIES, story))
        lines.append('印章：峄山碑篆体「%s」，全书统一。题款 verbatim 见底本。"""' % SEAL)
        lines.append('import os')
        lines.append('import subprocess')
        lines.append('import sys')
        lines.append('')
        lines.append('HERE = os.path.dirname(os.path.abspath(__file__))')
        lines.append('GEN = os.path.join(os.path.dirname(os.path.dirname(HERE)), \'gen_image.py\')')
        lines.append('COMPOSE = os.path.join(os.path.dirname(os.path.dirname(HERE)), \'compose_inscription.py\')')
        lines.append('')
        lines.append('STYLE = %r' % STYLE)
        lines.append('NOTEXT = %r' % NOTEXT)
        lines.append('WHITESIDE = %r' % WHITESIDE)
        for cn, cv in [('KONGZI', KONGZI), ('ZILU', ZILU), ('YANHUI', YANHUI),
                       ('ZENGDIAN', ZENGDIAN), ('ZIGONG', ZIGONG),
                       ('RANYOU', RANYOU), ('ZIXIA', ZIXIA),
                       ('SET_XT', SET_XT), ('SET_TM', SET_TM), ('SET_LOU', SET_LOU),
                       ('SET_CHUAN', SET_CHUAN), ('SET_WU', SET_WU),
                       ('SET_CHEN', SET_CHEN), ('SET_WC', SET_WC),
                       ('SET_TIAN', SET_TIAN), ('SET_LU', SET_LU)]:
            lines.append('%s = %r' % (cn, cv))
        lines.append('')
        lines.append('SCENES = [')
        for name, prompt, cols in scenes:
            lines.append('    (%r,' % name)
            lines.append('     %r),' % prompt)
        lines.append(']')
        lines.append('')
        lines.append('INSCRIPTIONS = [')
        for name, prompt, cols in scenes:
            lines.append('    (%r, %r),' % (name, cols))
        lines.append(']')
        lines.append('')
        lines.append('SEAL = %r' % SEAL)
        lines.append('SEAL_FONT = os.path.join(os.path.dirname(os.path.dirname(HERE)),')
        lines.append('                         \'fonts\', \'YiShanBeiZhuanTi.ttf\')')
        lines.append('SEAL_SIZE = 46')
        lines.append('SUPERSEDED = set()')
        lines.append('')
        # run() 与通鉴样板逐字一致
        lines.append(open(os.path.join(HERE, '资治通鉴', '01-三家分晋',
                                       'gen_batch.py'), encoding='utf-8').read()
                      .split('def run():')[1].join(['def run():', '']))
        with open(os.path.join(d, 'gen_batch.py'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
        total_scenes += len(scenes)
        print('emit', story, len(scenes), '幕')
    print('TOTAL', total_scenes, '幕')


if __name__ == '__main__':
    emit()
