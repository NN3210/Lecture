#!/usr/bin/env python3
"""第5回「トラバース測量 I」の12図をSVG・PNG（180 dpi）で再生成する。"""
from pathlib import Path
import hashlib
import atexit
import json
import os
import shutil
import sys
import unicodedata
import warnings
from xml.sax.saxutils import escape

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / 'materials/slides/第05回_トラバース測量I/diagrams'
QA = ROOT / 'notes/session05_figures'
QA.mkdir(parents=True, exist_ok=True)
# キャッシュも変更を許可された範囲内に置く。
os.environ['MPLCONFIGDIR'] = str(QA / '.mplconfig')
os.environ['XDG_CACHE_HOME'] = str(QA / '.cache')


def cleanup_cache():
    """自分の作図キャッシュだけ、許可されたQAフォルダ内で削除する。"""
    for name in ['.mplconfig', '.cache']:
        p = QA / name
        if p.exists() and p.resolve().parent == QA.resolve():
            shutil.rmtree(p)


atexit.register(cleanup_cache)
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Polygon
from matplotlib.text import Text
from PIL import Image, ImageDraw

FONT = next((n for n in ['Noto Sans CJK JP', 'Meiryo']
             if n in {f.name for f in font_manager.fontManager.ttflist}), None)
if FONT is None:
    raise RuntimeError('Noto Sans CJK JP または Meiryo が必要です。')
NAVY, TEAL, ORANGE, GRAY = '#1f4e79', '#13877b', '#bd512b', '#526273'
plt.rcParams.update({'font.family': [FONT], 'font.size': 14,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'svg.fonttype': 'path', 'axes.unicode_minus': False,
                     'svg.hashsalt': 'session05', 'text.color': NAVY,
                     'mathtext.fontset': 'dejavusans'})
warnings.filterwarnings('error', message=r'Glyph .* missing from font')
CHECKS, ANGLES = [], []
TITLES = dict(zip(
    ['traverse_types', 'station_selection', 'interior_angle_sum',
     'direction_angle_propagation', 'deflection_angle', 'traverse_example',
     'latitude_departure', 'closure_preview', 'inverse_quadrant4',
     'ts_coordinate_mode', 'exercise_traverse', 'angle_error_flow'],
    ['トラバースの3種類', '測点の選び方', '内角の和', '方向角の伝播',
     '偏角の符号', '4点閉合トラバースの例題', '緯距と経距', '閉合差の予告',
     '逆計算と4象限', 'TSの座標表示', '5点トラバースの演習', '測角誤差の調整']))
# READMEの表の値を、そのまま保持する。配列は測量順の (X, Y)。
EXAMPLE = np.array([[1000, 1000], [1055.410, 1106.441],
                    [1136.126, 1056.341], [1089.477, 949.027]])
END = np.array([1000.001, 1000.000])
DIST = ['120.000', '95.000', '117.015', '102.977']
BEARINGS = ['62°30′00″', '328°10′20″', '246°30′20″', '150°19′50″']
INTERIOR = ['92°10′10″', '85°40′20″', '98°20′00″', '83°49′30″']
EXERCISE = np.array([[0, 0], [-36.4, 76.8], [28.4, 165.7],
                     [111.3, 117.4], [123.0, 33.3]])
OBS = ['100°12′12″', '118°35′52″', '95°48′32″', '128°10′42″', '97°13′42″']


def canvas(h=3.4):
    """第3回と同じ、縦横比を固定した12インチ幅の作図面。"""
    fig, ax = plt.subplots(figsize=(12, h))
    fig.subplots_adjust(left=.02, right=.98, bottom=.04, top=.96)
    ax.set(xlim=(0, 12), ylim=(0, h), aspect='equal')
    ax.axis('off')
    return fig, ax


def text(ax, x, y, s, fs=13, color=NAVY, ha='left', va='center', **kw):
    """投影時の可読性を保つ共通文字設定。"""
    return ax.text(x, y, s, fontsize=fs, color=color, ha=ha, va=va,
                   linespacing=1.5, **kw)


def box(ax, x, y, w, h, s, color=NAVY, fs=14):
    """薄い同色の塗りと角丸の説明箱。"""
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle='round,pad=0.04,rounding_size=0.1',
                 lw=1.5, edgecolor=color, facecolor='white'))
    text(ax, x+w/2, y+h/2, s, fs, color, 'center')


