# ondemand — オンデマンド講義動画（TTS ナレーション）の作成環境

測量学のオンデマンド回（最初の対象は **第5回 トラバース測量 I**）を、スライド画像 + 講師本人の声に似せた TTS（テキスト読み上げ）ナレーションの動画として作るための文書とスクリプト群。
AI エージェント（Claude Code / Codex）がこのフォルダーの文書を読んで、そのまま実行できるように書いてある。

## まず読む順番

| 順 | 文書 | 内容 |
| --- | --- | --- |
| 1 | この README | 全体像、フォルダー構成、動作確認済みの範囲 |
| 2 | [`01_指南書_声の複製TTSと動画化.md`](01_指南書_声の複製TTSと動画化.md) | **本体。** 環境構築 → 台本 → 本人の声の抽出 → 声の複製 → 動画化 → 点検、の実行手順 |
| 3 | [`台本の書き方.md`](台本の書き方.md) | ナレーション台本（narration.md）の形式と、読み上げ向けの書き換え規則（測量用語の読み） |
| 4 | [`02_TTSと声の複製の選択肢_20261022.md`](02_TTSと声の複製の選択肢_20261022.md) | 2026-10-22 時点の TTS・声の複製サービス/モデルの比較、要件、根拠（出典 URL） |

## 全体の流れ

```
pptx（第5回）─ pptx_export.ps1 ─▶ スライド PNG ─┐
発表者ノート（slides.md の <!-- --> か pptx）─ extract_notes.py ─▶ narration.md（読み上げ用に書き直す）─┤
                                                                                  ├─ build_video.py ─▶ mp4 + srt + timings.json
本人の声 ─(PLAUD 録音 + Circleback 話者分離)─ extract_speaker.py ─ prepare_reference.py ─▶ 参照音声 ─┤
                                            └─▶ XTTS（ローカル）/ ElevenLabs（クラウド）で声を複製 ─┘
```

1. 最初は無料の **edge-tts**（Microsoft の既製の日本語音声）で動画を 1 本作って、台本・画面・字幕の流れを固める。
2. 次に本人の声の参照音声を作り、**XTTS v2（ローカル、CPU）** で声の似せ方を試す。
3. 品質が必要なら **ElevenLabs** の Instant / Professional Voice Clone に切り替える（有料、本人の声だけをアップロード）。

## フォルダー構成

```
Surveying/
├─ ondemand/                     ← 文書（この README、指南書、比較）
│   ├─ .gitignore                ← voice/ work/ と音声・動画ファイルを commit から除外
│   ├─ voice/                    ← 【commit しない】本人の声の素材
│   │   ├─ raw/                  ← PLAUD からダウンロードした録音（会議全体、他の人の声を含む）。raw/transcripts/ に Circleback の JSON
│   │   ├─ self_search/          ← find_self.py の出力（report.md, self_map.json, auto_enroll.wav, enroll_segments.json, enroll_check.md, cache/ に 16 kHz WAV・VAD・埋め込み）
│   │   ├─ enroll/               ← 本人だけの短い録音（話者判定用。30 秒〜3 分）
│   │   ├─ segments/<日付>/      ← extract_speaker.py が切り出した本人の発話区間 + index.csv
│   │   └─ reference/            ← prepare_reference.py の出力（xtts_ref_NN.wav, ivc_reference.mp3, pvc_part_NN.mp3）
│   └─ work/                     ← 【commit しない】動画の作業ファイル（スライドごとの音声、manifest.json）
├─ scripts/ondemand/             ← スクリプト（commit する）
│   ├─ tts_backends.py           ← TTS エンジン（edge / xtts / elevenlabs）の共通関数
│   ├─ tts_synth.py              ← テキスト 1 本 → WAV 1 本（動作確認用）
│   ├─ extract_notes.py          ← pptx の発表者ノート → narration.md の下書き
│   ├─ build_video.py            ← narration.md + PNG → mp4 + srt + timings.json
│   ├─ plaud_download.py         ← PLAUD クラウドの録音一覧・ダウンロード
│   ├─ extract_speaker.py        ← 会議録音 + Circleback の話者分離 → 本人の区間だけ切り出し
│   ├─ find_self.py              ← enroll 録音なしで、複数の会議録音をまたいで本人（装着者）を見つけ auto_enroll.wav を作る
│   ├─ verify_enroll.py          ← auto_enroll.wav の区間を音声認識で読み直し、文字起こしと一致するか検証
│   ├─ vad_util.py               ← Silero VAD で発話区間を出す補助（Circleback の粗い話者区間を発話だけに割る）
│   ├─ prepare_reference.py      ← 切り出した区間 → 各エンジン用の参照音声（整音・連結）
│   ├─ voice_similarity.py       ← 音声どうしの話者類似度（合成音声が本人に似ているかの数値確認）
│   ├─ check_asr.py              ← 合成音声を音声認識（faster-whisper）に戻して台本と比較（誤読・途切れの検出）
│   └─ audio_io.py               ← torchaudio.load を soundfile に差し替える補助（Windows の torchcodec 対策）
└─ materials/slides/第05回_トラバース測量I/   ← 第5回の slides.md（Marp、発表者ノート付き。2026-10-22 に別セッションが作成中）・pptx・narration.md・preview/（PNG）
```

動画（mp4）は 50 MB を超えることが多いので commit しない。完成した動画の置き場所（LMS、クラウドの共有フォルダー等）は `notes/worklog.md` に記す。

## 必要なもの（この PC で確認済み、2026-10-22）

