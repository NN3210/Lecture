#!/usr/bin/env python3
"""講義4点例題の独立検算。生成処理は読み込み・流用しない。

入力は example.json の観測角文字列・辺長・始点・既知方向のみ。
mpmath 60桁で計算し、表示時まで丸めない。python review08_numbers.py で実行。
"""
import json
import re
from pathlib import Path

from mpmath import mp

mp.dps = 60
ROOT = Path(__file__).resolve().parent
example = json.loads((ROOT / "example.json").read_text())
lecture = example["lecture"]
slides = {s["id"]: s for s in json.loads((ROOT / "part2.json").read_text())}
checks = []


def check(label, condition):
    assert condition, label
    checks.append(label)


def near(label, actual, expected, tolerance="1e-9"):
    check(label, abs(actual - mp.mpf(str(expected))) <= mp.mpf(tolerance))


def seconds(text):
    degree, minute, second = map(int, re.fullmatch(r"(\d+)°(\d+)′(\d+)″", text).groups())
    return mp.mpf(degree * 3600 + minute * 60 + second)


def dms(value):
    total = int(mp.floor(value + mp.mpf("0.5")))
    degree, remainder = divmod(total, 3600)
    minute, second = divmod(remainder, 60)
    return f"{degree}°{minute:02d}′{second:02d}″"


def display(value, digits=3, signed=False):
    # 表示専用。計算へ戻さない。
    scale = mp.mpf(10) ** digits
    rounded = mp.floor(abs(value) * scale + mp.mpf("0.5"))
    integer, fraction = divmod(int(rounded), int(scale))
    prefix = "−" if value < 0 else ("+" if signed else "")
    return f"{prefix}{integer}.{fraction:0{digits}d}"


full = mp.mpf(360 * 3600)
half = full / 2
observed = [seconds(row["observed_dms"]) for row in lecture["rows"]]
lengths = [mp.mpf(str(row["distance"])) for row in lecture["rows"]]
start = tuple(mp.mpf(str(v)) for v in lecture["start"])
initial = seconds(lecture["t_start_dms"])
theory = (len(observed) - 2) * half
error = mp.fsum(observed) - theory
correction = -error / len(observed)
adjusted = [angle + correction for angle in observed]
directions = [initial]
for angle in adjusted[1:]:
    directions.append((directions[-1] + half + angle) % full)
returned = (directions[-1] + half + adjusted[0]) % full
unadjusted_return = initial
for angle in observed[1:] + observed[:1]:
    unadjusted_return = (unadjusted_return + half + angle) % full

components = [
    (length * mp.cos(direction * mp.pi / half), length * mp.sin(direction * mp.pi / half))
    for length, direction in zip(lengths, directions)
]
coordinates = [start]
for dx, dy in components:
    coordinates.append((coordinates[-1][0] + dx, coordinates[-1][1] + dy))
fx, fy = (mp.fsum(row[axis] for row in components) for axis in (0, 1))
perimeter = mp.fsum(lengths)
closure = mp.sqrt(fx ** 2 + fy ** 2)
ratio = closure / perimeter
bowditch = [(-fx * length / perimeter, -fy * length / perimeter) for length in lengths]
corrected = [(dx + vx, dy + vy) for (dx, dy), (vx, vy) in zip(components, bowditch)]
corrected_coordinates = [start]
for dx, dy in corrected:
    corrected_coordinates.append((corrected_coordinates[-1][0] + dx, corrected_coordinates[-1][1] + dy))

for field, actual in {
    "n": len(observed), "theory_sec": theory, "observed_sum_sec": mp.fsum(observed),
    "angle_error_sec": error, "correction_each_sec": correction,
    "adjusted_sum_sec": mp.fsum(adjusted), "return_direction_sec": returned,
    "angular_return_error_sec": returned - initial, "perimeter": perimeter,
    "closure_x": fx, "closure_y": fy, "closure_distance": closure,
}.items():
    near(f"example.lecture.{field}", actual, lecture[field], "1e-11")
near("example.lecture.closure_ratio_denominator", perimeter / closure,
     lecture["closure_ratio_denominator"], "0.001")
check("角許容40秒以内", abs(error) <= lecture["tolerance_sec"])
check("未調整の一周方向", dms(unadjusted_return) == lecture["unadjusted_return_direction_dms"])

for i, row in enumerate(lecture["rows"]):
    for field, actual in {
        "observed_sec": observed[i], "correction_sec": correction, "adjusted_sec": adjusted[i],
        "direction_sec": directions[i], "direction_deg": directions[i] / 3600,
        "dx": components[i][0], "dy": components[i][1],
        "x": coordinates[i + 1][0], "y": coordinates[i + 1][1],
        "bowditch_cx": bowditch[i][0], "bowditch_cy": bowditch[i][1],
        "corrected_dx": corrected[i][0], "corrected_dy": corrected[i][1],
        "corrected_x": corrected_coordinates[i + 1][0], "corrected_y": corrected_coordinates[i + 1][1],
    }.items():
        near(f"example.{row['line']}.{field}", actual, row[field])
    check(f"example.{row['line']}.方向角表記", dms(directions[i]) == row["direction_dms"])
    check(f"example.{row['line']}.調整角表記", dms(adjusted[i]) == row["adjusted_dms"])