def arrow(ax, p, q, color=NAVY, lw=2, ls='-', shrink=3):
    """始点から終点へ向かう矢印。"""
    ax.annotate('', q, p, arrowprops={'arrowstyle': '-|>', 'lw': lw,
                'color': color, 'linestyle': ls, 'shrinkA': shrink,
                'shrinkB': shrink}, zorder=3)


def bearing(v):
    """画面上の (東, 北) ベクトルを北から右回りの方向角に変える。"""
    return np.degrees(np.arctan2(v[0], v[1])) % 360


def unit(t):
    """北を0度として (東, 北) の単位ベクトルを返す。"""
    return np.array([np.sin(np.deg2rad(t)), np.cos(np.deg2rad(t))])


def arc(ax, center, radius, start, sweep, color=TEAL, head=True, lw=1.8):
    """北基準の弧。正の掃引角は右回り、負なら左回り。"""
    c = np.asarray(center)
    t = np.deg2rad(np.linspace(start, start+sweep, max(60, int(abs(sweep)*2))))
    p = c + radius*np.column_stack([np.sin(t), np.cos(t)])
    ax.plot(p[:, 0], p[:, 1], color=color, lw=lw, zorder=2)
    if head:
        arrow(ax, p[-min(12, len(p)-1)], p[-1], color, lw, shrink=0)
    # 弧の両端が指定した方位の半直線上にあることを検査。
    assert np.allclose((p[0]-c)/radius, unit(start))
    assert np.allclose((p[-1]-c)/radius, unit(start+sweep))
    return c + radius*unit(start+sweep/2)


def inner(ax, pts, i, r=.24, head=False):
    """左回り多角形の後視から前視まで、実際の2辺の間に内角を描く。"""
    p = pts[i]
    start = bearing(pts[i-1]-p)
    sweep = (bearing(pts[(i+1) % len(pts)]-p)-start) % 360
    assert 0 < sweep < 180, 'この教材では凸多角形を使用する。'
    ANGLES.append({'頂点': i, '開始方向角': float(start), '内角': float(sweep)})
    return arc(ax, p, r, start, sweep, head=head)


def point(ax, p, label='', known=False, offset=(.12, .12)):
    """既知点は二重丸、新点は白丸。"""
    ax.plot(*p, 'o', ms=10 if known else 5, mfc='white', mec=NAVY, mew=1.5, zorder=5)
    if known:
        ax.plot(*p, 'o', ms=4, mfc='white', mec=NAVY, mew=1.2, zorder=6)
    if label:
        text(ax, p[0]+offset[0], p[1]+offset[1], label, 14)


def route(ax, pts, closed=True):
    """測線を指定された巡回順に描く。"""
    for i in range(len(pts) if closed else len(pts)-1):
        arrow(ax, pts[i], pts[(i+1) % len(pts)])


def leader(ax, p, xy, s, color=GRAY, ha='left', fs=12):
    """図形から離した文字を細い引出線で対応づける。"""
    ax.annotate(s, xy=p, xytext=xy, ha=ha, va='center', fontsize=fs,
                color=color, linespacing=1.5,
                arrowprops={'arrowstyle': '-', 'color': color, 'lw': .8,
                            'shrinkA': 5, 'shrinkB': 4})


