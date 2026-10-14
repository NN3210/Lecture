#!/usr/bin/env python3
"""第3回「測量の座標」の概念図10点をSVG・PNG（180 dpi）で再生成する。"""
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
# キャッシュは作業対象の配下に限定し、自分で作ったフォルダだけ終了時に削除。
_cache = tempfile.mkdtemp(prefix='.session03_cache_', dir=ROOT)
atexit.register(shutil.rmtree, _cache, ignore_errors=True)
os.environ['MPLCONFIGDIR'] = _cache
os.environ['XDG_CACHE_HOME'] = _cache
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Ellipse, FancyBboxPatch, Polygon
from matplotlib.text import Text
from PIL import Image, ImageDraw

FIG = ROOT / 'materials/slides/第03回_測量の座標/diagrams'
QA = ROOT / 'notes/session03_figures'
FONT = next((name for name in ['Noto Sans CJK JP', 'Meiryo']
             if name in {f.name for f in font_manager.fontManager.ttflist}), None)
if FONT is None:
    raise RuntimeError('Noto Sans CJK JP または Meiryo をインストールしてください。')
plt.rcParams.update({'font.family': [FONT], 'font.size': 14,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'svg.fonttype': 'path', 'axes.unicode_minus': False,
                     'svg.hashsalt': 'session03', 'text.color': '#1f4e79'})
NAVY, TEAL, ORANGE, GRAY = '#1f4e79', '#13877b', '#bd512b', '#526273'
warnings.filterwarnings('error', message=r'Glyph .* missing from font')
CHECKS = []


def save(fig, name):
    """既存の保存流儀を踏襲し、余白の自動切除だけ省いて幅12インチを保つ。"""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bounds = fig.bbox
    for label in fig.findobj(Text):
        if not label.get_visible() or not label.get_text():
            continue
        # 目盛の非表示側ラベルは対象外。
        bb = label.get_window_extent(renderer)
        if bb.width and bb.height and (bb.x0 < -1 or bb.y0 < -1 or
                                      bb.x1 > bounds.x1 + 1 or bb.y1 > bounds.y1 + 1):
            raise RuntimeError(f'{name}: 文字が画面外です: {label.get_text()}')
        if not 12 <= label.get_fontsize() <= 16:
            raise RuntimeError(f'{name}: 文字サイズ範囲外: {label.get_text()}')
    svg = FIG / f'{name}.svg'
    fig.savefig(svg, facecolor='white', metadata={'Date': None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())
                   + '\n', encoding='utf-8')
    png = FIG / f'{name}.png'
    fig.savefig(png, dpi=180, facecolor='white')
    with Image.open(png) as im:
        im.load()
        expected = tuple(round(v * 180) for v in fig.get_size_inches())
        assert im.size == expected, (name, im.size, expected)
        assert abs(im.info['dpi'][0] - 180) < .02
        # 四辺の白余白を確認（画像端への描画の接触を検出）。
        pixels = np.asarray(im.convert('RGB'))
        assert all(np.all(edge == 255) for edge in
                   [pixels[:3], pixels[-3:], pixels[:, :3], pixels[:, -3:]])
        CHECKS.append({'図': name, '幅px': im.width, '高さpx': im.height,
                       'dpi': list(im.info['dpi']), 'フォント': FONT,
                       '文字の画面内配置': True, '四辺の余白': True})
    plt.close(fig)


def canvas(h=3.2):
    fig, ax = plt.subplots(figsize=(12, h))
    fig.subplots_adjust(left=.02, right=.98, bottom=.04, top=.96)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, h)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')
    return fig, ax


def box(ax, x, y, w, h, text, color=NAVY, fs=14):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle='round,pad=0.04,rounding_size=0.1',
                 linewidth=1.5, edgecolor=color, facecolor='#f3f7fb'))
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


