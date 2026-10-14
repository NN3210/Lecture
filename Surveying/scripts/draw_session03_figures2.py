#!/usr/bin/env python3
"""第3回の追加概念図11〜21をSVG・PNG（180 dpi）で再生成する。"""
from pathlib import Path
import atexit
import hashlib
import json
import os
import shutil
import sys
import tempfile
import warnings

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
_cache = Path(tempfile.mkdtemp(prefix='.session03_cache_', dir=ROOT)).resolve()


def cleanup():
    # 自分が作成した、Surveying直下のキャッシュだけ削除する。
    if _cache.parent != ROOT.resolve() or not _cache.name.startswith('.session03_cache_'):
        raise RuntimeError('キャッシュの削除対象が作業範囲外です。')
    if _cache.exists():
        shutil.rmtree(_cache)


atexit.register(cleanup)
os.environ['MPLCONFIGDIR'] = str(_cache)
os.environ['XDG_CACHE_HOME'] = str(_cache)
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, Ellipse, FancyBboxPatch, Polygon
from matplotlib.text import Text
from PIL import Image, ImageDraw

FIG = ROOT / 'materials/slides/第03回_測量の座標/diagrams'
QA = ROOT / 'notes/session03_figures'
FONT = next((name for name in ['Noto Sans CJK JP', 'Meiryo']
             if name in {f.name for f in font_manager.fontManager.ttflist}), None)
if FONT is None:
    raise RuntimeError('Noto Sans CJK JP または Meiryo をインストールしてください。')
NAVY, TEAL, ORANGE, GRAY = '#1f4e79', '#13877b', '#bd512b', '#526273'
plt.rcParams.update({'font.family': [FONT], 'font.size': 14,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'svg.fonttype': 'path', 'axes.unicode_minus': False,
                     'svg.hashsalt': 'session03_part2', 'text.color': NAVY})
warnings.filterwarnings('error', message=r'Glyph .* missing from font')
CHECKS = []
HEIGHTS = {'coord_concept': 3.4, 'coord_hierarchy': 5.2,
           'ellipsoid_flattening': 3.4, 'geoid_gravity': 3.4,
           'geoid_range': 3.4, 'water_flow': 3.4,
           'datum_shift': 3.4, 'projection_surfaces': 5.2,
           'mercator_tissot': 5.2, 'cylinder_normal_vs_transverse': 5.2,
           'utm_zones_japan': 5.2}


def canvas(h=3.4):
    fig, ax = plt.subplots(figsize=(12, h), dpi=180)
    fig.subplots_adjust(left=.02, right=.98, bottom=.04, top=.96)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, h)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')
    return fig, ax


def box(ax, x, y, w, h, text, color=NAVY, fs=14):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle='round,pad=0.04,rounding_size=0.1',
                 linewidth=1.5, edgecolor=color, facecolor='white'))
    ax.text(x+w/2, y+h/2, text, ha='center', va='center', fontsize=fs,
            color=color, linespacing=1.5)


def arrow(ax, x1, y1, x2, y2, color=GRAY):
    ax.annotate('', (x2, y2), (x1, y1),
                arrowprops={'arrowstyle': '-|>', 'lw': 2, 'color': color})


def double_arrow(ax, x1, y1, x2, y2, color):
    ax.annotate('', (x2, y2), (x1, y1),
                arrowprops={'arrowstyle': '<->', 'lw': 1.6, 'color': color,
                            'shrinkA': 0, 'shrinkB': 0})


def arc(ax, center, radius, start, end, color, head=True):
    angles = np.deg2rad(np.linspace(start, end, 101))
    x = center[0] + radius * np.cos(angles)
    y = center[1] + radius * np.sin(angles)
    ax.plot(x, y, color=color, lw=1.6)
    if head:
        arrow(ax, x[-9], y[-9], x[-1], y[-1], color)


def save(fig, name):
    """図別の高さ・180 dpiの文字境界・PNG余白・欠落グリフを検査。"""
    expected_inches = (12, HEIGHTS[name])
    assert np.allclose(fig.get_size_inches(), expected_inches)
    fig.canvas.draw()
    renderer, bounds = fig.canvas.get_renderer(), fig.bbox
    labels = []
    for label in fig.findobj(Text):
        if not label.get_visible() or not label.get_text():
            continue
        bb = label.get_window_extent(renderer)
        if bb.width and bb.height:
            if bb.x0 < 0 or bb.y0 < 0 or bb.x1 > bounds.x1 or bb.y1 > bounds.y1:
                raise RuntimeError(f'{name}: 文字が画面外です: {label.get_text()}')
            if not 12 <= label.get_fontsize() <= 16:
                raise RuntimeError(f'{name}: 文字サイズ範囲外: {label.get_text()}')
            labels.append({'文字': label.get_text(), 'pt': label.get_fontsize(),
                           '境界px_左下原点': [round(v, 2) for v in bb.extents]})
    svg = FIG / f'{name}.svg'
    fig.savefig(svg, facecolor='white', metadata={'Date': None})
    content = svg.read_text(encoding='utf-8')
    assert '<text' not in content, 'SVGの文字がパス化されていません。'
    svg.write_text('\n'.join(line.rstrip() for line in content.splitlines())+'\n', encoding='utf-8')
    png = FIG / f'{name}.png'
    fig.savefig(png, dpi=180, facecolor='white')
    with Image.open(png) as im:
        im.load()
        expected = tuple(round(v*180) for v in expected_inches)
        assert im.size == expected, (name, im.size, expected)
        assert all(abs(dpi-180) < .02 for dpi in im.info['dpi'])
        pixels = np.asarray(im.convert('RGB'))
        assert all(np.all(edge == 255) for edge in
                   [pixels[:3], pixels[-3:], pixels[:, :3], pixels[:, -3:]])
        ys, xs = np.where(np.any(pixels != 255, axis=2))
        margins = {'左': int(xs.min()), '右': int(im.width-1-xs.max()),
                   '上': int(ys.min()), '下': int(im.height-1-ys.max())}
        CHECKS.append({'図': name, '幅px': im.width, '高さpx': im.height,
                       '寸法inch': list(expected_inches), 'dpi': list(im.info['dpi']),
                       'フォント': FONT, '文字の画面内配置': True,
                       '四辺の白余白': True, '白余白px': margins,
                       '欠落グリフ警告なし': True, 'SVG文字パス化': True,
                       '文字検査': labels})
    plt.close(fig)


