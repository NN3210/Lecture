"""第05回「トラバース測量 I」の例題・確認問題・演習の数値を検算する（標準ライブラリのみ）。"""

import math
import sys


def dms2deg(d, m=0, s=0):
    """度分秒を十進の度にする。"""
    return d + m / 60 + s / 3600


def dms(deg, sec_digits=0, wrap=True):
    """十進の度を 度°分′秒″ の文字列にする（wrap=True なら 0〜360° に整える）。"""
    if wrap:
        deg %= 360.0
    deg = round(deg * 3600, 6) / 3600
    d = int(deg)
    m = int((deg - d) * 60)
    s = (deg - d - m / 60) * 3600
    if round(s, sec_digits) >= 60:
        s = 0.0
        m += 1
    if m >= 60:
        m = 0
        d += 1
    width = 2 + sec_digits + (1 if sec_digits else 0)
    return f"{d}°{m:02d}′{s:0{width}.{sec_digits}f}″"


def signed_dms(deg):
    sign = "−" if deg < 0 else "+"
    return sign + dms(abs(deg))


def forward(xa, ya, t_deg, s):
    """順計算：既知点 (xa, ya) から方向角 t_deg・距離 s の新点。"""
    t = math.radians(t_deg)
    return xa + s * math.cos(t), ya + s * math.sin(t)


def inverse(xa, ya, xb, yb):
    """逆計算：距離と方向角（0〜360°）。象限判定は atan2 で行う。"""
    dx, dy = xb - xa, yb - ya
    s = math.hypot(dx, dy)
    t = math.degrees(math.atan2(dy, dx)) % 360.0
    return s, t, dx, dy


def propagate(t_start, betas):
    """交角法：T_{i+1} = T_i + β ± 180°。betas は 2 番目の測点から順に与える。"""
    ts = [t_start]
    for b in betas:
        ts.append((ts[-1] + b - 180.0) % 360.0)
    return ts