def three_surfaces():
    fig, ax = canvas()
    x = np.linspace(.35, 8, 400)
    ground = lambda x: 2.35 + .13*np.sin(x*1.4) + .06*np.cos(x*2.7)
    geoid = lambda x: 1.10 + .06*np.sin(x*1.2)
    ellipsoid = lambda x: .56 - .009*(x-4)**2
    for f, color in [(ground, NAVY), (geoid, TEAL), (ellipsoid, ORANGE)]:
        ax.plot(x, f(x), color=color, lw=2.5)
    p = 4.1
    z, g, e = ground(p), geoid(p), ellipsoid(p)
    ax.plot([p, p], [e-.15, z+.15], '--', color=GRAY, lw=1.2)
    ax.plot(p, z, 'o', color=NAVY, ms=5)
    ax.text(p-.3, z+.15, 'P', fontsize=15)
    for height in [e, g, z]:
        ax.plot([p, 6.4], [height, height], ':', color=GRAY, lw=.8)
    double_arrow(ax, 4.45, e, 4.45, g, TEAL)
    double_arrow(ax, 4.45, g, 4.45, z, TEAL)
    double_arrow(ax, 6.35, e, 6.35, z, ORANGE)
    ax.text(4.65, (e+g)/2, '$N$ ジオイド高', va='center', fontsize=12, color=TEAL)
    ax.text(4.65, (z+g)/2, '$H$ 標高', va='center', fontsize=13, color=TEAL)
    ax.text(6.55, 1.6, '$h$ 楕円体高', fontsize=13, color=ORANGE)
    ax.text(.5, 2.65, '地表', fontsize=15)
    ax.text(.5, 1.35, 'ジオイド（平均海面）', fontsize=13, color=TEAL)
    ax.text(.5, .12, '準拠楕円体 GRS80', fontsize=13, color=ORANGE)
    box(ax, 8.5, 1.35, 3.1, .85, 'h = H + N', fs=16)
    ax.text(8.6, .65, '高さの違いを拡大した模式図', fontsize=12, color=GRAY)
    save(fig, 'three_surfaces')