check("20: Bの調整角", dms(adjusted[1]) in slides[20]["lead"])
check("20: 後視BA", dms((initial + half) % full) in slides[20]["bullets"][0])
check("20: BC方向角", dms(directions[1]) in slides[20]["notes"])
check("21: 方向角表", [r[1] for r in slides[21]["table"]["rows"]] == [dms(t) for t in directions + [returned]])
check("25: AB成分表示", display(components[0][0]) in slides[25]["title"] and display(components[0][1]) in slides[25]["title"])
check("26: 全辺表", slides[26]["table"]["rows"] == [
    [row["line"], display(length), dms(direction), display(dx, signed=True), display(dy, signed=True)]
    for row, length, direction, (dx, dy) in zip(lecture["rows"], lengths, directions, components)
])
for slide_id, coords in ((27, coordinates), (43, corrected_coordinates)):
    check(f"{slide_id}: 座標表", [r[1:] for r in slides[slide_id]["table"]["rows"]] == [
        [display(x), display(y)] for x, y in coords
    ])
    note_coords = re.findall(r"[（(]([0-9]+\.[0-9]+),([0-9]+\.[0-9]+)[）)]", slides[slide_id]["notes"])
    for i, (printed, actual) in enumerate(zip(note_coords, coords[1:])):
        for axis in (0, 1):
            near(f"{slide_id}: notes座標{i}/{axis}", actual[axis], printed[axis], "5.01e-10")
    check(f"{slide_id}: notes座標個数", len(note_coords) == 4)

# 数値本文は印字桁に対応する幅で照合する。
note40 = slides[40]["notes"]
for label, value in (("f_X", fx), ("f_Y", fy), ("e", closure), ("P", perimeter)):
    token = re.search(rf"{label}＝([+−]?[\d.]+)m", note40).group(1).replace("−", "-")
    near(f"40: {label}", value, token, "5.01e-13")
near("40: r", ratio, "5.189928251e-7", "5.01e-17")
check("40: r表記", "5.189928251×10^−7" in note40)
check("40: 逆数表示", "1,926,809" in note40 and int(mp.floor(perimeter / closure + mp.mpf("0.5"))) == 1926809)
for i, row in enumerate(lecture["rows"]):
    token = re.search(rf"{row['line']}\(([+−][\d.]+),([+−][\d.]+)\)", slides[43]["notes"])
    for axis in (0, 1):
        near(f"43: {row['line']}の補正{axis}", bowditch[i][axis], token.group(axis + 1).replace("−", "-"), "5.01e-10")
for axis in (0, 1):
    near(f"Bowditch成分和{axis}", mp.fsum(row[axis] for row in corrected), 0, "1e-50")
    near(f"Bowditch戻り座標{axis}", corrected_coordinates[-1][axis], start[axis], "1e-50")
check("43: 全成分補正は1mm未満", all(abs(v) < mp.mpf("0.001") for pair in bowditch for v in pair))
rounded_sums = [mp.fsum(mp.mpf(display(pair[axis]).replace("−", "-")) for pair in components) for axis in (0, 1)]
near("26/40: 表示成分和X", rounded_sums[0], "0.001", "1e-50")
near("26/40: 表示成分和Y", rounded_sums[1], "0", "1e-50")

print(f"PASS: {len(checks)} checks, mpmath precision={mp.dps} decimal digits")
print("角和 / 誤差 / 各補正:", dms(mp.fsum(observed)), error, correction)
print("辺 調整角 方向角 ΔX ΔY 未補正座標 補正量 補正後座標")
for i, row in enumerate(lecture["rows"]):
    print(row["line"], dms(adjusted[i]), dms(directions[i]),
          *(mp.nstr(v, 18) for v in components[i]),
          tuple(mp.nstr(v, 18) for v in coordinates[i + 1]),
          tuple(mp.nstr(v, 18) for v in bowditch[i]),
          tuple(mp.nstr(v, 18) for v in corrected_coordinates[i + 1]))
for label, value in (("fX", fx), ("fY", fy), ("e", closure), ("P", perimeter), ("r", ratio), ("P/e", perimeter / closure)):
    print(label, mp.nstr(value, 30))
print("軽微表記差: slide25 notesのΔY=106.441299981386は末尾切捨て。")
print("12桁四捨五入:", display(components[0][1], 12), "m（0.001m表示への影響なし）")
