"""第02回の例題・演習を整数 mm と有理数で検算する（標準ライブラリのみ）。"""

from fractions import Fraction
from math import sqrt
import sys


def 検算(名称, 観測値_mm, 重み=None):
    """群平均を入力する場合、観測数は元の回数ではなく群の数とする。"""
    個数 = len(観測値_mm)
    重み付き = 重み is not None
    if 重み is None:
        重み = [1] * 個数
    重み合計 = sum(重み)
    平均 = Fraction(sum(w * x for w, x in zip(重み, 観測値_mm)), 重み合計)
    残差 = [Fraction(x) - 平均 for x in 観測値_mm]
    残差平方和 = sum(w * v * v for w, v in zip(重み, 残差))
    加重残差和 = sum(w * v for w, v in zip(重み, 残差))
    標準偏差 = sqrt(残差平方和 / (個数 - 1))
    平均の標準偏差 = 標準偏差 / sqrt(重み合計)
    assert 加重残差和 == 0
    assert all(v.denominator == 1 for v in 残差)
    print(f"【{名称}】")
    print(f"観測値（m）: {', '.join(f'{x / 1000:.3f}' for x in 観測値_mm)}")
    print(f"n = {個数}, 重み = {重み}, 重みの和 = {重み合計}")
    print(f"最確値 = {float(平均) / 1000:.3f} m")
    print(f"残差（mm）= [{', '.join(str(v) for v in 残差)}]")
    print(f"残差二乗（mm²）= [{', '.join(str(v * v) for v in 残差)}]")
    if 重み付き:
        print(f"重み×観測値（m）= [{', '.join(f'{w * x / 1000:.3f}' for w, x in zip(重み, 観測値_mm))}]")
        print(f"重み×残差二乗（mm²）= [{', '.join(str(w * v * v) for w, v in zip(重み, 残差))}]")
    print(f"{'加重残差和' if 重み付き else '残差和'} = {加重残差和} mm")
    print(f"{'加重残差平方和' if 重み付き else '残差平方和'} = {残差平方和} mm²")
    print(f"{'単位重み' if 重み付き else '1観測'}の標準偏差 = {標準偏差:.6f} mm → {標準偏差:.2f} mm")
    print(f"最確値の標準偏差 = {平均の標準偏差:.6f} mm → {平均の標準偏差:.2f} mm")
    print()


def main():
    # Windows の既定文字コードでも日本語・二乗記号を出力できるようにする。
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    検算("例題A", [50001, 50003, 50004, 50006, 50007, 50009])
    検算("例題B", [40002, 40012], [4, 1])
    検算("演習 問1", [30003, 30004, 30005, 30007, 30008, 30009])
    検算("演習 問2", [80000, 80015], [1, 4])
    print("測距精度の例: 2 mm + 2 ppm × 500 m = 3 mm")


if __name__ == "__main__":
    main()