def geodetic_coords():
    fig, ax = canvas(3.4)
    # 楕円体を斜投影。経度140°の点と子午線を同じ投影で描く。
    a, b, cx, cy = 2.0, 1.08, 2.6, 1.65
    def project(lat, lon):
        u, v = np.deg2rad(lat), np.deg2rad(lon-65)
        return cx+a*np.cos(u)*np.cos(v), cy+b*np.sin(u)+.32*np.cos(u)*np.sin(v)
    t = np.linspace(0, 360, 400)
    ax.add_patch(Ellipse((cx, cy), 4, 2.26, facecolor='#f3f7fb', edgecolor=GRAY, lw=1.4))
    ex, ey = project(np.zeros_like(t), t)
    ax.add_patch(Polygon(np.c_[ex, ey], facecolor=TEAL, alpha=.12, edgecolor='none'))
    ax.plot(ex, ey, color=TEAL, lw=1.5)
    lat = np.linspace(-90, 90, 180)
    for lon, color in [(0, ORANGE), (140, NAVY)]:
        ax.plot(*project(lat, lon), color=color, lw=1.7)
    p = project(40, 140)
    q = project(0, 140)
    p0 = project(0, 0)
    ax.plot([cx, p0[0]], [cy, p0[1]], color=ORANGE, lw=1)
    ax.plot([cx, q[0]], [cy, q[1]], color=NAVY, lw=1)
    lon = np.linspace(0, 140, 160)
    lx, ly = project(np.zeros_like(lon), lon)
    ax.plot(cx+.55*(lx-cx), cy+.55*(ly-cy), color=ORANGE, lw=2)
    arrow(ax, cx+.55*(lx[-9]-cx), cy+.55*(ly[-9]-cy),
          cx+.55*(lx[-1]-cx), cy+.55*(ly[-1]-cy), ORANGE)
    ax.plot(*p, 'o', color=NAVY, ms=5)
    ax.text(p[0]+.12, p[1]+.03, 'P', fontsize=12)
    ax.text(.7, .08, 'P：北緯40°・東経140°付近', fontsize=12)
    ax.text(1.2, .95, 'λ = 140°', fontsize=13, color=ORANGE)
    ax.text(.22, 1.05, '赤道面', fontsize=13, color=TEAL)
    ax.text(3.6, .35, '本初子午線', fontsize=13, color=ORANGE)
    ax.text(1.0, 3.04, '楕円体と経度 λ', fontsize=15)
    ax.plot([5.5, 5.5], [.35, 3], color=GRAY, alpha=.25)
    # 子午線断面：楕円の法線を計算し、中心からの動径と混同しない。
    c = np.array([7.5, 1.45])
    aa, bb, phi = 1.65, .92, np.deg2rad(40)
    normal = np.array([np.cos(phi), np.sin(phi)])
    denom = np.hypot(aa*np.cos(phi), bb*np.sin(phi))
    foot = c + np.array([aa*aa*np.cos(phi), bb*bb*np.sin(phi)])/denom
    point = foot + .8*normal
    base = foot - (foot[1]-c[1])/normal[1]*normal
    ax.add_patch(Ellipse(c, 2*aa, 2*bb, facecolor='#f3f7fb', edgecolor=ORANGE, lw=1.8))
    ax.plot([5.8, 10.9], [c[1], c[1]], color=TEAL, lw=1.2)
    ax.plot([base[0], point[0]], [base[1], point[1]], '--', color=GRAY, lw=1.2)
    double_arrow(ax, *foot, *point, NAVY)
    ax.plot(*point, 'o', color=NAVY, ms=5)
    ax.text(point[0]+.08, point[1], 'P', fontsize=14)
    ax.text(9.12, 2.33, '$h$', fontsize=15)
    arc(ax, base, .35, 0, 40, TEAL)
    ax.annotate('φ', xy=(base[0]+.33,1.56), xytext=(9.75,1.75), fontsize=15,
                color=TEAL, arrowprops={'arrowstyle':'-', 'color':TEAL, 'lw':.8})
    ax.text(6.2, 3.04, '子午線断面：緯度 φ と楕円体高 h', fontsize=15)
    ax.text(6.1, .13, 'φ：赤道面と法線の角　 h：法線に沿う高さ', fontsize=12)
    ax.text(10.0, 1.12, '赤道面', fontsize=12, color=TEAL)
    ax.text(10.0, 2.45, '法線', fontsize=12, color=GRAY)
    save(fig, 'geodetic_coords')


def three_norths():
    fig, ax = canvas(3.4)
    o = np.array([3.1, .35])
    # 座標北から真北へ時計回りを正。原点より西の点ではγ > 0。
    # matplotlibは東から反時計回りなので、時計回りの弧は角度を減らす。
    for deg, length, color in [(90, 2.45, NAVY), (74, 2.5, TEAL),
                               (99, 2.5, ORANGE), (25, 2.95, GRAY)]:
        end = o + length*np.array([np.cos(np.deg2rad(deg)), np.sin(np.deg2rad(deg))])
        arrow(ax, *o, *end, color)
    ax.text(3.05, 2.97, '座標北（X）', ha='right', fontsize=13)
    ax.text(3.95, 2.69, '真北', fontsize=13, color=TEAL)
    ax.text(.65, 2.55, '磁北（西偏約9°）', fontsize=12, color=ORANGE)
    ax.text(5.85, 1.62, 'P', fontsize=14, color=GRAY)
    ax.text(2.8, .10, 'O', fontsize=14)
    arc(ax, o, .8, 90, 25, NAVY)
    arc(ax, o, 1.35, 74, 25, TEAL)
    arc(ax, o, 2.1, 90, 74, TEAL)
    ax.text(4.1, .48, '方向角 T', fontsize=12)
    ax.text(4.15, 1.88, '方位角 α', fontsize=12, color=TEAL)
    gamma_mid = o + 2.1*np.array([np.cos(np.deg2rad(82)), np.sin(np.deg2rad(82))])
    ax.annotate('真北方向角 γ（右回りが正）', xy=gamma_mid, xytext=(4.15, 3.08),
                fontsize=12, color=TEAL,
                arrowprops={'arrowstyle': '-', 'color': TEAL,
                            'connectionstyle': 'angle,angleA=180,angleB=82,rad=0'})
    box(ax, 6.45, 1.75, 5.12, 1.0, '方位角 = 方向角 − 真北方向角\nα = T − γ', fs=14)
    ax.text(6.55, 1.13, 'γ は座標北から真北へ右回りを正。\n原点より東で負、西で正',
            fontsize=12, linespacing=1.5)
    ax.text(6.55, .35, 'この図は原点より西の点（γ > 0）の例。\n角度は説明用に拡大',
            fontsize=12, color=GRAY, linespacing=1.5)
    save(fig, 'three_norths')