def save(fig, name):
    """文字サイズ・画面内配置・解像度・白余白を検査して保存する。"""
    fig.canvas.draw()
    renderer, bounds = fig.canvas.get_renderer(), fig.bbox
    labels = []
    for label in fig.findobj(Text):
        if not label.get_visible() or not label.get_text():
            continue
        bb = label.get_window_extent(renderer)
        if not (bb.width and bb.height):
            continue
        if bb.x0 < 0 or bb.y0 < 0 or bb.x1 > bounds.x1 or bb.y1 > bounds.y1:
            raise RuntimeError(f'{name}: 画面外の文字: {label.get_text()}')
        if not 12 <= label.get_fontsize() <= 16:
            raise RuntimeError(f'{name}: 文字サイズ範囲外: {label.get_text()}')
        labels.append(label)
    # 文字同士の交差は目視確認の補助情報として残す（数式も1つの文字箱）。
    overlaps = []
    for i, a in enumerate(labels):
        ba = Text.get_window_extent(a, renderer)
        for b in labels[i+1:]:
            bb = Text.get_window_extent(b, renderer)
            if min(ba.x1, bb.x1)-max(ba.x0, bb.x0) > 1 and min(ba.y1, bb.y1)-max(ba.y0, bb.y0) > 1:
                overlaps.append([a.get_text(), b.get_text()])
    svg, png = FIG / f'{name}.svg', FIG / f'{name}.png'
    fig.savefig(svg, facecolor='white', metadata={'Date': None})
    content = svg.read_text(encoding='utf-8')
    pos = content.index('>', content.index('<svg'))
    content = content[:pos] + f' role="img" aria-labelledby="{name}-title {name}-desc"' + content[pos:]
    pos = content.index('>', content.index('<svg'))+1
    content = content[:pos] + f'\n<title id="{name}-title">{escape(TITLES[name])}</title>\n<desc id="{name}-desc">測量学の講義用概念図。座標はXが北、Yが東、方向角は北から右回り。</desc>' + content[pos:]
    svg.write_text('\n'.join(line.rstrip() for line in content.splitlines())+'\n', encoding='utf-8')
    fig.savefig(png, dpi=180, facecolor='white')
    with Image.open(png) as im:
        im.load()
        expected = tuple(round(v*180) for v in fig.get_size_inches())
        assert im.size == expected
        assert abs(im.info['dpi'][0]-180) < .02
        pixels = np.asarray(im.convert('RGB'))
        assert all(np.all(e == 255) for e in [pixels[:3], pixels[-3:], pixels[:, :3], pixels[:, -3:]])
        CHECKS.append({'図': name, '題名': TITLES[name], '幅px': im.width,
                       '高さpx': im.height, 'サイズinch': fig.get_size_inches().tolist(),
                       'dpi': list(im.info['dpi']), 'フォント': FONT,
                       'SVGあり': svg.is_file(), 'PNGあり': png.is_file(),
                       '文字サイズ12〜16pt': True, '文字の画面内配置': True,
                       '四辺の余白': True, '文字箱の交差候補': overlaps,
                       'PNG_SHA256': hashlib.sha256(png.read_bytes()).hexdigest()})
    plt.close(fig)


def traverse_types():
    """閉合・結合・開放で、点検に使える既知条件を比較する。"""
    fig, ax = canvas(5.2)
    for x, s in [(2, '閉合トラバース'), (6, '結合トラバース'), (10, '開放トラバース')]:
        text(ax, x, 4.8, s, 16, ha='center')
    for x in [4, 8]:
        ax.plot([x, x], [.5, 4.55], color=GRAY, alpha=.2)
    p = np.array([[1, 1.5], [2.8, 1.35], [3.35, 2.9], [2.05, 3.9], [.65, 3.05]])
    route(ax, p)
    for i in range(5):
        inner(ax, p, i)
        point(ax, p[i], 'ABCDE'[i], i == 0, [(-.3, -.24), (.12, -.24), (.12, .1), (0, .25), (-.3, .1)][i])
    p = np.array([[4.4, 1.6], [5.05, 2.3], [5.7, 1.95], [6.25, 3.05], [6.9, 2.65], [7.45, 3.45]])
    route(ax, p, False)
    for i in range(6):
        point(ax, p[i], 'ABCDEF'[i], i in [0, 5], (-.08, -.28))
    for p0, p1, lab in [(p[0], [4.4, 3.35], 'A′'), (p[-1], [6.7, 4.05], 'F′')]:
        arrow(ax, p0, p1, GRAY, 1.2, '--')
        point(ax, p1, lab, True, (-.12, .25))
    p = np.array([[8.5, 1.55], [9.3, 2.35], [10.25, 2.05], [11.25, 3.35]])
    route(ax, p, False)
    for i in range(4):
        point(ax, p[i], 'ABCD'[i], i == 0, (-.05, -.28))
    text(ax, 11.45, 3.65, '？', 16, ORANGE)
    for x, s in [(2, '内角の和と座標の戻りで点検'), (6, '終点の方向角と座標で点検'), (10, '点検できない')]:
        text(ax, x, .55, s, 12, ha='center')
    save(fig, 'traverse_types')


