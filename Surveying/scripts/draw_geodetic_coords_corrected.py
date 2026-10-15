"""緯度・経度・楕円体高を、楕円の式に基づいて新規作図する。"""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, Ellipse, FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'materials/slides/第03回_測量の座標/diagrams'
NOTES = ROOT / 'notes/geodetic_coords_correction_20261015'
OUT.mkdir(parents=True, exist_ok=True)
NOTES.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'font.family': 'Meiryo', 'svg.fonttype': 'path', 'axes.unicode_minus': False})
NAVY, TEAL, ORANGE, GRAY = '#183e53', '#008b80', '#c55228', '#647582'
BG, FILL = '#faf9f6', '#edf4f8'
fig = plt.figure(figsize=(16, 9), facecolor=BG)

def text(x, y, s, size=17, color=NAVY, weight='normal', **kw):
    return fig.text(x, y, s, fontsize=size, color=color, fontweight=weight, **kw)

def line(ax, p, q, color=NAVY, lw=1.8, **kw):
    ax.plot([p[0], q[0]], [p[1], q[1]], color=color, lw=lw, **kw)

def point(ax, p, name, offset, color=NAVY):
    ax.scatter(*p, s=44, color=color, zorder=8)
    ax.text(*(p + np.array(offset)), name, fontsize=16, color=color, fontweight='bold', zorder=9)

text(.035, .925, '緯度・経度・楕円体高', 32, weight='bold')
text(.042, .828, '緯度  φ', 19, TEAL, 'bold')
text(.180, .828, '赤道面と、楕円体面の法線がなす角。', 19)
text(.042, .762, '経度  λ', 19, NAVY, 'bold')
text(.180, .762, '本初子午線面と、その地点の子午線面がなす角。', 19)
text(.042, .696, '楕円体高  h', 19, ORANGE, 'bold')
text(.180, .696, '楕円体面から地表の点Pまで、法線に沿って測る高さ。', 19)
for x, w in [(.03, .435), (.485, .485)]:
    fig.add_artist(FancyBboxPatch((x, .166), w, .474, transform=fig.transFigure,
        boxstyle='round,pad=0.008,rounding_size=0.012', facecolor='white', edgecolor='none', zorder=-1))
text(.055, .596, '経度 λ｜北極側から見た赤道面', 18, weight='bold')
text(.510, .596, '緯度 φ・楕円体高 h｜子午線断面', 18, weight='bold')

# 左：北極側からの正射影。東経140度は反時計回りの鈍角。
left = fig.add_axes([.045, .219, .405, .355])
left.set_aspect('equal')
left.set_xlim(-1.48, 1.65)
left.set_ylim(-1.12, 1.25)
left.axis('off')
left.add_patch(Circle((0, 0), 1, facecolor='#e4f2f0', edgecolor=TEAL, lw=2))
O = np.array([0., 0.])
lam = np.deg2rad(140.)
A = np.array([np.cos(lam), np.sin(lam)])
line(left, O, np.array([1., 0.]))
line(left, O, A)
point(left, O, 'O', (-.07, -.18))
point(left, A, 'A', (-.14, .03))
left.scatter(1, 0, s=35, color=NAVY, zorder=8)
tt = np.linspace(0, lam, 160)
rr = .48
left.plot(rr*np.cos(tt), rr*np.sin(tt), color=ORANGE, lw=2.2)
left.add_patch(FancyArrowPatch((rr*np.cos(lam-.09), rr*np.sin(lam-.09)),
    (rr*np.cos(lam), rr*np.sin(lam)), arrowstyle='-|>', mutation_scale=14, color=ORANGE, lw=1.8))
left.text(.08, .48, 'λ＝東経140°', fontsize=15, color=ORANGE)
left.text(1.12, -.05, '本初子午線面\nの方向（0°）', fontsize=12, color=NAVY, va='center')
left.annotate('A：地点の子午線と\n赤道の交点', xy=A, xytext=(-1.40, 1.02), fontsize=12,
    color=NAVY, arrowprops={'arrowstyle':'-', 'color':GRAY, 'lw':1.1}, ha='left', va='center')
text(.065, .183, '北極側から見ると、東経は反時計回り。', 13, TEAL)