def traverse(name, t_ab, obs, S, pts):
    """閉合トラバースの調整・方向角・緯距経距をまとめて検算する。"""
    n = len(obs)
    theory = (n - 2) * 180.0
    total = sum(obs)
    err = (total - theory) * 3600
    corr = -err / n
    adj = [b + corr / 3600 for b in obs]
    print(f"【{name}】n = {n}、理論値 {theory:.0f}°")
    print(f"  観測内角の和 = {dms(total, wrap=False)}、測角誤差 ε = {err:+.1f}″、配分 = {corr:+.1f}″/角")
    for p, o, a in zip(pts, obs, adj):
        print(f"    {p}: 観測 {dms(o)} → 調整 {dms(a)}")
    print(f"  調整角の和 = {dms(sum(adj), wrap=False)}")
    # 方向角（B 以降の調整角を順に使い、最後に A の調整角で AB に戻す）
    ts = propagate(t_ab, adj[1:] + adj[:1])
    lines = [pts[i] + pts[(i + 1) % n] for i in range(n)]
    for i in range(n):
        prev = ts[i]
        beta = adj[(i + 1) % n]
        raw = prev + beta
        sign = "−180°" if raw >= 180 else "+180°"
        t_next = ts[i + 1]
        print(f"    {lines[(i + 1) % n]}: {dms(prev)} + {dms(beta)} = {dms(raw, wrap=False)} → {sign} → {dms(t_next)}")
    print(f"  一周して AB = {dms(ts[-1])}（既知 {dms(t_ab)}）→ {'一致' if abs((ts[-1] - t_ab + 180) % 360 - 180) < 1e-6 else '不一致'}")
    unadj = propagate(t_ab, obs[1:] + obs[:1])
    print(f"  （調整前の角で一周すると AB = {dms(unadj[-1])}、ずれ {((unadj[-1] - t_ab + 180) % 360 - 180) * 3600:+.0f}″）")
    sx = sy = 0.0
    print("  測線    S(m)      T            ΔX(m)      ΔY(m)")
    for i in range(n):
        t = ts[i]
        dx = S[i] * math.cos(math.radians(t))
        dy = S[i] * math.sin(math.radians(t))
        sx += round(dx, 3)
        sy += round(dy, 3)
        print(f"    {lines[i]}  {S[i]:8.3f}  {dms(t)}  {dx:+9.3f}  {dy:+9.3f}   cos={math.cos(math.radians(t)):+.6f} sin={math.sin(math.radians(t)):+.6f}")
    print(f"    合計 {sum(S):8.3f}                ΣΔX={sx:+.3f}  ΣΔY={sy:+.3f}  閉合差={math.hypot(sx, sy) * 1000:.1f} mm")
    deltas = [a - 180.0 for a in adj]
    print("  偏角 δ = β − 180°: " + "、".join(f"{p}: {signed_dms(d)}" for p, d in zip(pts, deltas)) + f"、和 = {sum(deltas):+.4f}°")
    print()
    return adj, ts


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    print("【5-2 許容範囲 σ√n】")
    for sig in (20, 30):
        print(f"  σ = {sig}″ → " + "、".join(f"n={n}: {sig * math.sqrt(n):.0f}″" for n in (4, 5, 10)))
    print()

    traverse("5-2〜5-4 講義例題（4 点）", dms2deg(62, 30, 0),
             [dms2deg(92, 10, 20), dms2deg(85, 40, 30), dms2deg(98, 20, 10), dms2deg(83, 49, 40)],
             [120.000, 95.000, 117.015, 102.977], "ABCD")

    print("【5-2 結合トラバースの測角誤差】")
    t_start = 40.0
    betas = [dms2deg(200, 10, 10), dms2deg(160, 20, 20), dms2deg(190, 30, 30)]
    t_calc = (t_start + sum(betas) - 3 * 180) % 360
    t_end = dms2deg(51, 0, 30)
    print(f"  Σβ = {dms(sum(betas), wrap=False)}、T_end(計算) = {dms(t_calc)}、既知 {dms(t_end)}、ε = {(t_calc - t_end) * 3600:+.0f}″ → 各角 {-(t_calc - t_end) * 3600 / 3:+.0f}″")
    print()

    print("【5-2 ここまでの確認②】")
    obs_sum = dms2deg(539, 59, 20)
    print(f"  5 点、観測和 {dms(obs_sum, wrap=False)} → ε = {(obs_sum - 540) * 3600:+.0f}″、各角 {-(obs_sum - 540) * 3600 / 5:+.0f}″、許容 20″×√5 = {20 * math.sqrt(5):.1f}″")
    print()

    print("【5-3 士補の型（電卓なし）】")
    ts = propagate(dms2deg(330, 20, 10), [dms2deg(95, 30, 40), dms2deg(210, 15, 20)])
    print(f"  T_AB = {dms(ts[0])} → T_BC = {dms(ts[1])} → T_CD = {dms(ts[2])}")
    print("【5-3 ここまでの確認③】")
    print(f"  200° + 100° → {dms(propagate(200, [100])[1])}、30° + 120° → {dms(propagate(30, [120])[1])}、β = 250° → δ = {250 - 180:+}°")
    print()

    print("【5-4 関数表で解く 150°】")
    print(f"  S = 200.00、T = 150° → ΔX = {200 * math.cos(math.radians(150)):+.2f}、ΔY = {200 * math.sin(math.radians(150)):+.2f}")
    print("【5-4 ここまでの確認④】")
    print(f"  S = 100、T = 270° → ΔX = {100 * math.cos(math.radians(270)):+.3f}、ΔY = {100 * math.sin(math.radians(270)):+.3f}")
    print()

    print("【5-5 4 象限の例】")
    for dx, dy in [(300, 400), (-300, 400), (-300, -400), (300, -400)]:
        s, t, _, _ = inverse(0, 0, dx, dy)
        print(f"  ΔX = {dx:+}、ΔY = {dy:+} → S = {s:.3f}、arctan = {signed_dms(math.degrees(math.atan(dy / dx)))}、T = {dms(t)}")
    print("【5-5 ここまでの確認⑤】")
    for (xa, ya, xb, yb) in [(100, 100, 100, 300), (0, 0, -50, 50), (0, 0, 50, -50)]:
        s, t, dx, dy = inverse(xa, ya, xb, yb)
        print(f"  ΔX = {dx:+.0f}、ΔY = {dy:+.0f} → S = {s:.3f}、T = {dms(t)}")
    print()

    print("【5-6 後視誤差の影響】")
    for sec in (60, 3600):
        print(f"  S = 100 m、δ = {sec}″ → ずれ ≈ {100 * sec / 206264.806:.3f} m")
    print()

    adj, ts = traverse("演習 問1（5 点）", dms2deg(115, 20, 30),
                       [dms2deg(100, 12, 12), dms2deg(118, 35, 52), dms2deg(95, 48, 32), dms2deg(128, 10, 42), dms2deg(97, 13, 42)],
                       [85.000, 110.000, 96.000, 84.894, 127.412], "ABCDE")

    print("【演習 問2】")
    xp, yp, xq, yq = 1500.000, 2300.000, 1580.000, 2150.000
    s, t, dx, dy = inverse(xp, yp, xq, yq)
    print(f"  ΔX = {dx:+.3f}、ΔY = {dy:+.3f}、S = {s:.3f} m")
    print(f"  arctan(ΔY/ΔX) = {signed_dms(math.degrees(math.atan(dy / dx)))} → +360° → T_PQ = {dms(t)}（{t:.5f}°）、T_QP = {dms(t - 180)}")
    xb, yb = forward(xp, yp, t, s)
    print(f"  検算：順計算で Q = ({xb:.3f}, {yb:.3f})")


if __name__ == "__main__":
    main()
