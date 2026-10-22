作成しました。**13段・標準13分（最大15分）**の設計と、図版13点です。

- [段階設計・発表者ノート・数値表](<home>/Documents/Workplace/MISC/Lecture/AgrTechno/notes/codex/電磁波の段階設計.md)
- [報告書・図版一覧・未確認事項](<home>/Documents/Workplace/MISC/Lecture/AgrTechno/notes/codex/report_A_電磁波の段階設計.md)
- [再生成スクリプト](<home>/Documents/Workplace/MISC/Lecture/AgrTechno/scripts/figures/make_charts.py)

全図1600×900 px・Yu Gothic。字形欠け、配置、物理式を検証し、全画像を目視確認しました。

```powershell
python -I scripts/figures/make_charts.py
python -I scripts/figures/make_charts.py --only 03
```

変更は指定された3ディレクトリ内のみです。Git操作は行っていません。