def station_selection():
    """視通・辺長・鋭角の違いが見える選点例。"""
    fig, ax = canvas()
    text(ax, .4, 3.05, '良い選点', 16)
    text(ax, 6.1, 3.05, '避ける選点', 16)
    p = np.array([[1.0, .65], [2.6, .6], [3.35, 1.45], [2.65, 2.4], [1.05, 2.25]])
    for i in range(5):
        q = p[[i, (i+1) % 5]]
        ax.plot(q[:, 0], q[:, 1], color=TEAL, alpha=.15, lw=12, solid_capstyle='round')
        ax.plot(q[:, 0], q[:, 1], color=NAVY, lw=1.5)
        ax.plot(*p[i], marker='+', ms=12, mew=2, color=NAVY)
    text(ax, 3.65, 1.85, '視通あり', 13, TEAL)
    text(ax, 3.65, 1.15, '辺長をそろえる\n角を偏らせない', 12)
    # 右端の鋭角は実際に約25度。左下の2点間だけ極端に短くする。
    q = np.array([[6.55, .8], [6.8, .8], [9.25, 1.55], [6.55, 2.0]])
    ax.add_patch(Polygon(q, closed=True, fill=False, edgecolor=NAVY, lw=1.6))
    for p0 in q:
        ax.plot(*p0, '+', color=NAVY, ms=10, mew=1.5)
    a = inner(ax, q, 2, .47)
    leader(ax, a, (9.55, 2.25), '鋭角：約25°\n位置の誤差が大きい', ORANGE)
    leader(ax, (6.67, .8), (6.1, .22), '短辺：求心誤差が角に効く', ORANGE)
    ax.add_patch(Polygon([[7.65, 1.55], [8.15, 1.55], [8.15, 2.2], [7.65, 2.2]], facecolor=GRAY, alpha=.7))
    leader(ax, (7.9, 1.9), (8.15, 2.75), '障害物：視通なし', GRAY)
    save(fig, 'station_selection')


def interior_angle_sum():
    """五角形を3個の三角形に分割する。"""
    fig, ax = canvas()
    p = np.array([[.65, .6], [3.2, .5], [4.35, 1.9], [2.7, 2.9], [.7, 2.5]])
    ax.add_patch(Polygon(p, closed=True, fill=False, edgecolor=NAVY, lw=2))
    for j in [2, 3]:
        ax.plot(p[[0, j], 0], p[[0, j], 1], '--', color=GRAY, lw=1.3)
    for j in [1, 2, 3]:
        c = p[[0, j, j+1]].mean(axis=0)
        text(ax, *c, '180°', 14, ha='center')
    box(ax, 5.35, 1.7, 6, 1.15, 'n 角形 = (n − 2) 個の三角形\n内角の和 = (n − 2) × 180°', fs=15)
    for j, (n, s) in enumerate([(3, 180), (4, 360), (5, 540), (6, 720)]):
        x = 5.7+j*1.55
        text(ax, x, 1.1, f'n = {n}', 13, ha='center')
        text(ax, x, .58, f'{s}°', 14, TEAL, 'center')
    save(fig, 'interior_angle_sum')


def direction_angle_propagation():
    """後視から前視への交角と、北からの長い方向角を区別する。"""
    fig, ax = canvas(5.2)
    b = np.array([4.0, 2.1])
    a = b-3.25*unit(62.5)
    c = b+2.8*unit(328+10/60)
    arrow(ax, a, b)
    arrow(ax, b, c)
    # 後視は同じ測線上。往路と区別できるよう中間区間に破線矢印を重ねる。
    arrow(ax, b, b+1.45*unit(242.5), GRAY, 1.4, '--')
    arrow(ax, b, b+[0, 2.3], GRAY, 1)
    arrow(ax, a, a+[0, 1.85], GRAY, 1)
    text(ax, 4.15, 4.5, 'X（北）', 12, GRAY)
    text(ax, a[0]-.15, a[1]+2.03, 'X（北）', 12, GRAY)
    arc(ax, a, .65, 0, 62.5, NAVY)
    arc(ax, b, .7, 242.5, 85+40/60, TEAL, lw=2.8)
    arc(ax, b, 1.45, 0, 328+10/60, ORANGE)
    for p, name, offset in [(a, 'A', (-.4, .05)), (b, 'B', (.17, -.17)), (c, 'C', (.15, .1))]:
        point(ax, p, name, offset=offset)
    text(ax, .35, .23, '$T_{AB}$ = 62°30′', 13)
    leader(ax, b+.7*unit(285), (.4, 3.35), '$β_B$ = 85°40′', TEAL, fs=13)
    text(ax, 4.9, .45, '$T_{BC}$ = 328°10′', 13, ORANGE)
    leader(ax, b+1.15*unit(242.5), (1.6, 1.35), '後視 B → A\n242°30′', GRAY, fs=12)
    text(ax, .35, 4.75, '前視 B → C', 13)
    box(ax, 6.6, 2.5, 5.0, 1.65,
        '$T_{BC}$ = $T_{AB}$ + 180° + $β_B$ − 360°\n= $T_{AB}$ + $β_B$ ± 180°\n交角は後視 → 前視を右回り', fs=13)
    text(ax, 6.75, 1.65, '方向角は北から右回り\n0°以上 360°未満にそろえる', 13, ORANGE)
    text(ax, 6.75, .7, 'この図の角度は分単位で表示', 12, GRAY)
    save(fig, 'direction_angle_propagation')


