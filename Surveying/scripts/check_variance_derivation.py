"""スライドの確率モデルと分散の恒等式を分数のまま検算する。"""
from fractions import Fraction as F
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
probabilities = [F(1, 4), F(1, 2), F(1, 4)]
assert sum(probabilities) == 1
records = []
for bias in [0, 3]:
    values = [F(x + bias) for x in [-2, 0, 2]]
    mean = sum(x * p for x, p in zip(values, probabilities))
    second = sum(x * x * p for x, p in zip(values, probabilities))
    variance = sum((x - mean) ** 2 * p for x, p in zip(values, probabilities))
    assert variance == second - mean**2 == 2
    assert mean == bias and second == 2 + bias**2
    records.append(dict(誤差_mm=list(map(int, values)), 平均_mm=int(mean),
                        二乗期待値_mm2=int(second), 分散_mm2=int(variance)))

# 非対称で平均0の分布も、一般の恒等式を満たす。
values, probs = [F(-1), F(2)], [F(2, 3), F(1, 3)]
assert sum(x*p for x, p in zip(values, probs)) == 0
assert sum(x*x*p for x, p in zip(values, probs)) == 2
dest = ROOT / 'notes/variance_derivation_20261015/数値検算.json'
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps(dict(数値例=records, 非対称な平均0の例も成立=True),
                           ensure_ascii=False, indent=2), encoding='utf-8')
print('期待値・分散・偏りの分解を分数演算で検算済み。')