def coord_concept():
    fig, ax = canvas()
    origin, scale = np.array([.8, .55]), .85
    transform = lambda p: origin + scale*np.asarray(p)
    theta = np.deg2rad(30)
    rotation = np.array([[np.cos(theta), -np.sin(theta)],
                         [np.sin(theta), np.cos(theta)]])
    point, shifted = np.array([3., 2.]), np.array([1., .5])
    local = rotation.T @ (point-shifted)
    for end, label, offset in [([4.35, 0], 'x', [.10, -.06]),
                                ([0, 2.85], 'y', [-.25, .04])]:
        end = transform(end)
        arrow(ax, *origin, *end, NAVY)
        ax.text(*(end+offset), label, fontsize=14)
    op = transform(shifted)
    for end, label in [([3.65, 0], 'x′'), ([0, 2.4], 'y′')]:
        end = transform(shifted+rotation@np.array(end))
        arrow(ax, *op, *end, TEAL)
        offset = [.22, -.08] if label == 'x′' else [-.30, .04]
        ax.text(*(end+offset), label, color=TEAL, fontsize=14)
    p = transform(point)
    for base, color in [(np.array([point[0], 0]), NAVY),
                         (shifted+rotation@np.array([local[0], 0]), TEAL)]:
        q = transform(base)
        ax.plot([q[0], p[0]], [q[1], p[1]], ':', color=color, lw=1.3)
    ax.plot(*p, 'o', color=ORANGE, ms=6)
    ax.text(p[0]-.30, p[1]+.23, 'P', color=ORANGE, fontsize=16)
    ax.text(.50, .28, 'O', fontsize=13)
    ax.text(op[0]+.12, op[1]-.30, 'O′', color=TEAL, fontsize=13)
    arc(ax, op, .65, 0, 30, TEAL)
    ax.plot([op[0], op[0]+.95], [op[1], op[1]], ':', color=GRAY, lw=1)
    ax.text(op[0]+.80, op[1]+.15, '30°', color=TEAL, fontsize=12)
    ax.text(4.25, 3.07, '(x, y) = (3, 2)', fontsize=13, ha='center')
    ax.text(4.25, 2.74, f'(x′, y′) = ({local[0]:.2f}, {local[1]:.2f})',
            fontsize=12, ha='center', color=TEAL)
    ax.text(.50, .02, 'O′ = (1.0, 0.5) ／ 単位は共通', fontsize=12, color=GRAY)
    box(ax, 6.15, 1.70, 5.40, 1.10,
        '座標系 ＝ 原点 ＋ 軸の向き ＋ 単位\n（＋ 高さの基準面）', fs=14)
    ax.text(8.85, 1.06, '点 ↔ 数の組 の 1 対 1 対応（全単射）',
            ha='center', fontsize=13)
    ax.text(8.85, .48, '点は同じでも、座標系が変わると数が変わる',
            ha='center', fontsize=13, color=ORANGE)
    save(fig, 'coord_concept')


def coord_hierarchy():
    fig, ax = canvas(5.2)
    xs, w = [.15, 3.15, 6.15, 9.15], 2.70
    ax.text(.20, 4.86, '同じ1点を、目的に応じた座標で表す（帯広付近の例）', fontsize=16)
    choices = ['測地系\nJGD2011・GRS80', '測地系',
               '投影法と系の番号\nジオイドモデル', '器械点と後視点']
    titles = ['地心直交座標\n(X, Y, Z)', '地理座標\n緯度 φ・経度 λ\n楕円体高 h',
              '投影座標\n平面直角座標 X, Y\n＋ 標高 H', '局所座標\n器械座標 x, y, h']
    values = ['X = −3 746 081 m\nY = 2 802 427 m\nZ = 4 320 784 m',
              'φ = 42°55′N\nλ = 143°12′E\nh = 85 m',
              '第 XIII 系\nX ≈ −120 000 m\nY ≈ −85 000 m\nH ≈ 56 m（N ≈ 29 m）',
              'x = +12.345 m\ny = −3.210 m\nh = +0.52 m']
    for x, choice, title, value in zip(xs, choices, titles, values):
        ax.text(x+w/2, 4.43, '決めるもの', ha='center', fontsize=12, color=TEAL)
        ax.text(x+w/2, 4.00, choice, ha='center', va='center', fontsize=12,
                color=TEAL, linespacing=1.5)
        box(ax, x, 1.55, w, 2.05, '', fs=14)
        ax.text(x+w/2, 3.15, title, ha='center', va='center', fontsize=14, linespacing=1.4)
        ax.plot([x+.12, x+w-.12], [2.64, 2.64], color=GRAY, alpha=.3, lw=1)
        ax.text(x+w/2, 2.06, value, ha='center', va='center', fontsize=12, linespacing=1.6)
    captions = ['公式で相互変換', '投影（ガウス・クリューゲル）\n標高 H = h − N',
                '器械点の座標と\n後視の方向角']
    for i, caption in enumerate(captions):
        mid = (xs[i]+w+xs[i+1])/2
        double_arrow(ax, xs[i]+w+.04, 2.72, xs[i+1]-.04, 2.72, ORANGE)
        ax.plot([mid, mid], [2.50, 1.26], color=ORANGE, lw=.9)
        ax.text(mid, .88, caption, ha='center', va='center', fontsize=12,
                color=ORANGE, linespacing=1.6)
    ax.text(6, .15, '局所座標の h は、器械座標での高さ（地理座標の楕円体高 h とは区別）',
            ha='center', fontsize=12, color=GRAY)
    save(fig, 'coord_hierarchy')


