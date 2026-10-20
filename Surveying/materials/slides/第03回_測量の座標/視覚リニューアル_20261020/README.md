# 第3回 測量の座標：視覚リニューアル版

高校生にもイメージしやすい、図と問いから始める81枚の別版。元の `../slides.md`・`../slides.pptx`・`../slides.pdf` は変更していません。

- [PowerPoint](測量学第03回_視覚リニューアル.pptx)
- [閲覧・配布用PDF](測量学第03回_視覚リニューアル.pdf)

## 変更内容

- 校庭の待ち合わせ、コップの水面、みかんの皮など、身近な例を使って18枚を再構成。
- 回転・基線ベクトル・方向角の計算例6枚に、式と対応する編集可能な図を追加。
- 章ごとの色、問いかける見出し、結論の囲みを統一。小テスト・手計算テスト・出典は保持。
- 再構成したページの元の本文は、発表者ノートにも保存。
- 元のOffice数式211件は、要素・属性・文字列を照合し、変更がないことを確認。

## 表示と編集

PowerPointのOffice数式対応環境では数式を編集できます。非対応のビューア向けには、元のPDFから作った数式・表などの互換画像を格納しました。数式を編集した場合は、互換画像とPDFも更新してください。通常の本文・追加した図形は編集可能です。本文フォントは Noto Sans CJK JP、数式は元のフォントを保持しています。

PDFはLibreOfficeで書き出し、81枚の一覧と変更箇所の拡大表示を点検。通常のテキストボックスの全文がPDFに含まれることも機械照合しています。Microsoft PowerPoint実機での表示確認は未実施です。

## 再生成

`Surveying/` で次を実行します。Python依存は python-pptx・PyMuPDF・Pillow・lxml。PPTX生成に元のPPTXとPDFの両方を使用します。

```sh
python scripts/redesign_session03_20261020.py
soffice --headless --convert-to pdf --outdir materials/slides/第03回_測量の座標/視覚リニューアル_20261020 materials/slides/第03回_測量の座標/視覚リニューアル_20261020/測量学第03回_視覚リニューアル.pptx
python scripts/verify_session03_20261020.py
```

`review/validation.json` に元ファイルのSHA-256と数式保持の記録、`review/pdf-validation.json` に表示用テキストの照合、`review/contact_*.jpg` に全81枚の一覧を保存します。内容上の新しい出典は追加していません。新規の図は説明用の模式図です。
