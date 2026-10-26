"""回2案の数値と新演習を、生読定から独立に再計算する。角度内部単位は秒。"""
from pathlib import Path
import json
import math

OUT = Path(__file__).parent
TURN = 360 * 3600


def sec(d, m=0, s=0):
    return d * 3600 + m * 60 + s


def dms(value):
    sign = '−' if value < 0 else ''
    value = round(abs(value), 1)
    d, rest = divmod(value, 3600)
    m, s = divmod(rest, 60)
    return f'{sign}{int(d)}°{int(m):02d}′{s:04.1f}″'


def difference(a, b):
    return (b - a) % TURN


# 表示予定の生読定を直接与える。期待値は別に手計算した結果。
raw = [
    {'round': 1, 'r': {'A': (5, 0, 10), 'B': (67, 14, 28), 'C': (133, 32, 30)},
     'l': {'A': (185, 0, 14), 'B': (247, 14, 28), 'C': (313, 32, 30)}},
    {'round': 2, 'r': {'A': (95, 0, 20), 'B': (157, 14, 36), 'C': (223, 32, 44)},
     'l': {'A': (275, 0, 16), 'B': (337, 14, 30), 'C': (43, 32, 44)}},
]
expected = {
    (1, 'B'): (sec(62, 14, 18), sec(62, 14, 14), 4),
    (2, 'B'): (sec(62, 14, 16), sec(62, 14, 14), 2),
    (1, 'C'): (sec(128, 32, 20), sec(128, 32, 16), 4),
    (2, 'C'): (sec(128, 32, 24), sec(128, 32, 28), -4),
}
records = []
for row in raw:
    readings = {face: {key: sec(*value) for key, value in row[face].items()} for face in ('r', 'l')}
    for target in ('B', 'C'):
        p = difference(readings['r']['A'], readings['r'][target])
        q = difference(readings['l']['A'], readings['l'][target])
        assert (p, q, p-q) == expected[(row['round'], target)]
        records.append({'round': row['round'], 'target': target,
                        'p_sec': p, 'q_sec': q, 'D_sec': p+q, 'C_sec': p-q,
                        'mean_sec': (p+q)/2,
                        'p': dms(p), 'q': dms(q), 'D': dms(p+q), 'mean': dms((p+q)/2)})

tolerance = {'double_angle_range_sec': 10, 'observation_range_sec': 8,
             'status': '授業だけの仮基準。公共測量の規程値ではない。境界値は範囲内。'}
targets = {}
for target in ('B', 'C'):
    rows = [row for row in records if row['target'] == target]
    drange = max(row['D_sec'] for row in rows) - min(row['D_sec'] for row in rows)
    crange = max(row['C_sec'] for row in rows) - min(row['C_sec'] for row in rows)
    accept = drange <= tolerance['double_angle_range_sec'] and crange <= tolerance['observation_range_sec']
    targets[target] = {'double_angle_range_sec': drange, 'observation_range_sec': crange,
                       'accept': accept, 'adopted_sec': sum(row['mean_sec'] for row in rows)/2 if accept else None}
assert targets['B'] == {'double_angle_range_sec': 2, 'observation_range_sec': 2, 'accept': True, 'adopted_sec': sec(62, 14, 15.5)}
assert targets['C'] == {'double_angle_range_sec': 16, 'observation_range_sec': 8, 'accept': False, 'adopted_sec': None}

checks = []


def check(name, actual, expected_value, tol=1e-9):
    assert abs(actual-expected_value) <= tol, (name, actual, expected_value)
    checks.append({'name': name, 'value': actual, 'expected': expected_value, 'tolerance': tol})


check('読定差', difference(sec(30,10), sec(103,35)), sec(73,25))
check('360度境界', difference(sec(350), sec(20)), sec(30))
check('確認1読定差', difference(sec(15,20), sec(88,45)), sec(73,25))
check('同じ器械点の方向角', (sec(40)+sec(73,25))%TURN, sec(113,25))
check('一方向の正反平均モデル', (sec(40,0,6)+sec(220)-sec(180))/2, sec(40,0,3))
check('較差の対回間範囲', max(1,-3)-min(1,-3), 4)
lecture_raw = [(sec(12,15,20),sec(85,40,35),sec(192,15,26),sec(265,40,37)),
               (sec(102,7,40),sec(175,32,49),sec(282,7,36),sec(355,32,47))]