def jpcs_zones():
    fig, ax = canvas(3.4)
    # 原点値の出典：https://www.gsi.go.jp/LAW/heimencho （2026-10-14確認）
    # READMEのXIII「東経144°」は144°15′に訂正。区域・海岸線ではない模式配置。
    rows = [('I',129.5,33), ('II',131,33), ('III',132+1/6,36),
            ('IV',133.5,33), ('V',134+1/3,36), ('VI',136,36),
            ('VII',137+1/6,36), ('VIII',138.5,36), ('IX',139+5/6,36),
            ('X',140+5/6,40), ('XI',140.25,44), ('XII',142.25,44),
            ('XIII',144.25,44), ('XIV',142,26), ('XV',127.5,26),
            ('XVI',124,26), ('XVII',131,26), ('XVIII',136,20), ('XIX',154,26)]
    xx = lambda lon: .5+(lon-124)*.35
    yy = lambda lat: .40+(lat-20)*.093
    for center, w, h, angle in [((xx(130.2),yy(33)),1.05,.6,0),
                                ((xx(136.9),yy(37.6)),3.75,.55,8),
                                ((xx(133.5),yy(32.7)),.8,.35,0),
                                ((xx(142.3),yy(44)),2.05,.63,0),
                                ((xx(127.6),yy(26)),3.2,.42,0)]:
        ax.add_patch(Ellipse(center,w,h,angle=angle,facecolor=GRAY,alpha=.10,edgecolor='none'))
    for label, lon, lat in rows:
        x, y = xx(lon), yy(lat)
        color = TEAL if label in ['XI','XII','XIII'] else NAVY
        ax.plot(x, y, 'o', ms=4.5, color=color)
        offset = -.28 if label in ['III','VI','VIII'] else .13
        ax.text(x, y+offset, label, ha='center', fontsize=12, color=color)
    for x,y,label in [(1.25,1.62,'九州'),(3.64,1.15,'四国'),(4.3,2.25,'本州'),
                       (5.7,3.03,'北海道'),(.3,1.30,'南西諸島')]:
        ax.text(x,y,label,fontsize=12,color=GRAY)
    ax.annotate('XIII 原点：北緯44°、東経144°15′',
                xy=(xx(144.25),yy(44)),xytext=(7.75,2.15),fontsize=12,color=TEAL,
                arrowprops={'arrowstyle':'-', 'color':TEAL})
    ax.text(7.75,1.60,'XI 道南西 ／ XII 道央 ／ XIII 道東',fontsize=12,color=TEAL)
    ax.text(7.75,.40,'原点の位置を経度順に配置\n区域・海岸線・縮尺は表さない',fontsize=12,color=GRAY,linespacing=1.6)
    save(fig, 'jpcs_zones')