def deflection_angle():
    """前の測線の延長線から測る右偏・左偏。"""
    fig, ax = canvas()
    for cx, turn, color, title in [(2.5, 55, ORANGE, '右偏（+）'), (9, -55, TEAL, '左偏（−）')]:
        b = np.array([cx, 1.25]); a = b+[0, -.7]; c = b+1.7*unit(turn)
        text(ax, cx-1.8, 3.0, title, 15)
        arrow(ax, a, b); arrow(ax, b, c)
        arrow(ax, b, b+[0, 1.55], GRAY, 1.3, '--')
        arc(ax, b, .65, 0, turn, color)
        text(ax, cx+(.9 if turn > 0 else -1.5), 2.45, 'δ = +' if turn > 0 else 'δ = −', 14, color)
        for p, lab in [(a, 'A'), (b, 'B'), (c, 'C')]:
            point(ax, p, lab, offset=(-.28, -.08))
        text(ax, cx+.12, 2.83, '延長線', 12, GRAY)
    text(ax, 6, .18, 'δ = β − 180°　　右に折れると正、左に折れると負', 14, ha='center')
    save(fig, 'deflection_angle')


def traverse_example():
    """表の座標を等縮尺で配置し、辺・内角に数値を添える。"""
    fig, ax = canvas(5.3)
    scale = .0185
    origin = np.array([2.1, 1.45])
    p = origin+(EXAMPLE[:, ::-1]-[950, 1000])*scale
    # X軸はデータから離して置く。Y軸と両軸の目盛は共通の等縮尺。
    base = np.array([.8, origin[1]-50*scale])
    arrow(ax, base, [6.5, base[1]], GRAY, 1)
    arrow(ax, base, base+[0, 4.4], GRAY, 1)
    for value in [950, 1000, 1050, 1100, 1150]:
        x = origin[0]+(value-950)*scale
        y = origin[1]+(value-1000)*scale
        ax.plot([x, x], [base[1]-.05, base[1]+.05], color=GRAY, lw=1)
        ax.plot([base[0]-.05, base[0]+.05], [y, y], color=GRAY, lw=1)
        text(ax, x, base[1]-.22, str(value), 12, GRAY, 'center')
        text(ax, base[0]-.15, y, str(value), 12, GRAY, 'right')
    text(ax, 6.65, .52, 'Y（東）m', 12, GRAY)
    text(ax, .3, 5.05, 'X（北）m', 12, GRAY)
    route(ax, p)
    angle_xy = [(3.65, 2.15), (4.0, 2.65), (3.65, 3.37), (2.95, 2.88)]
    point_off = [(-.12, -.28), (.17, -.08), (.1, .23), (-.25, -.2)]
    for i in range(4):
        a = inner(ax, p, i, .26)
        arrow(ax, p[i], p[i]+[0, .53], GRAY, .9)
        point(ax, p[i], 'ABCD'[i], offset=point_off[i])
        leader(ax, a, angle_xy[i], INTERIOR[i], TEAL, 'center')
    labels = [(4.65, 1.25), (5.4, 3.55), (3.25, 4.5), (1.7, 1.7)]
    for i, xy in enumerate(labels):
        mid = (p[i]+p[(i+1) % 4])/2
        leader(ax, mid, xy, f'$T_{{{"ABCD"[i]}{"BCDA"[i]}}}$ = {BEARINGS[i]}\n{DIST[i]} m', NAVY, 'center')
    box(ax, 7.35, 3.55, 4.25, 1.05, '左回り → 内角は右回り交角\n一周して $T_{AB}$ に戻る', fs=13)
    text(ax, 7.55, 2.55, 'A → B → C → D → A', 14)
    text(ax, 7.55, 1.72, '緑の弧：調整後の内角\n灰色の短線：各点の座標北', 12, GRAY)
    text(ax, 7.55, .85, '座標・辺長は仕様表の値\n閉合差は図では判別できない大きさ', 12, GRAY)
    save(fig, 'traverse_example')


