# AgrTechno 作業ルール

- このプロジェクトの作業対象は `Lecture/AgrTechno/` です。コマンドは原則としてこのディレクトリを作業ディレクトリにして実行します。
- 成果物・中間ファイルはすべて `AgrTechno/` 以下に保存してください。
- `Surveying/` や `MakePaddy/` など、他のプロジェクトのファイルは、ユーザーから指定がない限り変更しないでください。`Surveying/scripts/md2pptx.py` と `Lecture/.claude/skills/lecture-deck-build/scripts/` は読み取りと実行のみ行い、編集しません。
- 日本語で記述し、作業内容は `notes/worklog.md` に日付付きで追記してください。
- Git 操作には親の Lecture リポジトリを使います。独立した Git リポジトリやサブモジュールは作成しません。
- 公開情報・ファイルサイズ・commit / push の扱いは、親の `AGENTS.md` に従ってください。特に、昨年度の原本 `*.pptm`、画像の原本、50 MB 超のファイルは commit しません。
- スライドの原稿は `materials/slides/<回>/slides.md`（Marp 形式）が唯一の原稿です。pptx を手で編集せず、`slides.md` を直してから組み立て直してください。
- 旧デッキから取り出した Web の図（出典 URL 付きのキャプチャ）は、公開版には入れず、自作の図（Codex の image_gen か matplotlib）に置き換えます。
