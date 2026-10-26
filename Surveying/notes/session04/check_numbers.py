#!/usr/bin/env python3
"""notes/session04/numbers.json の独立検算（標準ライブラリのみ）。"""
from __future__ import annotations

import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
FULL = 360 * 3600
HALF = 180 * 3600


def close(actual: float, expected: float, tol: float = 1e-9) -> None:
    assert math.isclose(actual, expected, rel_tol=0.0, abs_tol=tol), (actual, expected)


def azimuth_deg(origin: list[float], target: list[float]) -> float:
    # 測量座標 X=北、Y=東なので atan2(ΔY, ΔX)。
    dx = target[0] - origin[0]
    dy = target[1] - origin[1]
    return math.degrees(math.atan2(dy, dx)) % 360.0


def main() -> None:
    data = json.loads((HERE / "numbers.json").read_text(encoding="utf-8"))

    rounds = data["direction_method"]["rounds"]
    reduced = {}
    for rnd in rounds:
        a0 = rnd["observations"][0]["mean_sec"]
        for obs in rnd["observations"]:
            # JSONには境界をまたいだC（第2対回）があるため、換算値を直接検算する。
            delta = obs["R_converted_sec"] - obs["L_sec"]
            assert delta == obs["Rprime_minus_L_sec"]
            assert obs["R_converted_sec"] % FULL == (obs["R_sec"] - HALF) % FULL
            close((obs["L_sec"] + obs["R_converted_sec"]) / 2, obs["mean_sec"])
            assert obs["mean_sec"] - a0 == obs["reduced_sec"]
            reduced.setdefault(obs["sight"], []).append(obs["reduced_sec"])
        assert rnd["observations"][-1]["reduced_sec"] == rnd["closure_Aclose_minus_Astart_sec"]

    comp = data["direction_method"]["between_round_comparisons"]
    assert reduced["B"][0] - reduced["B"][1] == comp["B_reduced_round1_minus_round2_sec"]
    assert reduced["C"][0] - reduced["C"][1] == comp["C_reduced_round1_minus_round2_sec"]
    for target in ("B", "C"):
        assert max(reduced[target]) - min(reduced[target]) == comp["range_by_target_sec"][target]
        close(sum(reduced[target]) / 2, comp["mean_reduced_sec"][target])

    ecc = data["eccentric_observation"]
    p = ecc["points_m"]
    az_ea = azimuth_deg(p["E"], p["A"])
    az_eb = azimuth_deg(p["E"], p["B"])
    angle_e = (az_eb - az_ea) % 360.0
    dist_ea = math.dist(p["E"], p["A"])
    dist_eb = math.dist(p["E"], p["B"])
    close(az_ea, ecc["from_E"]["azimuth_A_deg"])
    close(az_eb, ecc["from_E"]["azimuth_B_deg"])
    close(angle_e, ecc["from_E"]["clockwise_angle_A_to_B_deg"])
    close(dist_ea, ecc["from_E"]["distance_A_m"])
    close(dist_eb, ecc["from_E"]["distance_B_m"])
    angle_o = (azimuth_deg(p["O"], p["B"]) - azimuth_deg(p["O"], p["A"])) % 360.0
    close(angle_o, 90.0)
    close(math.dist(p["O"], p["A"]), 100.0)
    close(math.dist(p["O"], p["B"]), 100.0)
    corr = ecc["corrections_center_minus_eccentric"]
    close(corr["angle_deg"], angle_o - angle_e)
    close(corr["distance_A_m"], 100.0 - dist_ea)
    close(corr["distance_B_m"], 100.0 - dist_eb)

    z = data["zenith_angle"]
    close((z["ZL_sec"] - z["ZR_sec"] + FULL) / 2, z["recovered_Z_sec"])
    close((z["ZL_sec"] + z["ZR_sec"] - FULL) / 2, z["recovered_i_sec"])
    assert z["elevation_angle_sec"] == 90 * 3600 - z["recovered_Z_sec"]

    wrap = data["wraparound"]
    assert (wrap["end_sec"] - wrap["start_sec"]) % FULL == wrap["clockwise_difference_sec"]
    offset = 100 * math.tan(math.radians(1 / 3600))
    close(offset, data["one_arcsecond_at_100m"]["exact_lateral_offset_m"], 5e-16)
    close(offset * 1000, data["one_arcsecond_at_100m"]["exact_lateral_offset_mm"], 5e-13)

    print("OK: 方向法・偏心・天頂角・360°跨ぎ・1秒/100 m の全検算に合格")


if __name__ == "__main__":
    main()