| 項目 | 内容 |
| --- | --- |
| OS / CPU / GPU | Windows 11、Core i7-1165G7（4 コア）、GPU なし（内蔵 Iris Xe）。メモリ 16 GB |
| Python | システムの Python 3.11（edge-tts、動画化はこれで動く） |
| 仮想環境 | `%USERPROFILE%\.venvs\ondemand-tts`（XTTS・speechbrain・faster-whisper 用。torch 2.14 CPU、coqui-tts 0.28、speechbrain 1.1、faster-whisper 1.2） |
| ffmpeg / ffprobe | 8.0.1（winget の Gyan.FFmpeg、static ビルド）。PATH にある |
| PowerPoint | COM 経由で PNG 書き出し（`scripts/pptx_export.ps1`） |
| PLAUD / Circleback | 録音と文字起こしの取得は `C:\MyProjects\auto-tools\audio2md` のトークンを流用（トークンの値は書かない） |

## クイックスタート（edge-tts で 1 本作る）

```powershell
# 1. Marp の slides.md → pptx → PNG（preview/ は事前に作らない。空の preview/ があると書き出しに失敗する）
python scripts/md2pptx.py "materials/slides/第05回_トラバース測量I/slides.md" -o "materials/slides/第05回_トラバース測量I/slides.pptx"
powershell -ExecutionPolicy Bypass -File scripts/pptx_export.ps1 -Pptx "materials/slides/第05回_トラバース測量I/slides.pptx" -PngDir "materials/slides/第05回_トラバース測量I/preview"
# 2. 発表者ノート（slides.md の <!-- --> か pptx のノート）から台本の下書き → 台本の書き方.md に従って書き直す
python scripts/ondemand/extract_notes.py "materials/slides/第05回_トラバース測量I/slides.md" -o "materials/slides/第05回_トラバース測量I/narration.md"
# 3. 対応を確認してから動画化
python scripts/ondemand/build_video.py --narration "materials/slides/第05回_トラバース測量I/narration.md" --png-dir "materials/slides/第05回_トラバース測量I/preview" --out ondemand/work/lecture05_edge.mp4 --engine edge --dry-run
python scripts/ondemand/build_video.py --narration "materials/slides/第05回_トラバース測量I/narration.md" --png-dir "materials/slides/第05回_トラバース測量I/preview" --out ondemand/work/lecture05_edge.mp4 --engine edge
```

本人の声にする手順は指南書の第 5〜6 章。

## 動作確認済みの範囲（2026-10-22）

| 段階 | 状態 |
| --- | --- |
| edge-tts（ja-JP-KeitaNeural / NanamiNeural）で日本語の音声・字幕 | 確認済み |
| PNG 2 枚 + 台本 → mp4（57 秒、1280x720、H.264/AAC）+ srt + timings.json | 確認済み（音声長と動画長が一致） |
| PLAUD クラウドの一覧・ダウンロード（実体は Ogg/Opus 48 kHz モノラル 約 32 kbps） | 確認済み |
| Circleback の文字起こし JSON（segments[].speaker/start/end/text） | 構造を確認済み |
| speechbrain ECAPA の話者類似度（同一音声 0.84、別人 0.09〜0.13） | 確認済み（合成音声での検証） |
| XTTS v2 日本語を CPU で合成 | 確認済み（モデル読込後の RTF 4〜7。指南書 6.1 節） |
| 合成音声の聞き取り検査（check_asr.py、faster-whisper small） | 確認済み。認識側の算用数字・英字を台本の表記にそろえてから比べる版で、第5回の edge-tts 64 枚が CER 0〜7.6%（平均 2.4%）。結果は `work_*/asr/` に残す |
| 第5回の台本（narration.md、64 枚 約 13,700 字）と edge-tts の仮動画（45.1 分、mp4/srt/timings） | 確認済み（2026-10-22）。数字は漢数字、専門用語と外来語は XTTS が読める表記（`台本の書き方.md` 2.1 節）。srt と timings はスライドの隣に commit、mp4 はローカルのみ |
| ElevenLabs IVC / PVC | API 呼び出しの実装のみ。アカウント・課金は講師の判断で未実施 |
| 本人の実録音からの抽出（enroll 録音なし） | 確認済み（2026-10-22）。PLAUD の録音 5 本のうち文字起こしが雑音だった 1 本を除く 4 本で、`find_self.py --anchor` が本人のクラスターを 4/4 本で見つけ（anchor との類似度 0.74〜0.79、他人は 0.35 以下）、`verify_enroll.py` で 7/7 区間が文字起こしと一致。`extract_speaker.py` で本人の発話 690 本 73 分を切り出し、`prepare_reference.py` で XTTS 用 3 本と IVC 用 2.5 分を作成（本人との類似度 0.91〜0.98）。音声はローカルのみ |
| XTTS v2 を本人の実声で合成 | 確認済み（2026-10-22）。表紙の台本 133 字 → 24.3 秒、本人との類似度 0.69、CER 4.3%。算用数字が読まれないので台本は漢数字・仮名で書く（指南書 3 章） |
| XTTS v2 で書き直した台本の 3 枚（1・27・37）を本人の声で合成 | 確認済み（2026-10-22）。507 字 → 音声 93 秒。本人（参照音声）との類似度 0.64〜0.66、CER 0.9〜6.7%（平均 3.2%）。こさいん・せい・イキョ等の表記が意図どおりに読まれた。1・37 枚目の合成 55 秒分が 264 秒（モデル読込込み、RTF 4.8、空きメモリ 1.9 GB） |
| XTTS v2 で第5回 64 枚の全体を合成 | 未実施（CPU で 8〜10 時間、空きメモリ 2.5 GB 以上が必要。指南書 8 章のコマンド） |