def latitude_departure():
    """縦成分ΔX、横成分ΔYと、象限別の符号を示す。"""
    fig, ax = canvas(5.2)
    a = np.array([2.6, 1.05]); b = a+4.6*unit(62.5); foot = np.array([a[0], b[1]])
    arrow(ax, a, a+[0, 3.35], GRAY, 1)
    text(ax, 2.75, 4.45, 'X（北）', 13, GRAY)
    arrow(ax, a, b)
    arrow(ax, a, foot, TEAL)
    arrow(ax, foot, b, ORANGE)
    ax.plot([foot[0]+.18, foot[0]+.18, foot[0]], [foot[1], foot[1]-.18, foot[1]-.18], color=GRAY, lw=1)
    arc(ax, a, .75, 0, 62.5, ORANGE)
    text(ax, 3.25, 2.05, '$T$', 15, ORANGE)
    text(ax, 4.7, 1.95, '$S$', 16)
    text(ax, 2.2, 2.15, '緯距\nΔX = S cos T', 14, TEAL, 'right')
    text(ax, 4.65, 3.65, '経距 ΔY = S sin T', 14, ORANGE, 'center')
    point(ax, a, 'A', offset=(-.28, -.22)); point(ax, b, 'B', offset=(.13, .05))
    text(ax, .65, .4, '座標の増分 = 距離を北・東の成分に分けたもの', 13)
    ax.plot([7.35, 7.35], [.5, 4.6], color=GRAY, alpha=.2)
    o = np.array([9.65, 2.55])
    arrow(ax, o+[-1.9, 0], o+[1.9, 0], GRAY, 1)
    arrow(ax, o+[0, -1.65], o+[0, 1.65], GRAY, 1)
    text(ax, 9.8, 4.4, 'X（北）', 12, GRAY)
    text(ax, 11.4, 2.25, 'Y（東）', 12, GRAY)
    for dx, dy, s in [(1, .9, '北東 (+,+)\n0〜90°'), (1, -.9, '南東 (−,+)\n90〜180°'),
                       (-1, -.9, '南西 (−,−)\n180〜270°'), (-1, .9, '北西 (+,−)\n270〜360°')]:
        text(ax, o[0]+dx, o[1]+dy, s, 12, ha='center')
    text(ax, 9.65, .45, '符号の順序は (ΔX, ΔY)', 12, GRAY, 'center')
    save(fig, 'latitude_departure')


def closure_preview():
    """表の増分を積み重ね、戻りと微小な閉合差を示す。"""
    fig, ax = canvas()
    p = np.vstack([EXAMPLE, END])[:, ::-1]
    p = (p-[949.027, 1000])*.016+[1.05, .55]
    for i in range(4):
        corner = np.array([p[i, 0], p[i+1, 1]])
        arrow(ax, p[i], corner, TEAL, 1.4)
        arrow(ax, corner, p[i+1], ORANGE, 1.4)
        arrow(ax, p[i], p[i+1], NAVY, 1.7)
        point(ax, p[i], 'ABCD'[i], offset=[(-.25, -.24), (.13, -.04), (.1, .22), (-.3, .05)][i])
    text(ax, 4.0, 2.65, '縦：ΔX', 13, TEAL)
    text(ax, 4.0, 2.15, '横：ΔY', 13, ORANGE)
    text(ax, 4.0, 1.55, '出発点へ\nほぼ戻る', 12)
    text(ax, 3.3, .12, '閉合差は縮尺上では見えない', 12, GRAY)
    box(ax, 6.0, .65, 5.55, 2.1, 'ΣΔX = +0.001 m\nΣΔY = 0.000 m（例題）\n閉じるはず → 残りが閉合差\n許容と配分は第6回（コンパス法則）', fs=14)
    save(fig, 'closure_preview')