def ellipsoid_flattening():
    fig, ax = canvas()
    c, a = np.array([1.65, 1.72]), 1.16
    b = a*(1-1/30)
    ax.add_patch(Circle(c, a, fill=False, edgecolor=GRAY, ls='--', lw=1.5))
    ax.add_patch(Ellipse(c, 2*a, 2*b, fill=False, edgecolor=NAVY, lw=2.5))
    double_arrow(ax, *c, c[0]+a, c[1], NAVY)
    double_arrow(ax, *c, c[0], c[1]+b, TEAL)
    ax.text(2.12, 1.43, 'a', fontsize=15)
    ax.text(1.35, 2.22, 'b', fontsize=15, color=TEAL)
    ax.plot(*c, 'o', color=GRAY, ms=3)
    ax.text(.55, 3.02, '子午線断面', fontsize=14)
    ax.text(.40, .20, '破線：半径 a の円', fontsize=12, color=GRAY)
    ax.text(3.15, 2.77, '赤道半径 a = 6 378 137 m', fontsize=13)
    ax.text(3.15, 2.23, '極半径 b = 6 356 752 m', fontsize=13, color=TEAL)
    ax.text(3.15, 1.64, '差 a − b：約 21 km', fontsize=14, color=ORANGE)
    ax.text(3.15, .92, '扁平率 f = (a − b)/a\n　　　　 = 1/298.257',
            fontsize=13, linespacing=1.6)
    box(ax, 7.15, 1.61, 4.55, 1.18,
        '地球は赤道方向に約 21 km\nふくらんだ回転楕円体', fs=14)
    ax.text(9.40, .92, '誇張して描いている\n（実際の差は 0.3 %）',
            ha='center', fontsize=13, color=GRAY, linespacing=1.6)
    ax.text(9.40, .23, '図の扁平率は 1/30', ha='center', fontsize=12, color=GRAY)
    save(fig, 'ellipsoid_flattening')


def geoid_gravity():
    fig, ax = canvas()
    x = np.linspace(.3, 6.50, 400)
    ellipsoid = lambda v: .57-.008*(np.asarray(v)-3.4)**2
    geoid = lambda v: .88+.48*np.exp(-((np.asarray(v)-1.7)/1.6)**2)
    slope = lambda v: -.96*(v-1.7)/1.6**2*np.exp(-((v-1.7)/1.6)**2)
    # 山の右側では下向き法線が山へ傾く。糸を曲線の法線に一致させる。
    ax.add_patch(Polygon([[.30, 1.30], [.65, 1.55], [1.35, 2.62],
                          [1.70, 2.90], [2.2, 2.10], [2.9, 1.22]],
                         facecolor=GRAY, alpha=.20, edgecolor=GRAY))
    sea = x[x >= 3.6]
    ax.fill_between(sea, geoid(sea), geoid(sea)+.13, color=TEAL, alpha=.15)
    ax.plot(x, ellipsoid(x), color=ORANGE, lw=2)
    ax.plot(x, geoid(x), color=TEAL, lw=2.5)
    ax.text(.30, 3.04, '密度の大きい山', fontsize=13, color=GRAY)
    ax.text(5.85, 1.22, '海', fontsize=14, color=TEAL)
    for xpos in [3.05, 4.35, 5.75]:
        foot = np.array([xpos, geoid(xpos)])
        normal = np.array([-slope(xpos), 1.])
        normal /= np.linalg.norm(normal)
        top, weight = foot+1.32*normal, foot+.12*normal
        ax.plot([top[0], top[0]], [foot[1], top[1]], ':', color=GRAY, lw=.8)
        ax.plot([top[0], weight[0]], [top[1], weight[1]], color=NAVY, lw=1.8)
        ax.plot(*top, 'o', color=NAVY, ms=3)
        ax.add_patch(Circle(weight, .07, color=NAVY))
        # 接線と法線の直交を小さな直角記号で示す。
        tangent = np.array([normal[1], -normal[0]])
        pts = np.array([foot+.13*tangent, foot+.13*(tangent+normal), foot+.13*normal])
        ax.plot(pts[:, 0], pts[:, 1], color=TEAL, lw=1)
    arrow(ax, 4.0, 2.57, 3.45, 2.57, ORANGE)
    ax.text(4.18, 2.57, '山側へ傾く', va='center', fontsize=12, color=ORANGE)
    ax.text(4.18, 2.92, 'おもりを吊るした糸', fontsize=12)
    ax.text(.35, 1.53, 'ジオイド', fontsize=13, color=TEAL)
    ax.text(.35, .23, '楕円体', fontsize=13, color=ORANGE)
    ax.text(3.15, .15, '起伏と糸の傾きは誇張', fontsize=12, color=GRAY)
    ax.plot([6.90, 6.90], [.3, 3.05], color=GRAY, alpha=.25)
    ax.text(7.20, 2.71, '水は重力に垂直な面で静止する', fontsize=14)
    ax.text(7.20, 1.94, 'おもりの糸（鉛直線）は\nジオイドに垂直',
            fontsize=14, linespacing=1.6)
    ax.text(7.20, .78, '水準器の気泡が示す「水平」を\nつないだ面がジオイド',
            fontsize=14, color=TEAL, linespacing=1.6)
    save(fig, 'geoid_gravity')