def axes_quadrants():
    fig, ax = canvas(3.4)
    for cx in [2.65,8.7]:
        arrow(ax,cx-2.15,1.6,cx+2.15,1.6,NAVY)
        arrow(ax,cx,.43,cx,2.78,NAVY)
    ax.text(.35,3.02,'数学の座標：x 軸から左回り',fontsize=15)
    ax.text(6.25,3.02,'測量の座標：X 軸から右回り',fontsize=15)
    ax.text(4.85,1.54,'x',fontsize=15)
    ax.text(2.75,2.64,'y',fontsize=15)
    arc(ax,(2.65,1.6),.8,0,65,TEAL)
    ax.text(3.5,2.25,'左回り',fontsize=12,color=TEAL)
    ax.text(8.83,2.66,'X（北）0°',fontsize=12)
    ax.text(10.9,1.52,'Y（東）\n90°',fontsize=12)
    ax.text(6.45,1.48,'270°',fontsize=12,ha='right')
    ax.text(8.5,.14,'180°',fontsize=12)
    arc(ax,(8.7,1.6),.62,90,20,ORANGE)
    for x,y,text in [(9.8,2.25,'第1象限 (+,+)'),(9.8,.65,'第2象限 (−,+)'),
                     (7.15,.65,'第3象限 (−,−)'),(7.15,2.25,'第4象限 (+,−)')]:
        ax.text(x,y,text,fontsize=12,ha='center')
    ax.text(.5,.16,'軸の名前と角度を測る向きが異なる',fontsize=13,color=GRAY)
    save(fig, 'axes_quadrants')


def scale_factor():
    fig, ax = plt.subplots(figsize=(12,3.4))
    fig.subplots_adjust(left=.115,right=.71,bottom=.23,top=.90)
    y=np.linspace(-180,180,1001)
    factor=lambda v: .9999*(1+np.asarray(v)**2/(2*6370**2))
    ax.plot(y,factor(y),color=NAVY,lw=2.2)
    ax.axhline(1,color=GRAY,ls='--',lw=1)
    for value in [-130,130]:
        ax.axvline(value,color=GRAY,ls='--',lw=1)
    for value in [-130,-90,0,90,130]:
        ax.plot(value,factor(value),'o',color=TEAL if abs(value)==90 else ORANGE,ms=4)
    ax.set(xlim=(-180,180),ylim=(.9998,1.0002),xticks=[-180,-130,-90,0,90,130,180],
           yticks=[.9998,.9999,1,1.0001,1.0002],xlabel='Y（km）',ylabel='縮尺係数 m')
    ax.ticklabel_format(axis='y',style='plain',useOffset=False)
    ax.tick_params(labelsize=12)
    ax.grid(alpha=.12)
    ax.text(0,.99983,'適用範囲 ±130 km',ha='center',fontsize=12,color=GRAY)
    fig.text(.74,.78,'Y = 0：0.9999',fontsize=14,color=NAVY)
    fig.text(.74,.61,'Y = ±90 km：≈ 1.0000',fontsize=12,color=TEAL)
    fig.text(.74,.44,'Y = ±130 km：≈ 1.0001',fontsize=12,color=ORANGE)
    fig.text(.74,.23,'R = 6370 km\n注記は小数第4位に丸めた値。',fontsize=12,color=GRAY,linespacing=1.7)
    fig.text(.12,.94,'m = 0.9999(1 + Y²/(2R²))',fontsize=14,color=NAVY)
    save(fig,'scale_factor')


def distance_stages():
    fig,ax=canvas(3.2)
    positions=[(.1,1.9),(3.1,1.4),(6.1,.9),(9.1,.4)]
    labels=['斜距離 $L$','水平距離 $S$','基準面上の距離\n$S_0$','平面直角座標上の\n距離 $s$']
    values=['1000.049 m','1000.000 m','999.984 m','999.884 m']
    for (x,y),label,value in zip(positions,labels,values):
        box(ax,x,y,2.65,.73,label,fs=13)
        ax.text(x+1.325,y-.25,value,ha='center',fontsize=13,color=TEAL)
    for i,label in enumerate(['高度角で換算','標高補正\n×R/(R+H)','縮尺係数 ×m']):
        x,y=positions[i]
        nx,ny=positions[i+1]
        arrow(ax,x+2.70,y+.37,nx-.06,ny+.37)
        ax.text(nx+.25,y+1.02 if i==0 else y+.98,label,ha='center',fontsize=12,color=GRAY,
                va='top',linespacing=1.4)
    save(fig,'distance_stages')


