"""第4回「角測量」の数値を、教材の既計算値に依存せず再計算する。

標準ライブラリだけで実行できる。角度の加減算は原則として整数秒で行い、
偏心と 1 秒の横ずれだけを math から計算する。
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SESSION = ROOT / "notes" / "session04"
EXERCISE = ROOT / "materials" / "exercises" / "第04回_角測量"
EXPLANATION = ROOT / "materials" / "slides" / "第04回_角測量" / "explanation.html"


def dms(deg: int, minute: int, second: int) -> int:
    return deg * 3600 + minute * 60 + second


def close(actual: float, expected: float, tolerance: float, label: str) -> None:
    if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=tolerance):
        raise AssertionError(f"{label}: {actual!r} != {expected!r} (tol={tolerance})")


def require(text: str, pattern: str, label: str) -> None:
    if re.search(pattern, text) is None:
        raise AssertionError(f"{label}: 掲載値が見つからない: {pattern}")


def main() -> None:
    numbers = json.loads((SESSION / "numbers.json").read_text(encoding="utf-8"))
    verified = json.loads((SESSION / "verified_numbers.json").read_text(encoding="utf-8"))
    publication_files = [
        SESSION / "slides_part1.json",
        SESSION / "slides_part2.json",
        EXERCISE / "exercise.md",
        EXERCISE / "exercise_answers.md",
        EXPLANATION,
    ]
    optional_part3 = SESSION / "slides_part3.json"
    if optional_part3.exists():
        publication_files.append(optional_part3)
    publications = "\n".join(p.read_text(encoding="utf-8") for p in publication_files)

    # 生読定から正・反各列を独立に帰零する（反の180°換算は差で相殺）。
    raw = {
        1: {"L0": dms(12, 15, 20), "LB": dms(85, 40, 35),
            "R0": dms(192, 15, 26), "RB": dms(265, 40, 37),
            "Lclose": dms(12, 15, 25), "Rclose": dms(192, 15, 29)},
        2: {"L0": dms(102, 7, 40), "LB": dms(175, 32, 49),
            "R0": dms(282, 7, 36), "RB": dms(355, 32, 47),
            "Lclose": dms(102, 7, 35), "Rclose": dms(282, 7, 39)},
    }
    expected = {
        1: {"p": 264315, "q": 264311, "C": 4, "D": 528626,
            "theta": 264313.0, "return_L": 5, "return_R": 3},
        2: {"p": 264309, "q": 264311, "C": -2, "D": 528620,
            "theta": 264310.0, "return_L": -5, "return_R": 3},
    }
    computed: dict[int, dict[str, float]] = {}
    for k, r in raw.items():
        p, q = r["LB"] - r["L0"], r["RB"] - r["R0"]
        computed[k] = {
            "p": p, "q": q, "C": p - q, "D": p + q,
            "theta": (p + q) / 2,
            "return_L": r["Lclose"] - r["L0"],
            "return_R": r["Rclose"] - r["R0"],
        }
        assert computed[k] == expected[k], f"第{k}対回: {computed[k]}"

    delta_c = max(x["C"] for x in computed.values()) - min(x["C"] for x in computed.values())
    delta_d = max(x["D"] for x in computed.values()) - min(x["D"] for x in computed.values())
    mean_theta = sum(x["theta"] for x in computed.values()) / len(computed)
    max_return = max(abs(x[f"return_{face}"]) for x in computed.values() for face in ("L", "R"))
    assert (delta_d, delta_c, max_return, mean_theta) == (6, 6, 5, 264311.5)
    assert delta_d <= 8 and not delta_c <= 5 and max_return <= 6

    # verified_numbers.json と照合。
    for row in verified["rounds"]:
        b = next(t for t in row["targets"] if t["target"] == "B")
        c = computed[row["round"]]
        assert (b["p_sec"], b["q_sec"], b["C_sec"], b["D_sec"], b["mean_sec"]) == (
            c["p"], c["q"], c["C"], c["D"], c["theta"])
    bcheck = next(x for x in verified["checks"] if x["target"] == "B")
    assert (bcheck["double_angle_range_sec"], bcheck["observation_range_sec"], bcheck["final_angle_sec"]) == (
        delta_d, delta_c, mean_theta)

    # numbers.json の生読定・平均方向値も、各行から再構成する。
    for rnd in numbers["direction_method"]["rounds"]:
        for obs in rnd["observations"]:
            converted = obs["R_sec"] - 180 * 3600 if obs["R_sec"] >= 180 * 3600 else obs["R_sec"] + 180 * 3600
            assert converted == obs["R_converted_sec"]
            assert (obs["L_sec"] + converted) / 2 == obs["mean_sec"]
        assert rnd["observations"][-1]["mean_sec"] - rnd["observations"][0]["mean_sec"] == rnd["closure_Aclose_minus_Astart_sec"]

    # 偏心観測を座標差から独立計算。方向角は X（北）から時計回り。
    O, E, A, B = (0.0, 0.0), (0.0, 1.0), (100.0, 0.0), (0.0, 100.0)
    def distance(P: tuple[float, float], Q: tuple[float, float]) -> float:
        return math.hypot(Q[0] - P[0], Q[1] - P[1])
    def azimuth(P: tuple[float, float], Q: tuple[float, float]) -> float:
        return math.degrees(math.atan2(Q[1] - P[1], Q[0] - P[0])) % 360
    az_a, az_b = azimuth(E, A), azimuth(E, B)
    angle_e = (az_b - az_a) % 360
    ecc = numbers["eccentric_observation"]
    close(az_a, ecc["from_E"]["azimuth_A_deg"], 1e-12, "E→A方向角")
    close(angle_e, 90.5729386976835, 1e-12, "EでのA→B角")
    close(distance(E, A), 100.00499987500625, 1e-12, "EA")
    close(distance(E, B), 99.0, 1e-12, "EB")
    corrections = (90.0 - angle_e, distance(O, A) - distance(E, A), distance(O, B) - distance(E, B))
    for actual, expected_value, label in zip(corrections, (-0.5729386976835, -0.00499987500625, 1.0), ("角補正", "A距離補正", "B距離補正")):
        close(actual, expected_value, 1e-12, label)

    # 天頂角：K=ZL+ZR-360°, i=K/2, Z=ZL-i, α=90°-Z。
    zl, zr = dms(78, 12, 42), dms(281, 47, 42)
    K = zl + zr - dms(360, 0, 0)
    i = K / 2
    Z = zl - i
    alpha = dms(90, 0, 0) - Z
    assert (K, i, Z, alpha) == (24, 12, 281550, 42450)
    assert verified["zenith"] == {"K_sec": 24, "i_sec": 12, "Z_sec": 281550, "elevation_sec": 42450}

    # 1″/100 m、360°跨ぎ、DMS例。
    offset_mm = 100 * math.tan(math.radians(1 / 3600)) * 1000
    close(offset_mm, 0.484813681113, 1e-12, "100 m先の1秒")
    assert ((20 - 350) % 360) == 30
    assert dms(95, 1, 10) == 342070
    assert dms(12, 34, 50) + dms(0, 26, 25) == dms(13, 1, 15)

    # 公開物に主要結果が現れることを確認（HTMLは参照のみで変更しない）。
    for pattern, label in [
        (r"73°25′11\.5″", "方向法平均"), (r"146°50′26″", "第1対回倍角"),
        (r"146°50′20″", "第2対回倍角"), (r"観測差[^\n]{0,100}6″", "観測差"),
        (r"78°12′42″", "正天頂読定"), (r"281°47′42″", "反天頂読定"),
        (r"K[^\n]{0,30}24″", "高度定数"), (r"11°47′30″", "高低角"),
        (r"0\.485 mm", "1秒/100 m"), (r"95°01′10″", "DMS読取例"),
        (r"−0\.57293", "偏心角補正"), (r"−0\.0050", "偏心A距離補正"),
        (r"\+1\.0000|＋1\.0000|\+1 m", "偏心B距離補正"),
    ]:
        require(publications, pattern, label)

    print("OK: 第4回の方向法・点検基準・偏心・天頂角・DMSを独立計算で検算しました。")
    print(f"方向法: ΔD={delta_d}″ (<=8), ΔC={delta_c}″ (>5), 最大帰零差={max_return}″ (<=6) → 再測")
    print(f"平均角（点検前）={mean_theta / 3600:.10f}° = 73°25′11.5″")
    print(f"偏心補正: 角={corrections[0]:.10f}°, A={corrections[1]:.10f} m, B={corrections[2]:+.4f} m")
    print(f"天頂: K={K}″, i={i:g}″, Z=78°12′30″, α=+11°47′30″")
    print(f"1″/100 m={offset_mm:.12f} mm; 95°01′10″={dms(95, 1, 10)}″")


if __name__ == "__main__":
    main()