def geoid_range():
    fig, ax = canvas()
    xx = lambda n: .45+(n+120)/220*7.10
    y = 1.24
    arrow(ax, xx(-120), y, xx(100)+.13, y, NAVY)
    for n in [-120, -80, -40, 0, 100]:
        ax.plot([xx(n), xx(n)], [y-.07, y+.07], color=NAVY, lw=1.1)
        ax.text(xx(n), y-.32, str(n).replace('-', '−') if n <= 0 else f'+{n}',
                ha='center', fontsize=12)
    ax.plot([xx(20), xx(45)], [y, y], color=TEAL, lw=15, alpha=.28, solid_capstyle='butt')
    ax.text(.45, 3.02, 'ジオイド高 N（m）：楕円体からの高さ', fontsize=15)
    for n, title, tx in [(-106, '世界最小 約 −106 m\n（インド南方の海）', .45),
                         (85, '世界最大 約 +85 m\n（ニューギニア付近）', 5.00)]:
        ax.plot(xx(n), y, 'o', color=NAVY, ms=5)
        ax.plot([xx(n), xx(n)], [y+.12, 2.17], color=GRAY, lw=.9)
        ax.text(tx, 2.34, title, fontsize=12, linespacing=1.5)
    for n in [29, 37]:
        ax.plot(xx(n), y, 'o', color=ORANGE, ms=5)
    ax.annotate('帯広 約 +29 m', xy=(xx(29), y-.12), xytext=(3.25, .31),
                fontsize=12, color=ORANGE,
                arrowprops={'arrowstyle': '-', 'color': ORANGE, 'lw': 1})
    ax.annotate('東京 約 +37 m', xy=(xx(37), y-.12), xytext=(5.70, .31),
                fontsize=12, color=ORANGE,
                arrowprops={'arrowstyle': '-', 'color': ORANGE, 'lw': 1})
    ax.text(4.55, 1.65, '日本 約 +20〜+45 m', fontsize=12, color=TEAL)
    box(ax, 8.05, .92, 3.65, 1.75,
        'N は楕円体から\nジオイドまでの高さ。\n日本では楕円体の上に\n20〜45 m', fs=14)
    save(fig, 'geoid_range')


def water_flow():
    fig, ax = canvas()
    # 図内の縦方向も指定値に比例。Hは共通のジオイドから測る。
    xa, xb, z0, scale = 1.55, 5.40, 1.64, .031
    e_a, e_b = z0-40*scale, z0-34*scale
    a, b = np.array([xa, z0+20*scale]), np.array([xb, z0+24*scale])
    x = np.linspace(.35, 6.70, 200)
    ellipsoid = e_a+(e_b-e_a)*(x-xa)/(xb-xa)
    ax.plot(x, np.full_like(x, z0), color=TEAL, lw=2.4)
    ax.plot(x, ellipsoid, color=ORANGE, lw=2.4)
    ax.plot([xa, xb], [a[1], b[1]], color=GRAY, lw=1.5)
    for p, e, name in [(a, e_a, 'A'), (b, e_b, 'B')]:
        ax.plot([p[0], p[0]], [e, p[1]], ':', color=GRAY, lw=1)
        ax.plot(*p, 'o', color=NAVY, ms=5)
        ax.text(p[0]-.10, p[1]+.19, name, fontsize=16)
    for xpos, lo, hi, label, color, dx in [
            (.95, e_a, a[1], 'h = 60 m', ORANGE, -.12),
            (1.94, e_a, z0, 'N = 40 m', TEAL, .12),
            (1.94, z0, a[1], 'H = 20 m', NAVY, .12),
            (5.96, e_b, b[1], 'h = 58 m', ORANGE, .12),
            (5.02, e_b, z0, 'N = 34 m', TEAL, -.12),
            (5.02, z0, b[1], 'H = 24 m', NAVY, -.12)]:
        double_arrow(ax, xpos, lo, xpos, hi, color)
        ax.text(xpos+dx, (lo+hi)/2, label, ha='left' if dx > 0 else 'right',
                va='center', fontsize=12, color=color,
                rotation=90 if label.startswith('h') else 0,
                bbox={'facecolor': 'white', 'edgecolor': 'none', 'pad': 1})
    arrow(ax, 4.90, 2.77, 2.10, 2.66, NAVY)
    ax.text(3.5, 2.94, '水は B → A に流れる', ha='center', fontsize=14)
    ax.text(.35, .06, '楕円体（傾きを誇張）', fontsize=12, color=ORANGE)
    ax.text(3.5, 1.40, 'ジオイド', ha='center', fontsize=12, color=TEAL,
            bbox={'facecolor': 'white', 'edgecolor': 'none', 'pad': 1})
    box(ax, 7.35, 1.80, 4.25, 1.10,
        '楕円体高 h：A > B\n標高 H：B > A', fs=15)
    ax.text(7.45, 1.05, '楕円体高では\n水の流れる向きが分からない',
            fontsize=14, linespacing=1.6)
    ax.text(7.45, .32, '農業水利・排水の設計は\n標高 H で判断する',
            fontsize=14, color=TEAL, linespacing=1.6)
    save(fig, 'water_flow')