def elevation_reduction():
    fig,ax=canvas(3.4)
    center=(2.9,.32)
    for radius,color in [(2.12,ORANGE),(2.75,NAVY)]:
        arc(ax,center,radius,51,129,color,head=False)
    for deg in [51,129]:
        end=np.array(center)+2.75*np.array([np.cos(np.deg2rad(deg)),np.sin(np.deg2rad(deg))])
        ax.plot([center[0],end[0]],[center[1],end[1]],color=GRAY,lw=1.4)
    ax.plot(*center,'o',ms=4,color=GRAY)
    ax.text(2.35,.04,'中心',fontsize=12,color=GRAY)
    ax.text(2.85,3.14,'$S$',fontsize=15)
    ax.text(2.83,2.12,'$S_0$',fontsize=15,color=ORANGE)
    ax.text(1.06,1.33,'R + H',fontsize=13)
    ax.text(3.95,1.27,'R',fontsize=13,color=ORANGE)
    ax.text(5.0,2.77,'標高 H の地表',fontsize=14)
    ax.text(5.0,2.19,'基準面（楕円体面）',fontsize=14,color=ORANGE)
    ax.plot([4.0,4.8],[2.85,2.85],color=NAVY,lw=1)
    ax.plot([3.8,4.8],[2.24,2.24],color=ORANGE,lw=1)
    box(ax,7.8,1.55,3.7,.78,'S₀ = S·R/(R+H)',fs=16)
    ax.text(5.0,.92,'高い所で測った距離は基準面では短くなる',fontsize=14,color=TEAL)
    ax.text(5.0,.35,'球面近似の模式図（高さを拡大）\nここでは H を基準面からの高さとみなす。',fontsize=12,color=GRAY,linespacing=1.5)
    save(fig,'elevation_reduction')


def forward_calc():
    fig,ax=canvas(3.4)
    a=np.array([2.75,2.17])
    b=a+2.8*np.array([np.sin(np.deg2rad(120)),np.cos(np.deg2rad(120))])
    arrow(ax,.9,.35,.9,2.87,NAVY)
    arrow(ax,.9,.35,6.15,.35,NAVY)
    ax.text(.3,2.95,'X（北）',fontsize=12)
    ax.text(6.2,.30,'Y（東）',fontsize=12)
    arrow(ax,*a,a[0],3.12,TEAL)
    ax.text(2.94,2.99,'座標北',fontsize=12,color=TEAL)
    ax.plot([a[0],b[0]],[a[1],b[1]],color=NAVY,lw=2.5)
    ax.plot([a[0],a[0],b[0]],[a[1],b[1],b[1]],'--',color=GRAY,lw=1.3)
    ax.plot([a[0]+.16,a[0]+.16,a[0]],[b[1],b[1]+.16,b[1]+.16],color=GRAY,lw=1)
    ax.plot(*a,'o',color=NAVY,ms=5)
    ax.plot(*b,'o',color=NAVY,ms=5)
    ax.text(a[0]-.75,a[1]+.08,'既知点 A',fontsize=12)
    ax.text(b[0]+.10,b[1]-.02,'新点 B',fontsize=12)
    arc(ax,a,.60,90,-30,ORANGE)
    ax.text(3.55,2.53,'T = 120°',fontsize=13,color=ORANGE)
    ax.text(4.15,1.59,'$S$',fontsize=15)
    ax.text(2.51,1.36,'ΔX = S cos T\n（緯距）',ha='right',fontsize=12,color=GRAY,linespacing=1.5)
    ax.text(4.0,.49,'ΔY = S sin T（経距）',ha='center',fontsize=12,color=GRAY)
    # 日本語は既存フォント、数式は専用フォントに分けて添字とΔを描画する。
    with plt.rc_context({'mathtext.fontset': 'dejavusans'}):
        box(ax,7.15,1.63,4.4,1.05,
            r'$X_B = X_A + \Delta X$'+'\n'+r'$Y_B = Y_A + \Delta Y$',fs=15)
    ax.text(7.3,1.05,'B は A の南東にある',fontsize=14,color=TEAL)
    ax.text(7.3,.48,'ΔX < 0　／　ΔY > 0',fontsize=14,color=TEAL)
    save(fig,'forward_calc')