def inverse_quadrant4():
    """同じ原点から4方向へ、北起算の長い弧も省略せずに描く。"""
    fig, ax = canvas(5.3)
    o = np.array([6, 2.9])
    arrow(ax, [3.4, o[1]], [8.65, o[1]], GRAY, 1)
    arrow(ax, [6, .75], [6, 4.85], GRAY, 1)
    text(ax, 6.12, 4.95, 'X（北）', 12, GRAY)
    text(ax, 8.7, 2.9, 'Y（東）', 12, GRAY)
    data = [(300, 400, '53°07′48″', '+', '補正なし', .38),
            (-300, 400, '126°52′12″', '−', '+180°', .64),
            (-300, -400, '233°07′48″', '+', '+180°', .9),
            (300, -400, '306°52′12″', '−', '+360°', 1.16)]
    for i, (dx, dy, val, sign, corr, r) in enumerate(data):
        p = o+np.array([dy, dx])*.0045
        arrow(ax, o, p)
        point(ax, p)
        arc(ax, o, r, 0, bearing(p-o), ORANGE, lw=1.5)
        right = dy > 0
        x = 8.3 if right else 3.7
        y = 4.3 if dx > 0 else 1.75
        ha = 'left' if right else 'right'
        text(ax, x, y, f'B{i+1} ({dx:+d}, {dy:+d})\nT = {val}', 13, NAVY, ha)
        text(ax, x, y-.72, f'arctan = {sign}53°07′48″\n{corr}', 12, ORANGE, ha)
        # 引出線は端点の外側から出し、方向角の弧とは交差させない。
        leader(ax, p, (x, y-.05), '', GRAY, ha)
    point(ax, o)
    text(ax, 5.4, 3.1, 'A', 13, ha='right')
    text(ax, 6, .5, '距離はいずれも500 m　／　橙色の弧：北から右回りの方向角', 12, ha='center')
    text(ax, 6, .12, '電卓が返す角は ±53°07′48″ だけ。符号を見て象限で補正する', 13, ha='center')
    save(fig, 'inverse_quadrant4')


def ts_coordinate_mode():
    """器械点・後視の入力から座標表示までを製品に依存せず示す。"""
    fig, ax = canvas(5.3)
    ax.add_patch(FancyBboxPatch((.35, 1.05), 3.2, 3.75,
                 boxstyle='round,pad=0.04,rounding_size=0.12',
                 facecolor=GRAY, edgecolor=NAVY, lw=2.5))
    text(ax, .65, 4.43, '座標測定', 16, 'white')
    rows = ['器械点 X0, Y0', '後視　方向角 T0', 'HA（方向角）T', 'SD（斜距離）', 'VA（鉛直角）', '→ X, Y, Z']
    # 指定日本語フォントを保ち、全角2セル・半角1セルの固定ピッチにする。
    for i, s in enumerate(rows):
        x = .65
        for ch in s:
            cells = 2 if unicodedata.east_asian_width(ch) in 'WFA' else 1
            text(ax, x, 3.88-i*.45, ch, 13, 'white')
            x += .15*cells
    text(ax, .45, .55, '表示項目を簡略化した概念図', 12, GRAY)
    boxes = [(3.95, 3.85, 4.65, 1.1,
              '入力：器械点 (X0, Y0, Z0)\n後視点の方向角 T0\nまたは後視点の座標 → 逆計算'),
             (3.95, 2.65, 4.65, .85,
              '観測：水平角 → 方向角 T\n鉛直角・斜距離 → 水平距離 S'),
             (3.95, 1.45, 4.65, .85,
              '計算：X = X0 + S cos T\nY = Y0 + S sin T'),
             (3.95, .45, 4.65, .65, '表示：N（= X）、E（= Y）、Z')]
    for i, (x, y, w, h, s) in enumerate(boxes):
        if i:
            prev = boxes[i-1]
            arrow(ax, [x+w/2, prev[1]-.04], [x+w/2, y+h+.04], GRAY, 1.6)
        box(ax, x, y, w, h, s, fs=12)
    text(ax, 9.05, 3.45, '画面の座標は、\n入力した器械点と\n後視で決まる', 13, ORANGE)
    text(ax, 9.05, 1.8, '別の既知点を\n観測して点検', 13, ORANGE)
    save(fig, 'ts_coordinate_mode')


def exercise_traverse():
    """演習は観測値だけ示し、未知方向角・緯距経距を表示しない。"""
    fig, ax = canvas()
    p = EXERCISE[:, ::-1]*.014+np.array([4.6, 1.05])
    route(ax, p)
    arrow(ax, p[0], p[0]+[0, 1.3], GRAY, 1)
    text(ax, 4.4, 2.5, 'X（北）', 12, GRAY, 'right')
    angle_pos = [(3.95, 1.05), (7.05, .33), (8.2, 1.38), (7.6, 2.8), (3.85, 2.9)]
    angle_ha = ['right', 'left', 'left', 'left', 'right']
    offsets = [(-.2, -.25), (-.05, -.26), (.1, .15), (.07, .25), (-.15, .23)]
    for i in range(5):
        v = inner(ax, p, i, .2)
        point(ax, p[i], 'ABCDE'[i], offset=offsets[i])
        leader(ax, v, angle_pos[i], f'{"ABCDE"[i]}　{OBS[i]}', TEAL, angle_ha[i])
    lengths = ['85.000', '110.000', '96.000', '84.894', '127.412']
    length_pos = [(4.9, .28), (7.7, .85), (7.75, 2.2), (5.6, 3.15), (3.5, 1.8)]
    for i in range(5):
        leader(ax, (p[i]+p[(i+1) % 5])/2, length_pos[i], lengths[i]+' m', NAVY, 'center')
    text(ax, .3, .45, '$T_{AB}$ = 115°20′30″（既知）', 13)
    text(ax, 9.55, 2.7, '演習：5点閉合', 14)
    text(ax, 9.55, 1.95, '緑の値は\n観測した内角', 12, TEAL)
    text(ax, 9.55, 1.1, 'A → B → C\n→ D → E → A', 12)
    save(fig, 'exercise_traverse')