def datum_shift():
    fig, ax = canvas()
    p = np.array([2.78, 2.62])
    # 共通の点Pから各楕円に下ろした法線をNewton法で求める。
    ellipses = [(np.array([1.40, 1.67]), 1.25, 1.02, GRAY, '--'),
                (np.array([1.94, 1.48]), 1.29, 1.13, NAVY, '-')]
    normals = []
    for center, a, b, color, style in ellipses:
        ax.add_patch(Ellipse(center, 2*a, 2*b, fill=False,
                             edgecolor=color, ls=style, lw=2))
        ax.plot(*center, '+', color=color, ms=7)
        angle = np.arctan2(p[1]-center[1], p[0]-center[0])
        for _ in range(12):
            q = center + [a*np.cos(angle), b*np.sin(angle)]
            tangent = np.array([-a*np.sin(angle), b*np.cos(angle)])
            second = np.array([-a*np.cos(angle), -b*np.sin(angle)])
            angle -= np.dot(q-p, tangent)/(np.dot(tangent, tangent)+np.dot(q-p, second))
        q = center + [a*np.cos(angle), b*np.sin(angle)]
        normal = (q-center)/np.array([a*a, b*b])
        normal /= np.linalg.norm(normal)
        offset = p-q
        assert abs(offset[0]*normal[1]-offset[1]*normal[0]) < 1e-10
        lo, hi = q-.72*normal, p
        ax.plot([lo[0], hi[0]], [lo[1], hi[1]], color=color, ls=style, lw=1.7)
        ax.plot(*q, 'o', color=color, ms=3)
        normals.append((q, normal))
    ax.plot(*p, 'o', color=ORANGE, ms=6, zorder=5)
    ax.text(p[0]+.17, p[1]+.06, 'P（同じ杭）', fontsize=13, color=ORANGE)
    ax.text(.35, 3.03, '測地系が変わると、基準の楕円体も変わる', fontsize=14)
    for (q, n), text, ty, color in zip(normals,
            ['旧測地系の法線', '世界測地系の法線'], [1.88, 1.10], [GRAY, NAVY]):
        ax.annotate(text, xy=q-.43*n, xytext=(3.75, ty), fontsize=12, color=color,
                    arrowprops={'arrowstyle': '-', 'color': color, 'lw': 1},
                    bbox={'facecolor': 'white', 'edgecolor': 'none', 'pad': 2})
    ax.text(.35, .17, '中心・形状・法線の差は誇張（子午線断面）', fontsize=12, color=GRAY)
    ax.plot([6.05, 6.05], [.35, 3.05], color=GRAY, alpha=.25)
    ax.text(6.35, 2.68, '同じ杭でも、測地系が違えば\n緯度・経度は違う', fontsize=15, linespacing=1.5)
    ax.text(6.35, 1.72, '旧日本測地系 → 世界測地系\n東京付近では約 450 m、北西へずれる',
            fontsize=13, color=ORANGE, linespacing=1.5)
    ax.text(6.35, 1.21, '座標の表す位置の差（杭そのものは動かない）', fontsize=12, color=GRAY)
    ax.text(6.35, .71, 'ベッセル  a = 6 377 397 m', fontsize=13, color=GRAY)
    ax.text(6.35, .27, 'GRS80     a = 6 378 137 m', fontsize=13)
    save(fig, 'datum_shift')


def projection_surfaces():
    fig, ax = canvas(5.2)

    def globe(x, y, r=.63):
        ax.add_patch(Circle((x, y), r, facecolor=GRAY, alpha=.08, edgecolor='none'))
        ax.add_patch(Circle((x, y), r, fill=False, edgecolor=GRAY, lw=1.4))
        ax.add_patch(Ellipse((x, y), 2*r, .36*r, fill=False, edgecolor=GRAY, lw=.8))
        ax.add_patch(Ellipse((x, y), .65*r, 2*r, fill=False, edgecolor=GRAY, lw=.8))

    # 接円筒：球の赤道と同じ半径、上下の輪郭を斜めに見せる。
    globe(2, 3.91)
    for y in [3.08, 4.74]:
        ax.add_patch(Ellipse((2, y), 1.26, .32, fill=False, edgecolor=NAVY, lw=2))
    for x in [1.37, 2.63]:
        ax.plot([x, x], [3.08, 4.74], color=NAVY, lw=2)
    ax.add_patch(Ellipse((2, 3.91), 1.26, .23, fill=False, edgecolor=NAVY, lw=2))
    ax.text(2, 4.99, '円筒に写す', ha='center', fontsize=15)

    # 接円錐：側面の直線を球に接するように計算。
    globe(6, 3.91)
    apex, radius, bottom = 4.99, .63, 3.12
    dz = apex-3.91
    touch_y = 3.91+radius**2/dz
    touch_x = np.sqrt(radius**2-(touch_y-3.91)**2)
    half = touch_x*(apex-bottom)/(apex-touch_y)
    ax.plot([6-half, 6, 6+half], [bottom, apex, bottom], color=TEAL, lw=2)
    ax.add_patch(Ellipse((6, bottom), 2*half, .32, fill=False, edgecolor=TEAL, lw=2))
    ax.add_patch(Ellipse((6, touch_y), 2*touch_x, .17, fill=False, edgecolor=TEAL, lw=2))
    ax.text(7.04, 4.76, '円錐に写す', ha='left', fontsize=15, color=TEAL)

    globe(10, 3.80)
    ax.add_patch(Polygon([[8.85, 4.18], [10.56, 4.18], [11.15, 4.68], [9.44, 4.68]],
                         facecolor=ORANGE, alpha=.10, edgecolor='none'))
    ax.add_patch(Polygon([[8.85, 4.18], [10.56, 4.18], [11.15, 4.68], [9.44, 4.68]],
                         fill=False, edgecolor=ORANGE, lw=2))
    ax.plot(10, 4.43, 'o', color=ORANGE, ms=4)
    ax.text(10, 4.99, '平面に写す', ha='center', fontsize=15, color=ORANGE)
    ax.text(6, 2.62, '曲面は裂け目なしに平面に広げられない → 必ずどこかがひずむ',
            ha='center', fontsize=15)
    for x in [2, 6, 10]:
        arrow(ax, x, 2.37, x, 2.05)
    # 展開後の面：長方形・扇形・円。
    ax.add_patch(Polygon([[.95, 1.00], [3.05, 1.00], [3.05, 1.90], [.95, 1.90]],
                         fill=False, edgecolor=NAVY, lw=2))
    theta = np.linspace(np.deg2rad(210), np.deg2rad(330), 101)
    sector = np.column_stack((6+1.15*np.cos(theta), 2.08+1.15*np.sin(theta)))
    ax.add_patch(Polygon(np.vstack(([6, 2.08], sector)), fill=False, edgecolor=TEAL, lw=2))
    ax.add_patch(Circle((10, 1.47), .57, fill=False, edgecolor=ORANGE, lw=2))
    for x, title, example, color in [
            (2, '円筒図法', 'メルカトル・横メルカトル', NAVY),
            (6, '円錐図法', '地形図の一部・航空図', TEAL),
            (10, '方位図法', '極の地図・航空の大圏', ORANGE)]:
        ax.text(x, .60, title, ha='center', fontsize=15, color=color)
        ax.text(x, .20, example, ha='center', fontsize=13, color=color)
    save(fig, 'projection_surfaces')


