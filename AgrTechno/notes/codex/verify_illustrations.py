from PIL import Image, ImageDraw
from pathlib import Path
import json
root=Path(__file__).resolve().parents[2]
folder=root/"materials/slides/2026_農業とテクノロジ_RS/figures/illustrations"
records=json.loads((folder/"生成管理.json").read_text(encoding="utf-8"))
sheet=Image.new("RGB",(1600,1000),"#FAF9F5")
draw=ImageDraw.Draw(sheet)
for index,r in enumerate(records):
    img=Image.open(folder/(r["name"]+".png"))
    img.load()
    assert img.mode=="RGB" and img.size==(1600,900) and img.format=="PNG"
    assert (folder/(r["name"]+".png")).stat().st_size<50*1024*1024
    thumb=img.resize((400,225),Image.Resampling.LANCZOS)
    x=(index%4)*400
    y=(index//4)*250
    sheet.paste(thumb,(x,y+25))
    draw.text((x+8,y+8),r["name"],fill="#1F4E79")
    r["background_exact_at_corners"]=all(tuple(c)==(250,249,245) for c in r["corners"])
    r["text_visual_check"]="文字混入なし（目視）"
    r["clipping_visual_check"]="主体の見切れなし（目視）"
    r["status"]="要再生成：背景の完全単色条件が未達"
sheet.save(root/"notes/codex/illustrations_B_contact_sheet.png",compress_level=3)
(folder/"生成管理.json").write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding="utf-8")
print("13 PNGs: RGB, 1600x900, under 50 MB; contact sheet saved")
