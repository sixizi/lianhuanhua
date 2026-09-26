# -*- coding: utf-8 -*-
"""fix_superline_scenes.py v2 - 5 幕超线定向修复。

v1 教训：只锁「右上四分之一」不够——长题款检查区是右半幅全高条带（y 至 1300-1682），
而模型把「左半幅与下半幅」解读为右下角可画，武士群像/尸阵全聚在右侧中下。
v2 配方（三条缺一不可）：
  1. 右半幅【从上到下整条】纯宣纸留白（明说含右下角）
  2. 右下角负状态：绝不画任何人物、尸骸、兵戈、烟尘（此前失败模式的点名否定）
  3. 构图重心锚死：一切景物只准出现在左半幅与左下角
"""
import os
import subprocess
import sys

os.chdir('/Users/qirong.liu/Library/CloudStorage/OneDrive-Personal/vibe/Hermes/imagefact')
GEN = 'gen_image.py'
COMPOSE = 'compose_inscription.py'

STYLE = ('中国传统连环画风格，遒劲流畅的墨线勾勒人物与场景，线条细密工整，'
         '造型生动传神，如上海人民美术出版社经典工笔重彩连环画，'
         '在白描骨架上敷以明丽典雅的中国画色彩，朱砂石青石绿赭石点染，'
         '色彩饱满而透气，不腻不脏，宣纸底色，构图饱满，叙事清晰')
NOTEXT = ('画面中不得出现任何文字、任何汉字、任何印章印鉴，'
          '画面主体集中在左半幅与下半幅，右上角区域大面积留白，'
          '什么都不画。')
RIGHT_BLANK = ('画面右半幅从上到下整条竖区全部是纯宣纸留白——从画面正中竖线到右边纸边，'
               '从纸顶到纸底，全部空白，包括右下角在内，绝不画任何人物、绝不画任何尸骸、'
               '绝不画任何兵戈旗帜、绝不画任何山石树木、绝不画任何烟尘云气雨丝。'
               '右半幅一眼望去只有干净的宣纸底色。')
ANCHOR = '一切景物、一切人物只准集中在画面左半幅与左下角。'

FIXES = [
    ('12-昆阳之战', '04-屋瓦皆飞',
     '溃战风雨旷野：莽兵溃败奔逃的队伍在画面左半幅，伏尸沿左下角斜铺，'
     '雷电与雨幕只出现在画面左上角，虎豹惊窜在左下角。' + ANCHOR,
     ['城中亦鼓噪而出', '中外合势震呼动天地',
      '莽兵大溃走者相腾践伏尸百馀里', '会大雷风屋瓦皆飞雨下如注',
      '虎豹皆股战士卒赴水溺死者以万数', '水为不流']),
    ('18-孝文汉化', '01-戎服执鞭',
     '洛阳郊野雨后：魏主戎服执鞭乘马立于画面左下，仪仗收拢在左侧，'
     '群臣跪伏于马前泥泞中。' + ANCHOR,
     ['魏主自发平城至洛阳霖雨不止', '帝戎服执鞭乘马而出',
      '群臣稽颡于马前', '帝曰庙算已定大军将进诸公更欲何云']),
    ('18-孝文汉化', '04-改姓元氏',
     '宗庙颁册：魏主手捧册命立于案前，鲜卑贵族依序列班垂首受命，'
     '人物全部位于画面左半幅。' + ANCHOR,
     ['北人谓土为拓后为跋', '魏之先出于黄帝以土德王故为拓跋氏',
      '宜改姓元氏', '始改拔拔氏为长孙氏', '独孤氏为刘氏']),
    ('19-玉壁之战', '02-穿地取尔',
     '玉壁城攻防：东魏军的土山与地道口集中在画面左下，烟焰从左下角地道口喷出，'
     '城楼与长堑在左侧中景。' + ANCHOR,
     ['欢于城南起土山欲乘之以入', '孝宽缚木接之令常高于土山以御之',
      '虽尔缚楼至天我当穿地取尔', '孝宽掘长堑邀其地道选战士屯堑上']),
    ('19-玉壁之战', '04-敕勒哀歌',
     '高欢牙帐夜宴：斛律金苍凉高歌，高欢倚榻和之垂泪，诸将垂首默然，'
     '帐中一盏灯只点在画面左下角。' + ANCHOR,
     ['东魏苦攻凡五十日', '士卒战及病死者七万人共为一冢',
      '欢智力皆困因而发疾', '使斛律金作敕勒歌欢自和之哀感流涕']),
]


def main():
    only = sys.argv[1:]
    fails = []
    for folder, name, hard, cols in FIXES:
        if only and not any(s in name or s in folder for s in only):
            continue
        D = os.path.join('资治通鉴', folder)
        base = os.path.join(D, name + '-底图.jpg')
        out = os.path.join(D, name + '.jpg')
        print('===', folder, name, flush=True)
        prompt = hard + RIGHT_BLANK + '。' + STYLE + '。' + NOTEXT
        r = subprocess.run([sys.executable, GEN, prompt, '-d', D, '-n', name + '-底图'])
        if r.returncode != 0:
            fails.append(folder + '/' + name + '-gen')
            continue
        cmd = [sys.executable, COMPOSE, base, '-o', out]
        for c in cols:
            cmd += ['-c', c]
        cmd += ['-s', '资治通鉴', '--seal-font', 'fonts/YiShanBeiZhuanTi.ttf',
                '--seal-size', '46']
        r2 = subprocess.run(cmd)
        if r2.returncode != 0:
            fails.append(folder + '/' + name + '-compose')
    print('SUMMARY failed=' + str(fails))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