def mercator_y(latitude):
    """単位球のメルカトル縦座標（経度のラジアンと同じ単位）。"""
    return np.log(np.tan(np.pi/4+np.deg2rad(latitude)/2))


def mercator_tissot():
    fig = plt.figure(figsize=(12, 5.2), dpi=180)
    ax = fig.add_axes([.055, .15, .61, .76])
    # xもyもラジアン。equalにより赤道での東西・南北の縮尺を一致させる。
    ymax = mercator_y(75)
    ax.set_xlim(-np.pi, np.pi)
    ax.set_ylim(-ymax-.45, ymax+.45)
    ax.set_aspect('equal', adjustable='box')
    for lon in range(-180, 181, 30):
        ax.plot(np.deg2rad([lon, lon]), [-ymax, ymax], color=GRAY, alpha=.4, lw=.8)
    for lat in [-75, -60, -30, 0, 30, 60, 75]:
        ax.plot([-np.pi, np.pi], [mercator_y(lat)]*2, color=GRAY,
                alpha=.65 if lat == 0 else .4, lw=1.2 if lat == 0 else .8)
        radius = np.deg2rad(6)/np.cos(np.deg2rad(lat))
        for lon in range(-150, 151, 60):
            ax.add_patch(Circle((np.deg2rad(lon), mercator_y(lat)), radius,
                               facecolor=TEAL, edgecolor=TEAL, alpha=.25, lw=1.2))
    ax.set_xticks(np.deg2rad(np.arange(-180, 181, 60)),
                  ['−180°', '−120°', '−60°', '0°', '60°', '120°', '180°'], fontsize=12)
    lats = [-75, -60, -30, 0, 30, 60, 75]
    ax.set_yticks([mercator_y(lat) for lat in lats],
                  [f'{lat}°'.replace('-', '−') for lat in lats], fontsize=12)
    ax.set_xlabel('経度 λ', fontsize=13, labelpad=6, color=NAVY)
    ax.set_ylabel('緯度 φ', fontsize=13, labelpad=5, color=NAVY)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0, pad=5, colors=GRAY)
    ax.plot(np.deg2rad(137), mercator_y(35), 'o', color=ORANGE, ms=5, zorder=5)
    ax.annotate('日本', xy=(np.deg2rad(137), mercator_y(35)),
                xytext=(np.deg2rad(79), mercator_y(43)), fontsize=13, color=ORANGE,
                arrowprops={'arrowstyle': '-', 'lw': 1, 'color': ORANGE},
                bbox={'facecolor': 'white', 'edgecolor': 'none', 'pad': 1})
    fig.text(.035, .95, 'メルカトル図法とティソーの指示楕円', fontsize=16)
    fig.text(.69, .84, 'y = ln tan(45° + φ/2)', fontsize=15)
    fig.text(.69, .76, 'x = λ（ラジアン、単位球）', fontsize=12, color=GRAY)
    fig.text(.69, .59, '地球上で同じ大きさの円が、\n高緯度ほど大きく描かれる',
             fontsize=14, linespacing=1.6)
    fig.text(.69, .39, '長さ：1/cos φ 倍\n面積：1/cos² φ 倍\n緯度 60° で面積 4 倍',
             fontsize=14, color=TEAL, linespacing=1.7)
    fig.text(.69, .20, '角は保たれる（等角）\n→ 航海・測量で使う', fontsize=14, linespacing=1.6)
    fig.text(.035, .025, '円は各点の局所縮尺を示す（赤道の半径 6° 相当）。±75° の円全体が見える余白を付加。',
             fontsize=12, color=GRAY)
    fig.canvas.draw()
    origin, east, north = ax.transData.transform([[0, 0], [np.deg2rad(1), 0], [0, np.deg2rad(1)]])
    xscale, yscale = np.linalg.norm(east-origin), np.linalg.norm(north-origin)
    assert np.isclose(xscale, yscale, rtol=1e-12)
    assert np.isclose(1/np.cos(np.deg2rad(60))**2, 4)
    save(fig, 'mercator_tissot')
    CHECKS[-1]['投影検算'] = {'式': 'y = ln tan(π/4 + φ/2), x = λ（ラジアン）',
                             '赤道1度相当px_経度_緯度': [xscale, yscale],
                             '縦横縮尺一致': True, '緯度60度の面積倍率': 4,
                             '緯度_deg': lats, 'y': [float(mercator_y(lat)) for lat in lats],
                             '円半径_rad': [float(np.deg2rad(6)/np.cos(np.deg2rad(lat))) for lat in lats]}