# 右：回転楕円体の子午線断面。Qは楕円上、nはその勾配と平行。
ax = fig.add_axes([.500, .217, .455, .357])
ax.set_aspect('equal')
ax.set_xlim(-1.82, 2.78)
ax.set_ylim(-1.16, 1.54)
ax.axis('off')
a, b = 1.60, 1.05
phi = np.deg2rad(40.)
e2 = 1 - b*b/(a*a)
N = a / np.sqrt(1 - e2*np.sin(phi)**2)
Q = np.array([N*np.cos(phi), N*(1-e2)*np.sin(phi)])
n = np.array([np.cos(phi), np.sin(phi)])
t = np.array([np.sin(phi), -np.cos(phi)])
h = .58
P = Q + h*n
B = Q - Q[1]/n[1]*n
ax.add_patch(Ellipse(O, 2*a, 2*b, facecolor=FILL, edgecolor=ORANGE, lw=2.0))
line(ax, np.array([-1.70, 0.]), np.array([2.68, 0.]), TEAL, 1.5)
ax.text(2.22, -.20, '赤道面', fontsize=13, color=TEAL)
line(ax, np.array([0., -1.08]), np.array([0., 1.29]), GRAY, 1.2, ls=(0, (4, 3)))
ax.text(-.18, 1.35, '回転軸', fontsize=12, color=GRAY)
line(ax, B, Q, GRAY, 1.5, ls=(0, (4, 3)))
line(ax, Q, P+.22*n, NAVY, 2.0)
point(ax, O, 'O', (-.20, -.22))
point(ax, B, 'B', (-.02, -.22))
point(ax, Q, 'Q', (-.15, -.24), ORANGE)
point(ax, P, 'P', (.18, -.24))
arc_r = .27
ax.add_patch(Arc(B, 2*arc_r, 2*arc_r, theta1=0, theta2=np.rad2deg(phi), color=TEAL, lw=1.8))
ax.text(B[0]+.34, .075, 'φ', fontsize=18, color=TEAL)
# 接線と法線は内積0。右角の小さな印も同じベクトルから構成。
line(ax, Q-.20*t, Q+.28*t, GRAY, 1.2)
s = .085
corner = np.array([Q+s*n, Q+s*(n+t), Q+s*t])
ax.plot(corner[:, 0], corner[:, 1], color=GRAY, lw=1.1)
# 高さの寸法線はQPに平行で、補助線の端をQ・Pに合わせる。
d = .24
line(ax, Q, Q+(d+.05)*t, GRAY, .8)
line(ax, P, P+(d+.05)*t, GRAY, .8)
ax.add_patch(FancyArrowPatch(Q+d*t, P+d*t, arrowstyle='<->', color=NAVY,
    mutation_scale=13, lw=1.6))
hp = (P+Q)/2 + (d+.15)*t
ax.text(*hp, 'h', fontsize=19, color=NAVY, ha='center', va='center', fontstyle='italic')
xx = np.linspace(1.19, 2.68, 300)
zz = P[1] + .038*np.sin(7*(xx-P[0])) - .065*(xx-P[0])
ax.plot(xx, zz, color=NAVY, lw=2.2)
ax.text(2.35, P[1]+.13, '地表', fontsize=13, color=NAVY)
ax.annotate('楕円体面の法線', xy=P+.17*n, xytext=(1.13, 1.37), fontsize=12,
    color=NAVY, arrowprops={'arrowstyle':'-', 'color':GRAY, 'lw':1.0})
ax.text(-1.08, -.56, '基準楕円体', fontsize=14, color=ORANGE)
text(.520, .183, 'Q：楕円体面上の点　　P：地表の点', 13)

fig.add_artist(FancyBboxPatch((.035, .072), .930, .063, transform=fig.transFigure,
    boxstyle='round,pad=0.005,rounding_size=0.012', facecolor='#e4f2f0', edgecolor='none', zorder=-1))
text(.052, .094, 'Pが基準楕円体の外側にあるのは、地表と基準楕円体が一致しないため。', 17, TEAL, 'bold')
text(.045, .031, '模式図：扁平率・起伏・高さを強調。h＝0ならPとQは一致する。', 11, GRAY)
text(.955, .031, '定義の確認：国土地理院「日本の測地系」', 9, GRAY, ha='right')

# 検算：図を構成する幾何学的な関係を直接調べる。
gradient = np.array([Q[0]/a**2, Q[1]/b**2])
checks = {
    '楕円上のQ_残差': float(np.sum((Q/np.array([a,b]))**2)-1),
    '法線と接線の内積': float(n@t),
    '楕円勾配と法線の平行性_外積': float(gradient[0]*n[1]-gradient[1]*n[0]),
    'BQPの直線性_外積': float((Q-B)[0]*(P-Q)[1]-(Q-B)[1]*(P-Q)[0]),
    'Bの赤道面からの距離': float(B[1]),
    '法線の角度_度': float(np.rad2deg(np.arctan2(n[1],n[0]))),
    'QPの長さ': float(np.linalg.norm(P-Q)),
    '指定したh': h,
    '東経の角度_度': float(np.rad2deg(np.arctan2(A[1],A[0]))),
    '地表曲線とPの高さの差': float(P[1]+.038*np.sin(0)-.065*0-P[1]),
}
assert all(abs(checks[k]) < 1e-12 for k in list(checks)[:5])
assert abs(checks['法線の角度_度']-40) < 1e-12
assert abs(checks['QPの長さ']-h) < 1e-12
assert abs(checks['東経の角度_度']-140) < 1e-12
assert abs(checks['地表曲線とPの高さの差']) < 1e-12
for suffix in ['svg', 'jpg']:
    kwargs = {'pil_kwargs': {'quality': 97, 'subsampling': 0}} if suffix == 'jpg' else {}
    fig.savefig(OUT/f'geodetic_coords_corrected.{suffix}', dpi=200, facecolor=BG, **kwargs)
    if suffix == 'svg':
        svg_path = OUT/'geodetic_coords_corrected.svg'
        svg_path.write_text('\n'.join(s.rstrip() for s in svg_path.read_text(encoding='utf-8').splitlines())+'\n', encoding='utf-8')
plt.close(fig)
(NOTES/'幾何検算.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(checks, ensure_ascii=False, indent=2))
print(OUT/'geodetic_coords_corrected.jpg')