def inverse_quadrant():
    fig,ax=canvas(3.4)
    arrow(ax,.2,1.65,5.8,1.65,NAVY)
    arrow(ax,3,.35,3,2.92,NAVY)
    ax.text(3.1,2.94,'X',fontsize=14)
    ax.text(5.85,1.58,'Y',fontsize=14)
    items=[(4.45,2.42,'第1象限','ΔX > 0, ΔY > 0','そのまま'),
           (4.45,.84,'第2象限','ΔX < 0, ΔY > 0','+180°'),
           (1.45,.84,'第3象限','ΔX < 0, ΔY < 0','+180°'),
           (1.45,2.42,'第4象限','ΔX > 0, ΔY < 0','+360°')]
    for x,y,title,signs,add in items:
        ax.text(x,y,f'{title}\n{signs}\n{add}',ha='center',va='center',fontsize=12,linespacing=1.5)
    ax.text(6.38,3.02,'arctan(ΔY/ΔX) に加える角',fontsize=15)
    table=ax.table(cellText=[['第1','＋','＋','そのまま'],['第2','−','＋','+180°'],
                             ['第3','−','−','+180°'],['第4','＋','−','+360°']],
                   colLabels=['象限','ΔX','ΔY','加える角'],
                   colWidths=[.20,.21,.21,.38],bbox=[.54,.24,.43,.59],cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    for (r,c),cell in table.get_celld().items():
        cell.set_edgecolor('#d9e0e6')
        cell.set_text_props(color=NAVY)
        if r==0:
            cell.set_facecolor('#f3f7fb')
    ax.text(6.5,.37,'方向角は 0°以上360°未満にそろえる。',fontsize=12,color=GRAY)
    ax.text(6.5,.05,'軸上は別判定。同一点では方向角は定まらない。',fontsize=12,color=GRAY)
    save(fig,'inverse_quadrant')


def main():
    FIG.mkdir(parents=True,exist_ok=True)
    QA.mkdir(parents=True,exist_ok=True)
    readme=FIG/'README.md'
    before=hashlib.sha256(readme.read_bytes()).hexdigest()
    for draw in [three_surfaces,geodetic_coords,three_norths,jpcs_zones,axes_quadrants,
                 scale_factor,distance_stages,elevation_reduction,forward_calc,inverse_quadrant]:
        draw()
    assert hashlib.sha256(readme.read_bytes()).hexdigest()==before
    (QA/'validation.json').write_text(json.dumps({'README_SHA256':before,
                                               '真北方向角': '座標北から真北へ右回り正。東で負、西で正。α = T − γ',
                                               '正算式の数式フォント': 'DejaVu Sans（mathtext）',
                                               '検査結果':CHECKS},
                                               ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # 点検用一覧画像もSurveying配下に残す。正本PNGのサイズは変えない。
    sheet=Image.new('RGB',(1440,5*235),'white')
    draw=ImageDraw.Draw(sheet)
    for i,entry in enumerate(CHECKS):
        x,y=(i%2)*720,(i//2)*235
        with Image.open(FIG/(entry['図']+'.png')) as im:
            preview=im.convert('RGB')
            preview.thumbnail((720,204),Image.Resampling.LANCZOS)
            sheet.paste(preview,(x,y+24))
        draw.text((x+12,y+5),entry['図'],fill=NAVY)
    sheet.save(QA/'contact_sheet.png')
    print(f'{len(CHECKS)}点のSVG・PNGを保存。フォント: {FONT}。サイズ・余白・文字の画面内配置を確認。')


if __name__=='__main__':
    main()