def cylinder_normal_vs_transverse():
    fig = plt.figure(figsize=(12, 5.2), dpi=180)
    theta = np.linspace(0, 2*np.pi, 121)
    latitude = np.linspace(-np.pi/2, np.pi/2, 13)
    longitude = np.linspace(0, 2*np.pi, 25)
    u, v = np.meshgrid(longitude, latitude)
    # 地球の極軸は左右ともz軸。右の円筒軸だけをx軸へ寝かせる。
    for i, transverse in enumerate([False, True]):
        ax = fig.add_axes([.04+.49*i, .23, .43, .62], projection='3d')
        ax.set_proj_type('ortho')
        ax.view_init(elev=20, azim=-55)
        ax.set_box_aspect((1, 1, 1))
        ax.set(xlim=(-1.5, 1.5), ylim=(-1.5, 1.5), zlim=(-1.5, 1.5))
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])
        ax.set_axis_off()
        ax.plot_wireframe(np.cos(v)*np.cos(u), np.cos(v)*np.sin(u), np.sin(v),
                          color=GRAY, alpha=.40, lw=.65, rstride=1, cstride=1)
        t, height = np.meshgrid(theta, np.linspace(-1.35, 1.35, 10))
        xyz = (height, np.cos(t), np.sin(t)) if transverse else (np.cos(t), np.sin(t), height)
        ax.plot_surface(*xyz, color=NAVY, alpha=.07, linewidth=0, shade=False,
                        rcount=10, ccount=61)
        for end in [-1.35, 1.35]:
            ring = (np.full_like(theta, end), np.cos(theta), np.sin(theta)) if transverse else (
                    np.cos(theta), np.sin(theta), np.full_like(theta, end))
            ax.plot(*ring, color=NAVY, lw=1.8)
        for angle in np.deg2rad([0, 90, 180, 270]):
            line = ([-1.35, 1.35], [np.cos(angle)]*2, [np.sin(angle)]*2) if transverse else (
                    [np.cos(angle)]*2, [np.sin(angle)]*2, [-1.35, 1.35])
            ax.plot(*line, color=NAVY, alpha=.8, lw=1.2)
        contact = (np.zeros_like(theta), np.cos(theta), np.sin(theta)) if transverse else (
                    np.cos(theta), np.sin(theta), np.zeros_like(theta))
        ax.plot(*contact, color=ORANGE, lw=3)
        ax.plot([0, 0], [0, 0], [-1.48, 1.48], color=GRAY, ls=':', lw=1.2)
        cylinder_axis = ([-1.48, 1.48], [0, 0], [0, 0]) if transverse else (
                        [0, 0], [0, 0], [-1.48, 1.48])
        ax.plot(*cylinder_axis, color=NAVY, ls='--', lw=1.6)
        # 3D軸には文字を置かず、図座標に注記をまとめる。
    fig.text(.25, .93, '正軸円筒', ha='center', fontsize=16)
    fig.text(.75, .93, '横軸円筒', ha='center', fontsize=16)
    fig.text(.25, .85, '円筒の軸を極軸に合わせる', ha='center', fontsize=13)
    fig.text(.75, .85, '円筒の軸を赤道面に寝かせる', ha='center', fontsize=13)
    fig.text(.25, .25, 'メルカトル（赤道に接する）', ha='center', fontsize=14)
    fig.text(.75, .25, '横メルカトル＝ガウス・クリューゲル', ha='center', fontsize=14)
    fig.text(.75, .18, '中央子午線に接する', ha='center', fontsize=13, color=ORANGE)
    fig.text(.25, .18, '橙：接する赤道', ha='center', fontsize=13, color=ORANGE)
    fig.text(.50, .09, '接線の近くはひずみが小さい → 細長い帯に分けて使う（UTM、平面直角座標系）',
             ha='center', fontsize=14)
    fig.text(.50, .025, '接円筒の模式図。実際には中央の縮尺を調整する。灰色点線：極軸／紺色破線：円筒軸。',
             ha='center', fontsize=12, color=GRAY)
    save(fig, 'cylinder_normal_vs_transverse')
    CHECKS[-1]['描画方式'] = 'mplot3d（正投影）、日本語はすべてfig.text'