lecture_results = [(difference(a,b),difference(c,d)) for a,b,c,d in lecture_raw]
check('方向法説明 第1対回正の結果', lecture_results[0][0], sec(73,25,15))
check('方向法説明 第1対回反の結果', lecture_results[0][1], sec(73,25,11))
check('方向法説明 第2対回正の結果', lecture_results[1][0], sec(73,25,9))
check('方向法説明 第2対回反の結果', lecture_results[1][1], sec(73,25,11))
check('方向法説明 倍角差', abs(sum(lecture_results[0])-sum(lecture_results[1])), 6)
check('方向法説明 観測差', abs((lecture_results[0][0]-lecture_results[0][1])-(lecture_results[1][0]-lecture_results[1][1])), 6)
check('方向法説明 平均水平角', sum(sum(row) for row in lecture_results)/4, sec(73,25,11.5))
check('鉛直例K', sec(78,12,42)+sec(281,47,42)-TURN, 24)
check('鉛直例Z', (sec(78,12,42)-sec(281,47,42)+TURN)/2, sec(78,12,30))
check('鉛直例高低角', sec(90)-sec(78,12,30), sec(11,47,30))
check('高度定数の較差', max(24,30)-min(24,30), 6)
check('鉛直確認K', sec(85,10,20)+sec(274,49,50)-TURN, 10)
check('鉛直確認Z', (sec(85,10,20)-sec(274,49,50)+TURN)/2, sec(85,10,15))
check('鉛直確認高低角', sec(90)-sec(85,10,15), sec(4,49,45))
check('100m先の1秒の横ずれmm', 100000*math.tan(math.radians(1/3600)), 0.484813681113, 1e-10)
check('100m先の1分の横ずれmmの表示', round(100000*math.tan(math.radians(1/60)), 1), 29.1)

delta = math.degrees(math.atan(1/100))
oa = math.hypot(100, 1)
exercise_angle = 90-delta
coordinate_angle = (90-math.degrees(math.atan2(1,100))) % 360
# 第2経路：余弦定理の内積から中心角を求め、逆正接と照合する。
cosine_angle = math.degrees(math.acos(1/oa))
check('偏心演習の中心角 座標経路', exercise_angle, coordinate_angle)
check('偏心演習の中心角 余弦経路', exercise_angle, cosine_angle)
check('偏心演習OA', oa, 100.00499987500625)
explanatory_e_angle = (90 - math.degrees(math.atan2(-1,100))) % 360
check('偏心説明 Eでの角', explanatory_e_angle, 90+delta)
check('偏心説明 中心へ戻す角補正', 90-explanatory_e_angle, -delta)
check('偏心説明 距離補正は負', 100-oa, -0.004999875006248544)
check('偏心演習DMS表示', round(exercise_angle*3600,1), sec(89,25,37.4))
check('後視方向へ反転して交角を足す', (40+180+100)%360, 320)
check('宿題 指定されたrho=200000の場合', sec(83,20,30)+200000*9*math.sin(math.radians(330))/1000, sec(83,5,30), 1e-8)

# 較差0でも各方向の生読定に共通の器械誤差成分を含み得る反例。
ar, br, al, bl = sec(10,0,5), sec(70,0,5), sec(189,59,55), sec(249,59,55)
check('反例 正の結果', br-ar, sec(60))
check('反例 反の結果', bl-al, sec(60))
check('反例 較差', (br-ar)-(bl-al), 0)
check('反例 生読定の正反差は10秒', ar-(al-sec(180)), 10)

data = {
    'status': '回2合意版。Claudeとの相互批評と数値検算を反映。',
    'units': '角度の内部計算は角秒、距離はm。演習値は架空。',
    'direction_exercise': {'raw_dms': raw, 'results': records, 'tolerance': tolerance, 'targets': targets},
    'eccentric_exercise': {'conditions': 'O→E→Bの順に一直線。OE=1m、EA=100m。AはEの北。A→B時計回り90度。',
                           'delta_deg': delta, 'central_angle_deg': exercise_angle,
                           'central_angle_dms': dms(exercise_angle*3600), 'OA_m': oa,
                           'angle_correction_deg': -delta, 'distance_correction_m': oa-100},
    'supplement': {'rho_exact_arcsec_per_rad': 180*3600/math.pi,
                  'approximation_minus_exact_at_ratio_0_01_arcsec': (0.01-math.atan(0.01))*180*3600/math.pi,
                  'homework_correction_with_rho206265_arcsec': 206265*9*math.sin(math.radians(330))/1000},
    'checks': checks,
}
(OUT/'kai2_verified_numbers.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'passed_checks': len(checks), 'raw_record_checks': len(records), 'targets': targets,
                  'central_angle_dms': data['eccentric_exercise']['central_angle_dms']}, ensure_ascii=True))
