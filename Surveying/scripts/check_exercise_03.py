"""第03回「測量の座標」の小テスト・例題・演習の数値を検算する（標準ライブラリのみ）。"""

import math
import sys

R = 6370000.0  # 地球の半径（m）。測量士補試験で与えられる概数
M0 = 0.9999    # 平面直角座標系の原点の縮尺係数


def dms(deg):
    """十進の度を 度°分′秒″ の文字列にする（秒は小数第1位まで）。"""
    sign = "-" if deg < 0 else ""
    deg = abs(deg)
    d = int(deg)
    m = int((deg - d) * 60)
    s = (deg - d - m / 60) * 3600
    if round(s, 1) >= 60:
        s = 0.0
        m += 1
    if m >= 60:
        m = 0
        d += 1
    return f"{sign}{d}°{m:02d}′{s:04.1f}″"


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


def reduce_distance(L, dh, H, m=M0):
    """斜距離 L → 水平距離 S → 基準面距離 S0 → 平面距離 s。"""
    S = math.sqrt(L * L - dh * dh)
    S0 = S * R / (R + H)
    s = m * S0
    return S, S0, s


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    print("【小テスト（第2回範囲、測量士補形式）】")
    obs = [50.003, 50.005, 50.006, 50.008, 50.008]
    mean = sum(obs) / len(obs)
    v = [round((x - mean) * 1000) for x in obs]
    print(f"問2 最確値 = {mean:.3f} m、残差（mm）= {v}、残差和 = {sum(v)}")
    n, sv2 = 4, 27
    sigma = math.sqrt(sv2 / (n - 1))
    print(f"問3 σ = √({sv2}/{n - 1}) = {sigma:.2f} mm、σ_x̄ = σ/√{n} = {sigma / math.sqrt(n):.2f} mm")
    h1, l1, h2, l2 = 10.012, 2.0, 10.018, 4.0
    w1, w2 = 1 / l1, 1 / l2
    hw = (w1 * h1 + w2 * h2) / (w1 + w2)
    print(f"問4 重み = {w1 / w2:.0f}:1、最確値 = {hw:.3f} m")
    print(f"問5 ±(2 mm + 2 ppm) × 1 km → {2 + 2 * 1:.0f} mm")
    print()

    print("【講義 3-1 例題】")
    h, N = 85.000, 35.000
    print(f"楕円体高 h = {h:.3f} m、ジオイド高 N = {N:.3f} m → 標高 H = {h - N:.3f} m")
    print(f"確認①：h = 50.0、N = 35.0 → H = {50.0 - 35.0:.1f} m")
    print()

    print("【講義 3-2 例題】")
    Y = 50000.0
    m = M0 * (1 + Y * Y / (2 * R * R))
    print(f"縮尺係数 Y = {Y / 1000:.0f} km → m = {m:.5f}")
    for Yk in (0, 90, 130):
        Yv = Yk * 1000.0
        print(f"  Y = {Yk:>3d} km → m = {M0 * (1 + Yv * Yv / (2 * R * R)):.5f}")
    L, dh, H = 1000.049, 9.900, 100.0
    S, S0, s = reduce_distance(L, dh, H)
    print(f"L = {L:.3f} m、Δh = {dh:.3f} m、H = {H:.0f} m → S = {S:.3f} m、S0 = {S0:.3f} m、s = {s:.3f} m")
    print(f"標高補正量 S − S0 = {S - S0:.3f} m、縮尺係数補正量 s − S0 = {s - S0:.3f} m")
    print(f"確認②：S = 2000 m、H = 500 m → 補正量 = {2000 * 500 / R:.3f} m")
    print()

    print("【講義 3-3 例題】")
    xa, ya, T, S = 1000.000, 2000.000, 120.0, 150.000
    xb, yb = forward(xa, ya, T, S)
    print(f"順計算 A({xa:.3f}, {ya:.3f})、T = {T:.0f}°、S = {S:.3f} m → B({xb:.3f}, {yb:.3f})")
    s_, t_, dx, dy = inverse(xa, ya, round(xb, 3), round(yb, 3))
    print(f"逆計算 ΔX = {dx:.3f}、ΔY = {dy:.3f} → S = {s_:.3f} m、T = {t_:.4f}° = {dms(t_)}")
    print(f"  arctan(ΔY/ΔX) = {math.degrees(math.atan(dy / dx)):.1f}° → +180° → {t_:.1f}°")
    xa2, ya2, T2, S2 = 150.00, 250.00, 60.0, 200.00
    xb2 = xa2 + S2 * 0.5
    yb2 = ya2 + S2 * 0.86603
    print(f"士補形式 A({xa2:.2f}, {ya2:.2f})、T = {T2:.0f}°、S = {S2:.2f} m、cos60° = 0.5、sin60° = 0.86603 → B({xb2:.2f}, {yb2:.2f})")
    print(f"確認③：ΔX = −100、ΔY = −100 → T = {math.degrees(math.atan2(-100, -100)) % 360:.0f}°")
    print()

    print("【演習 問1】")
    xa, ya, xb, yb = 1200.000, 800.000, 1050.000, 600.000
    s_, t_, dx, dy = inverse(xa, ya, xb, yb)
    print(f"(1) 逆計算 A({xa:.3f}, {ya:.3f}) → B({xb:.3f}, {yb:.3f})：ΔX = {dx:.3f}、ΔY = {dy:.3f}")
    print(f"    S_AB = {s_:.3f} m、arctan(ΔY/ΔX) = {math.degrees(math.atan(dy / dx)):.4f}°、T_AB = {t_:.4f}° = {dms(t_)}")
    T3, S3 = 30.0, 200.000
    xc, yc = forward(xa, ya, T3, S3)
    print(f"(2) 順計算 A から T = {T3:.0f}°00′00″、S = {S3:.3f} m → C({xc:.3f}, {yc:.3f})")
    print(f"    ΔX = {S3 * math.cos(math.radians(T3)):.3f}、ΔY = {S3 * math.sin(math.radians(T3)):.3f}")
    sc, tc, _, _ = inverse(xa, ya, round(xc, 3), round(yc, 3))
    print(f"    検算：逆計算で S = {sc:.3f} m、T = {dms(tc)}")
    print()

    print("【演習 問2】")
    L, dh, H = 500.020, 4.500, 200.0
    S, S0, s = reduce_distance(L, dh, H)
    print(f"(1) L = {L:.3f} m、Δh = {dh:.3f} m → S = {S:.4f} → {S:.3f} m")
    print(f"(2) H = {H:.0f} m → S0 = S × R/(R+H) = {S0:.4f} → {S0:.3f} m（補正量 {S0 - S:+.3f} m）")
    print(f"(3) m = {M0} → s = {s:.4f} → {s:.3f} m（補正量 {s - S0:+.3f} m）")
    s_design = 300.000
    S_field = s_design / M0 * (R + H) / R
    print(f"(4) 設計の平面距離 s = {s_design:.3f} m を現地の水平距離に戻す → S = {S_field:.4f} → {S_field:.3f} m")


if __name__ == "__main__":
    main()
