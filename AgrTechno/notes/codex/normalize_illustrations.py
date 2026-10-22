from PIL import Image, ImageOps
from pathlib import Path
import json
root=Path(__file__).resolve().parents[2]
folder=root/"materials/slides/2026_農業とテクノロジ_RS/figures/illustrations"
records=json.loads((folder/"生成管理.json").read_text(encoding="utf-8"))
for r in records:
    source=Image.open(folder/r["source"]).convert("RGB")
    img=ImageOps.fit(source,(1600,900),method=Image.Resampling.LANCZOS,centering=(0.5,0.5))
    dest=folder/(r["name"]+".png")
    img.save(dest,format="PNG",compress_level=3)
    check=Image.open(dest)
    assert check.size==(1600,900) and check.mode=="RGB" and check.format=="PNG"
    r["size"]=[1600,900]
    r["mode"]="RGB"
    r["bytes"]=dest.stat().st_size
    r["corners"]=[check.getpixel(p) for p in [(0,0),(1599,0),(0,899),(1599,899)]]
(folder/"生成管理.json").write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps([{k:r[k] for k in ["name","size","mode","bytes","corners"]} for r in records],ensure_ascii=False))