def angle_error_flow():
    """許容判定と、許容内の等配分・許容外の再測を分岐する。"""
    fig, ax = canvas()
    xs = [.15, 3.15, 6.15, 9.15]
    labels = ['観測した内角の和\n360°00′40″',
              '理論値\n(n − 2) × 180° = 360°',
              '測角誤差 ε = +40″\nε ≤ 許容 σ√n',
              '等配分\n−40″/4 = −10″\nを各角に']
    for i, (x, s) in enumerate(zip(xs, labels)):
        if i:
            arrow(ax, [xs[i-1]+2.65, 2.25], [x-.05, 2.25], GRAY, 1.5)
        box(ax, x, 1.65, 2.6, 1.2, s, fs=12)
    arrow(ax, [7.45, 1.55], [7.45, .75], ORANGE, 1.6)
    text(ax, 7.45, .43, '超えたら再測', 13, ORANGE, 'center')
    text(ax, 10.5, .9, '調整角の和\n= 360°00′00″ を確認', 12, TEAL, 'center')
    text(ax, 1, .65, '許容内であることを確認してから調整する', 13)
    save(fig, 'angle_error_flow')


def main():
    """全図の出力と、仕様・元スクリプトを変えないことの確認。"""
    FIG.mkdir(parents=True, exist_ok=True)
    sources = [FIG/'README.md', ROOT/'scripts/draw_session03_figures.py']
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    for draw in [traverse_types, station_selection, interior_angle_sum,
                 direction_angle_propagation, deflection_angle, traverse_example,
                 latitude_departure, closure_preview, inverse_quadrant4,
                 ts_coordinate_mode, exercise_traverse, angle_error_flow]:
        draw()
    for p in sources:
        assert hashlib.sha256(p.read_bytes()).hexdigest() == hashes[str(p.relative_to(ROOT))]
    review_path = QA / 'visual_review.json'
    reviewed = json.loads(review_path.read_text(encoding='utf-8')) if review_path.exists() else {}
    for e in CHECKS:
        e['目視確認'] = reviewed.get('PNG_SHA256', {}).get(e['図']) == e['PNG_SHA256']
    result = {'入力ファイルSHA256': hashes,
              '座標の約束': 'Xが上（北）、Yが右（東）、方向角は北から右回り',
              '仕様の補足': [
                  '緯距経距図はAから真上へΔX、そこからBへ水平にΔY。READMEの「Bの真下」は横成分と両立しないため訂正。',
                  '演習内角の省略値はslides.mdの観測内角表とcheck_exercise_05.pyを参照。',
                  'TS画面の枠は、黒ではなく指定4色のNAVY。画面内は指定日本語フォントを固定セル配置し等幅化。',
                  'README冒頭の図番号参照と一覧が一致しないため、図の一覧のファイル名・内容を優先。'],
              '弧の検査': {'始終点の方位一致': True, '内角は隣接辺の間': True, '計算記録': ANGLES},
              '検査結果': CHECKS}
    (QA/'validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    sheet = Image.new('RGB', (1440, 6*360), 'white')
    draw = ImageDraw.Draw(sheet)
    for i, entry in enumerate(CHECKS):
        x, y = (i % 2)*720, (i//2)*360
        with Image.open(FIG/(entry['図']+'.png')) as im:
            preview = im.convert('RGB')
            preview.thumbnail((710, 325), Image.Resampling.LANCZOS)
            sheet.paste(preview, (x+(720-preview.width)//2, y+28+(325-preview.height)//2))
        draw.text((x+12, y+6), f'{i+1:02d}  '+entry['図'], fill=NAVY)
    sheet.save(QA/'contact_sheet.png')
    print(f'{len(CHECKS)}点のSVG・PNGを保存。フォント: {FONT}')
    print(json.dumps({e['図']: e['文字箱の交差候補'] for e in CHECKS if e['文字箱の交差候補']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