def utm_zones_japan():
    fig = plt.figure(figsize=(12, 5.2), dpi=180)
    ax = fig.add_axes([.065, .19, .58, .68])
    ax.set(xlim=(120, 156), ylim=(24, 46))
    ax.set_xticks(np.arange(120, 157, 6), [f'{x}°' for x in range(120, 157, 6)], fontsize=12)
    ax.set_yticks([24, 30, 36, 42, 46], [f'{x}°' for x in [24, 30, 36, 42, 46]], fontsize=12)
    ax.set_xlabel('東経', fontsize=13, labelpad=7, color=NAVY)
    ax.set_ylabel('北緯', fontsize=13, labelpad=5, color=NAVY)
    for spine in ax.spines.values():
        spine.set_color(GRAY)
    for i, west in enumerate(range(120, 156, 6)):
        ax.axvspan(west, west+6, color=TEAL if i % 2 else NAVY, alpha=.055)
        ax.axvline(west, color=GRAY, lw=.6, alpha=.4)
        ax.axvline(west+3, color=NAVY, lw=1.1, ls='--', alpha=.7)
        ax.text(west+3, 46.5, f'{51+i}帯', ha='center', va='bottom', fontsize=14, clip_on=False)
        ax.text(west+3, 25.0, f'{west+3}°', ha='center', fontsize=12, color=NAVY)
    # 回転楕円の外接範囲を指定の経緯度範囲に一致させる。
    def island(xlo, xhi, ylo, yhi, angle):
        rx2, ry2 = ((xhi-xlo)/2)**2, ((yhi-ylo)/2)**2
        c2, s2 = np.cos(np.deg2rad(angle))**2, np.sin(np.deg2rad(angle))**2
        a2, b2 = np.linalg.solve([[c2, s2], [s2, c2]], [rx2, ry2])
        assert a2 > 0 and b2 > 0
        ax.add_patch(Ellipse(((xlo+xhi)/2, (ylo+yhi)/2), 2*np.sqrt(a2), 2*np.sqrt(b2),
                             angle=angle, facecolor=GRAY, alpha=.25, edgecolor=GRAY, lw=1))
    island(139, 146, 41.5, 45.5, 12)
    island(131, 142, 34, 41, 30)
    island(132.5, 134.5, 33, 34.5, 15)
    island(129.5, 132, 31, 34, 75)
    for lon, lat in zip(np.linspace(123.25, 130.75, 9), np.linspace(24.25, 29.75, 9)):
        ax.add_patch(Ellipse((lon, lat), .4, .3, angle=30, facecolor=GRAY, alpha=.45, edgecolor='none'))
    for label, xy, target in [
            ('北海道', (149, 44.2), (144.7, 44.0)),
            ('本州', (145.3, 37.9), (139, 38.4)),
            ('四国', (137.3, 31.9), (133.7, 33.8)),
            ('九州', (124, 34), (130.5, 32.4)),
            ('南西諸島', (121.5, 29.4), (126.8, 26.9))]:
        ax.annotate(label, xy=target, xytext=xy, fontsize=12, color=GRAY,
                    arrowprops={'arrowstyle': '-', 'lw': .8, 'color': GRAY},
                    bbox={'facecolor': 'white', 'edgecolor': 'none', 'pad': 1})
    ax.plot(143.2, 42.9, 'o', color=ORANGE, ms=6, zorder=6)
    ax.annotate('帯広', xy=(143.2, 42.9), xytext=(149, 41.1), fontsize=13, color=ORANGE,
                arrowprops={'arrowstyle': '-', 'lw': 1.1, 'color': ORANGE})
    ax.tick_params(labelsize=12, colors=GRAY)
    fig.text(.04, .95, 'UTM：経度 6° ごとの帯と日本の位置', fontsize=16)
    overlay = fig.add_axes([0, 0, 1, 1], frameon=False)
    overlay.set(xlim=(0, 12), ylim=(0, 5.2))
    overlay.axis('off')
    box(overlay, 8.15, 2.50, 3.50, 1.76,
        'UTM：6° 幅 × 60 帯\n原点の縮尺係数 0.9996\nE は 500 000 m を足して\n負を避ける', fs=13)
    box(overlay, 8.15, 1.14, 3.50, 1.04,
        '平面直角座標系：19 系\n原点から東西に約 130 km\n原点の縮尺係数 0.9999', fs=12)
    fig.text(.68, .075, '帯広：第 54 帯\n中央子午線 141°E', fontsize=14, color=ORANGE, linespacing=1.5)
    fig.text(.065, .025, '破線：中央子午線。楕円・点列は島の位置を示す模式図。', fontsize=12, color=GRAY)
    assert int((143.2+180)//6)+1 == 54
    save(fig, 'utm_zones_japan')
    CHECKS[-1]['帯広の帯番号'] = 54
    CHECKS[-1]['中央子午線_degE'] = 141
    CHECKS[-1]['島の表現'] = '指定の経緯度範囲内の楕円・点列（海岸線なし）'


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    CHECKS.clear()
    # 既存10点・指示書・既存スクリプトを保護し、11〜16の再生成一致も検査。
    draws = [coord_concept, coord_hierarchy, ellipsoid_flattening,
             geoid_gravity, geoid_range, water_flow, datum_shift,
             projection_surfaces, mercator_tissot, cylinder_normal_vs_transverse,
             utm_zones_japan]
    previous_six = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for draw in draws[:6] for suffix in ['.svg', '.png']
                    if (p := FIG/(draw.__name__+suffix)).exists()}
    prior_path = QA/'validation_part2.json'
    prior_checks = json.loads(prior_path.read_text(encoding='utf-8'))['検査結果'] if prior_path.exists() else []
    new_names = {draw.__name__ for draw in draws}
    protected = [ROOT/'scripts/draw_session03_figures.py', FIG/'README.md']
    protected += [p for p in FIG.iterdir() if p.suffix in ('.svg', '.png') and p.stem not in new_names]
    before = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in protected}
    for draw in draws:
        draw()
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == digest
               for p, digest in before.items())
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == digest
               for p, digest in previous_six.items()), '既存6点の再生成結果が変わりました。'
    # 目視済みの画像と完全一致した場合に限り、以前の確認記録を引き継ぐ。
    for entry in CHECKS:
        digest = hashlib.sha256((FIG/(entry['図']+'.png')).read_bytes()).hexdigest()
        for old in prior_checks:
            visual = old.get('目視点検', {})
            if old['図'] == entry['図'] and visual.get('確認画像_SHA256') == digest:
                entry['目視点検'] = visual
    sheet = Image.new('RGB', (1440, ((len(CHECKS)+1)//2)*350), 'white')
    pen = ImageDraw.Draw(sheet)
    for i, entry in enumerate(CHECKS):
        x, y = (i % 2)*720, (i//2)*350
        with Image.open(FIG/(entry['図']+'.png')) as im:
            preview = im.convert('RGB')
            preview.thumbnail((720, 312), Image.Resampling.LANCZOS)
            sheet.paste(preview, (x, y+30+(312-preview.height)//2))
        pen.text((x+12, y+7), entry['図'], fill=NAVY)
    sheet.save(QA/'contact_sheet_part2.png')
    cleanup()
    report = {'保護対象_SHA256': before, '保護対象の変更なし': True,
              '既存6点_再生成前_SHA256': previous_six, '既存6点_再生成一致': True,
              '座標変換': {'P': [3, 2], 'O′': [1.0, .5], '軸の反時計回り回転_deg': 30,
                          'Pの第2座標_小数2桁': [2.48, .30]},
              '検査結果': CHECKS, '今回のキャッシュ削除済み': not _cache.exists(),
              '目視点検': 'PNG表示による確認結果は点検記録.mdを参照'}
    (QA/'validation_part2.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'{len(CHECKS)}点のSVG・PNGを保存。フォント: {FONT}。サイズ・dpi・余白・文字を検査済み。')


if __name__ == '__main__':
    main()
