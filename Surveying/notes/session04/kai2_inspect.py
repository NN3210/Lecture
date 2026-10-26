import json
from pathlib import Path
root=Path(__file__).parent
slides=sum([json.loads(p.read_text(encoding='utf-8')) for p in sorted(root.glob('slides_part*.json'))],[])
for s in slides:
    print(s['id'],s['kind'],s['title'])
