from pathlib import Path
import json
from PIL import Image, ImageOps, ImageDraw

notes = Path(__file__).resolve().parent
root = notes.parent.parent
illustrations = root / 'materials' / 'slides' / '第05回_トラバース測量I' / 'illustrations'
jobs = json.loads((notes / 'generation_sources' / 'jobs.json').read_text(encoding='utf-8'))
results = []
for job in jobs:
    source = notes / job['attempts'][job['selected']]['path']
    target = illustrations / (job['name'] + '.png')
    with Image.open(source) as img:
        img.load()
        original = {'format': img.format, 'mode': img.mode, 'size': list(img.size)}
        img.convert('RGB').resize((1600, 900), Image.Resampling.LANCZOS).save(target, format='PNG')
    with Image.open(target) as img:
        img.load()
        assert img.format == 'PNG' and img.mode == 'RGB' and img.size == (1600, 900)
        result = {'file': target.name, 'exists': target.is_file(), 'format': img.format, 'mode': img.mode, 'size': list(img.size), 'bytes': target.stat().st_size, 'retries': len(job['attempts'])-1, 'original': original}
        assert result['bytes'] < 50 * 1024 * 1024
        results.append(result)
(notes / 'generation_sources' / 'validation.json').write_text(json.dumps(results, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
# 縮小一覧は目視確認用。図内容を描き直す処理はしない。
sheet = Image.new('RGB', (1000, 4 * 310), '#FAF9F5')
draw = ImageDraw.Draw(sheet)
for i, job in enumerate(jobs):
    x, y = (i % 2)*500, (i // 2)*310
    with Image.open(illustrations / (job['name']+'.png')) as img:
        sheet.paste(img.resize((480,270), Image.Resampling.LANCZOS), (x+10,y+28))
    draw.text((x+10,y+8), job['name']+'.png', fill='#1F4E79')
sheet.save(notes / 'generation_sources' / 'contact_sheet.png')
print(json.dumps(results, ensure_ascii=True))
