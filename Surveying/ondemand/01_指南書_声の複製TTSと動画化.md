# 指南書：講師の声に似せた TTS ナレーションでオンデマンド講義動画を作る

対象: AI エージェント（Claude Code / Codex）と、TTS を初めて扱う講師。
目的: 講義スライド（pptx）と台本（Markdown）から、講師本人の声に似せたナレーション付きの動画（mp4 + 字幕 srt）を作る。最初の対象は **第5回 トラバース測量 I**。
前提: この文書のコマンドはリポジトリの `Surveying/` を作業ディレクトリとして実行する。文書内の `<...>` は実行時に置き換える。

## 0. 守ること（最初に読む）

1. **本人の声の音声は commit しない。** `ondemand/voice/` と `ondemand/work/`、音声・動画の拡張子は `ondemand/.gitignore` で除外済み。別の場所に音声を置くときも commit しない。
2. **他人の声をクラウド（ElevenLabs 等）に上げない。** 会議録音は同僚・学生・外部の人の声を含む。アップロードするのは `extract_speaker.py` → `prepare_reference.py` で本人の区間だけにした参照音声に限る。切り出し後も、必ず聞いて他人の声が混ざっていないか確かめる。
3. **複製するのは講師本人の声だけ。** 本人の依頼（この作業の発端）に基づく。動画の冒頭か概要欄に「ナレーションは講師の声をもとに合成した音声」と明記する。
4. **API キー・トークンは環境変数か `C:\MyProjects\auto-tools\audio2md\.env` に置き、値を文書・ログ・commit に書かない。**
5. **公開リポジトリ**なので、個人名・メール・会議の内容（文字起こしの text）を文書に転記しない。`index.csv` の text 列は `voice/` 内にだけ残す。
6. 50 MB を超えるファイル（動画・録音・モデル）は commit しない。完成した動画の置き場所は `notes/worklog.md` に書く。

## 1. 環境を整える

### 1.1 何がどこで動くか

| 処理 | 使う Python | 理由 |
| --- | --- | --- |
| edge-tts、台本抽出、動画化（ffmpeg）、PLAUD ダウンロード | システムの `python`（3.11） | 軽い。edge-tts と python-pptx は入っている |
| XTTS v2、speechbrain（話者判定）、voice_similarity | 仮想環境 `%USERPROFILE%\.venvs\ondemand-tts` | torch 等 3 GB 超。システムを汚さない |
| ElevenLabs | どちらでも | 標準ライブラリ（urllib）だけで呼ぶ |

以下、仮想環境の python を `$PY` と書く。PowerShell では `$PY = "$env:USERPROFILE\.venvs\ondemand-tts\Scripts\python.exe"`、bash では `PY="$HOME/.venvs/ondemand-tts/Scripts/python.exe"`。

### 1.2 確認（既に構築済みの PC ではここだけ）

```powershell
python -c "import edge_tts, pptx; print('system ok')"
ffmpeg -version | Select-Object -First 1
& $PY -c "import torch, TTS, speechbrain, soundfile; print('venv ok', torch.__version__, TTS.__version__)"
```

3 行とも通れば 1.3 は飛ばす。

### 1.3 構築（新しい PC、または venv が無いとき）

```powershell
python -m venv "$env:USERPROFILE\.venvs\ondemand-tts"
& $PY -m pip install --upgrade pip
& $PY -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
& $PY -m pip install "coqui-tts[ja]" "coqui-tts[codec]" speechbrain soundfile edge-tts faster-whisper
python -m pip install edge-tts python-pptx
```

- 所要: 10〜20 分（torch 約 200 MB、依存を含め 3 GB 超）。
- `coqui-tts[codec]`（torchcodec）は `import TTS` の起動チェックのためだけに入れる。Windows の static ビルド ffmpeg では torchcodec の DLL が読めないが、`scripts/ondemand/audio_io.py` が `torchaudio.load` を soundfile に差し替えるので実行には支障ない（1.4）。
- ffmpeg が無ければ `winget install Gyan.FFmpeg`。PowerPoint が無い PC ではスライド PNG を別の PC で作る。

### 1.4 既知の問題と対処（この PC で 2026-10-22 に遭遇したもの）

| 症状 | 原因 | 対処（実装済み） |
| --- | --- | --- |
| speechbrain のモデル取得で `OSError: symbolic link` | Windows はシンボリックリンクに特権が要る | `extract_speaker.py` は `LocalStrategy.COPY` で `~/.cache/speechbrain/` に複製する |
| `Could not load libtorchcodec` / `libtorchcodec_core*.dll` | torchcodec が FFmpeg の共有 DLL を要求。winget の ffmpeg は static | `audio_io.patch_torchaudio_load()` で `torchaudio.load` を soundfile 実装に差し替え。XTTS・speechbrain の読み込みはこれで動く |
| `import TTS` が `TORCHCODEC_IMPORT_ERROR` | torchcodec 未インストール | `pip install "coqui-tts[codec]"`（DLL が読めなくても import は通る） |
| XTTS 初回起動が長い | モデル 1.9 GB のダウンロード | 回線次第で数分〜。2 回目以降は `~/.cache/huggingface/hub/models--tts-hub--XTTS-v2` を使う |
| XTTS の警告 `exceeds the character limit of 71` | 日本語は 1 文 71 字まで | 台本の 1 文を 60 字以内にする（`台本の書き方.md`）。`split_sentences=True` は実装済み |
| PowerPoint の PNG 書き出しが失敗 | 空の `preview/` を事前に作った | `preview/` を消してから `pptx_export.ps1` を実行 |
| edge-tts が音声を返さない | Microsoft 側の仕様変更 | `python -m pip install -U edge-tts` |

## 2. 全体の流れと所要時間の目安

| 段階 | 入力 → 出力 | 時間の目安（90 分の講義） |
| --- | --- | --- |
| A. 台本 | pptx の発表者ノート → `narration.md` を読み上げ用に書き直す | 2〜4 時間（人または LLM。内容の正しさは講師が確認） |
| B. 仮動画（edge-tts） | narration.md + PNG → mp4/srt | 10 分（合成は数分） |
| C. 声の素材 | PLAUD 録音 + Circleback 文字起こし → 本人の区間 → 参照音声 | 1〜2 時間（録音 3〜5 本分） |
| D. 声の複製 | 参照音声 → XTTS（ローカル）/ ElevenLabs（クラウド）で合成 | XTTS: CPU で音声時間の約 10 倍 / ElevenLabs: 数分 |
| E. 本番動画 | 複製した声で mp4/srt、点検、章立て | 1 時間 + 合成時間 |

A と C は独立。B を先に作って台本を直し切ってから D に進むと、合成のやり直しが減る。

## 3. 台本（narration.md）を作る

1. スライドを用意する。第5回は 2026-10-22 時点で Marp 形式の下書き `materials/slides/第05回_トラバース測量I/slides.md`（約 64 枚、各枚に `<!-- -->` の発表者ノート付き。別セッションが作成中で未コミット）がある。無い回は講義計画 `materials/lecture_plan_13.md` と既存回の作り方（`materials/slides/第03回_測量の座標/README.md`）に従って作る。pptx と PNG は第3回と同じ手順で作る（Marp CLI の pptx 書き出しはこの PC では動かない）。

```powershell
python scripts/md2pptx.py "materials/slides/第05回_トラバース測量I/slides.md" -o "materials/slides/第05回_トラバース測量I/slides.pptx"
powershell -ExecutionPolicy Bypass -File scripts/pptx_export.ps1 -Pptx "materials/slides/第05回_トラバース測量I/slides.pptx" -PngDir "materials/slides/第05回_トラバース測量I/preview"
```

2. 発表者ノートから下書きを作る。Marp の `slides.md` を直接渡しても（`<!-- -->` を発表者ノートとして読む）、md2pptx.py で作った pptx を渡してもよい。枚数の数え方は md2pptx.py と同じなので、PNG の番号と一致する。

```powershell
python scripts/ondemand/extract_notes.py "materials/slides/第05回_トラバース測量I/slides.md" -o "materials/slides/第05回_トラバース測量I/narration.md"
```

3. `ondemand/台本の書き方.md` に従って書き直す。要点: `## N` がスライド番号、1 文 60 字以内、記号・式・単位・略語は仮名で書き下す（(n−2)×180° → エヌ引く二、かける百八十度）、各スライド 150〜350 字。**算用数字は漢数字か仮名にする**（第5回 → 第五回、2つ → ふたつ、180 度 → 百八十度）。XTTS の日本語前処理は cutlet のローマ字変換だけで算用数字を読みに展開しないため、2026-10-22 の試作で「第5回」が「だいかい」、「2つ」が「き」と読まれた（edge-tts と ElevenLabs は算用数字を読めるが、台本は 1 本にしたいので最初から書き下す）。
   XTTS 向けの表記の規則（2026-10-22 に第5回 64 枚で確かめたもの。表は `台本の書き方.md` の 2 章）:
   - 専門用語は cutlet が誤読するので仮名で書く: 緯距・経距 → イキョ・ケイキョ、後視 → こうし、野帳 → やちょう、夾角 → きょうかく、真北 → しんぽく、極座標 → きょく座標、十進 → じっしん、一周 → いっしゅう、一筆書き → ひとふでがき、左偏・右偏 → さへん・うへん、水平角 → すいへいかく、n 角形 → エヌかくけい、一行 → いちぎょう、一本 → いっぽん。
   - 符号の「正」は「せい」と書く（単独の「正」は Tadashi と読まれる。正反観測・補正・訂正はそのまま）。度分秒を単独で並べるときは「ど、ふん、びょう」（「度、分、秒」は tabi・bun になる）。
   - 片仮名の外来語は cutlet が英語つづりに戻す。XTTS が読めるもの（タンジェント、アークタンジェント、モード、スライド、プログラム、ルート、センチメートル、シグマ、イプシロン、プラスマイナス）はそのまま、読めないものは平仮名にする（コサイン → こさいん、サイン → さいん）か別の語にする（ミス → 誤り、イラスト → 絵・概念図、本スライド → このスライド）。
   - 「イキョ」「ケイキョ」の直後に句読点を置かない（ョ が落ちて Iki・cake になる）。「イキョとケイキョの計算、」のように助詞や語を続ける。片仮名の読みを連結すると別の語に切られる（デルタビー → Deru Tabii、エックスエー → sway）ので「デルタ ビー」「エックス エー」と空白で区切る。
4. cutlet で機械的に確かめる。台本全体をローマ字にして、`?`（読めない漢字）と上の誤読（Tadashi、Iki、cake、cosine、Goshi …）が無いことを見る。疑わしい語は XTTS で 1 文だけ合成し、faster-whisper で聞き取って比べる（6.4 の `check_asr.py --wav --text`）。2026-10-22 の第5回はこの手順で 30 語ほど直し、ローマ字の NG が 0 になってから合成した。

```powershell
& $PY -c "import cutlet,re,sys;t=open(sys.argv[1],encoding='utf-8').read();t=re.sub(r'<!--.*?-->','',t,flags=re.S);print(cutlet.Cutlet().romaji(t))" "materials/slides/第05回_トラバース測量I/narration.md" > ondemand/work/narration_romaji.txt
```

5. `TODO` が残っていないことを確認する（残ると無音 2 秒になる）。

```powershell
python scripts/ondemand/build_video.py --narration "materials/slides/第05回_トラバース測量I/narration.md" --png-dir "materials/slides/第05回_トラバース測量I/preview" --out ondemand/work/lecture05_edge.mp4 --dry-run
```

## 4. まず edge-tts で仮動画を作る（声の複製なし）

```powershell
# スライド PNG（1280x720、「スライド1.PNG」…）。preview/ は事前に作らない
powershell -ExecutionPolicy Bypass -File scripts/pptx_export.ps1 -Pptx "materials/slides/第05回_トラバース測量I/slides.pptx" -PngDir "materials/slides/第05回_トラバース測量I/preview"
# 動画
python scripts/ondemand/build_video.py --narration "materials/slides/第05回_トラバース測量I/narration.md" --png-dir "materials/slides/第05回_トラバース測量I/preview" --out ondemand/work/lecture05_edge.mp4 --engine edge --voice ja-JP-KeitaNeural --rate -5%
```

- 出力: `lecture05_edge.mp4`、`lecture05_edge.srt`、`lecture05_edge.timings.json`（スライドごとの開始秒。章立てに使う）。作業ファイルは `ondemand/work/work_lecture05_edge/`。
- 聞いて直す: 誤読・不自然な間は台本側を直して再実行する。変えたスライドだけ再合成される（manifest.json によるキャッシュ）。特定の枚を強制的に作り直すなら `--only 3,5`。
- 声の候補: 男性 `ja-JP-KeitaNeural`、女性 `ja-JP-NanamiNeural`。`--rate -5%`〜`-10%` で講義向けにややゆっくり。
- 点検のしかた: `ffmpeg -ss <秒> -i <mp4> -frames:v 1 frame.png` で任意の時刻の画面を取り出して見る。`ffprobe` で動画長と音声長が同じことを確認する。

ここまでで「動画としては完成」。以降は声を本人に似せる工程。

## 5. 本人の声の素材を作る

### 5.1 方針

- 材料は 2 系統。**(a) 本人だけの短い録音（enroll）**: 話者判定の基準と、XTTS / IVC の参照に直接使える。**(b) 会議録音（PLAUD → Circleback）**: 量はあるが他人の声・雑音が混ざる。(a) を基準に (b) から本人の区間だけを切り出す。
- (a) が無いとき、`extract_speaker.py` 単体では「最も長く話している人 = 装着者（本人）」とみなすが、会議では外れる。録音が 3 本以上あるなら **5.7 の `find_self.py`** で会議をまたいで本人を見つけ、その出力 `auto_enroll.wav` を (a) の代わりに使う。PC のマイクで録れるなら (a) を作る方が確実で早い。
- 録音の圧縮が強い（PLAUD クラウドの音声は Opus 約 32 kbps）ので、声の似方を上げたいなら (a) を PC のマイクで WAV 録音し、量（PVC 用 30 分以上）もそこで稼ぐのが結局早い。

### 5.2 (a) enroll 録音を作る

静かな部屋で、普段の講義の調子で 2〜3 分（できれば第5回の台本の冒頭を読む）。

```powershell
# 方法 1: ffmpeg で PC のマイクから録る（デバイス名は一覧で確認）
ffmpeg -list_devices true -f dshow -i dummy
ffmpeg -f dshow -i audio="<マイク名>" -ac 1 -ar 44100 -t 180 ondemand/voice/enroll/enroll_raw.wav
# 方法 2: Windows の「サウンド レコーダー」で録って m4a を変換
ffmpeg -i "<録音.m4a>" -ac 1 -ar 44100 ondemand/voice/enroll/enroll_raw.wav
# 方法 3: PLAUD で一人で録って 5.3 の手順でダウンロード（音質は劣る）
# 整音（ハイパス + 音量正規化）して enroll.wav に
ffmpeg -i ondemand/voice/enroll/enroll_raw.wav -af "highpass=f=80,loudnorm=I=-19:TP=-3:LRA=11" -ac 1 -ar 44100 ondemand/voice/enroll/enroll.wav
```

確認: `ffprobe ondemand/voice/enroll/enroll.wav` で 120 秒以上あること。再生して雑音・途切れが無いこと。

### 5.3 (b) PLAUD の録音をダウンロードする

```powershell
python scripts/ondemand/plaud_download.py list --limit 50
#   id  開始日時(ローカル)  長さ(分)  サイズ(MB)  ファイル名
python scripts/ondemand/plaud_download.py get <id1> <id2> --out ondemand/voice/raw
```

- 選ぶ録音: 本人が長く話している回（講義・説明・一人での打ち合わせ）を 3〜5 本。雑踏・車内は避ける。
- 保存名は `<開始日時>_<id>.ogg`（中身を見て拡張子を決める。実体は Ogg/Opus が多い）。300 分の録音で約 72 MB。
- トークンは `C:\MyProjects\auto-tools\audio2md\.env` の `PLAUD_TOKEN`（2027-01-01 まで）。切れたら audio2md の手順で更新する。

### 5.4 (b) Circleback の文字起こし（話者分離済み）を取る

PLAUD の録音は Circleback に自動で取り込まれ、話者分離（"Participant N"）付きの文字起こしになっている。

```powershell
cd C:\MyProjects\auto-tools\audio2md
python tools\circleback_transcript.py check-auth
python tools\circleback_transcript.py list --since 2026-09-01      # 会議一覧（新しい順）。linkId と日時と長さ
python tools\circleback_transcript.py fetch <linkId> --json         # data\transcripts\<日付>_<linkId>.md と .json
cd <Surveying に戻る>
```

- PLAUD の録音と Circleback の会議は **日付と長さ（duration）** で突き合わせる（Circleback の `createdAt` は UTC）。
- JSON の形: `segments[] = {id, speaker: "Participant N", start, end, text}`（秒）。`stats.speakers` に話者一覧。
- セッショントークン `CIRCLEBACK_SESSION` は 2026-11-19 まで。切れたら `tools\refresh_circleback_token.py`。
- 一覧だけなら Claude Code のスキル `circleback-access` でもよい。
- **注意（2026-10-22 に確認）**: `list` は `--since` やページ指定に関わらず **最新 20 件しか返さない**（ページ送りが効かず同じページを繰り返す）。それより古い会議は Circleback の画面で linkId を調べて `fetch` する。`fetch` は全区間を返す（`meeting.duration` と最後の区間の `end` が一致すれば完全）。
- PLAUD の録音と Circleback の会議は、PLAUD の開始日時（ローカル）と `createdAt`（UTC → +9 時間）が一致し、長さが ±1% で合うものを組にする。`find_self.py`（5.7）はこの長さの一致で自動で組にする。
- 取得した JSON と md は `ondemand/voice/raw/transcripts/` に置く。会議名に人名が入るので commit しない（`voice/` は .gitignore 済み）。

### 5.5 本人の区間を切り出す

```powershell
# まず話者ごとの発話量を見る
& $PY scripts/ondemand/extract_speaker.py --audio ondemand/voice/raw/<録音>.ogg --segments C:\MyProjects\auto-tools\audio2md\data\transcripts\<日付>_<linkId>.json --out ondemand/voice/segments/<日付> --stats-only
# enroll で本人を判定して切り出す（speechbrain ECAPA。初回はモデル 80 MB を取得）
& $PY scripts/ondemand/extract_speaker.py --audio ondemand/voice/raw/<録音>.ogg --segments <同上>.json --out ondemand/voice/segments/<日付> --enroll ondemand/voice/enroll/enroll.wav --min-dur 3 --max-dur 15 --max-total 1800 --min-sim 0.5
```

出力: `seg_0001.wav …`、`index.csv`（file, start, end, dur, sim, text）、`meta.json`（判定した Participant と各話者の類似度）。
Circleback の話者区間は粗く無音を多く含むので、切り出しは Silero VAD で **発話だけの区間（min-dur〜max-dur 秒）** に割ってから行う（`vad_util.py`。5.7 の `cache/<id>.16k.wav` を `--wav16` で渡せば VAD の結果 `<id>.vad.json` も再利用する）。`--min-sim 0.5` で enroll に似ない区間（他人の声、重なり）を捨てる。

2026-10-22 の実行記録（enroll は 5.7 の `auto_enroll.wav`、`--min-dur 3 --max-dur 15 --max-total 1800 --min-sim 0.5`）: 録音 4 本で本人の判定は中央値 0.86 / 0.86 / 0.51 / 0.75、2 位の話者は 0.41 / 0.32 / 0.33 / 0.25 で、どれも find_self.py の self_map.json と同じ話者だった。切り出しは 306 本 30.0 分、265 本 30.1 分、17 本 2.2 分、102 本 11.2 分（合計 690 本 73 分、1 本 10〜12 分の処理）。無作為に選んだ区間を音声認識で読み直すと、前 2 本は 8/8 が文字起こしと一致、3 本目（本人がエージェントに口頭で指示している録音、録音機から遠い）は 6 本中 2 本が類似度 0.55 前後で不一致だったので、参照音声には `--min-sim 0.6` 以上を使う（下の 5.6）。

判定の読み方:

- 類似度は 1 に近いほど同一人物。本人の中央値が **0.5 以上**で、2 位との差が **0.1 以上**なら信頼してよい。差が小さいと警告が出る。その場合は `--participant "Participant 2"` のように人が決める。
- **時刻ずれの確認**: `seg_0001.wav` など 2〜3 本を再生し、`index.csv` の text と合っているか聞く。ずれていれば `--offset <秒>` を付けて切り直す。
- `sim` 列が 0.45 未満の区間は他人の声の重なりか雑音が多い。次の 5.6 で `--min-sim 0.5` で落とす。
- 切り出した区間を数本ランダムに再生し、**他人の声が入っていないことを耳で確認**する（クラウドに上げる前の必須手順）。

### 5.6 参照音声を作る

```powershell
# XTTS 用（10〜20 秒の良い区間を 3 本、22.05 kHz）
python scripts/ondemand/prepare_reference.py --in ondemand/voice/segments/<日付1> ondemand/voice/segments/<日付2> --out ondemand/voice/reference --target xtts --min-sim 0.5 --n 3
# ElevenLabs IVC 用（良い区間を 2.5 分まで連結、mp3 192 kbps）
python scripts/ondemand/prepare_reference.py --in ondemand/voice/segments/<日付1> ondemand/voice/segments/<日付2> --out ondemand/voice/reference --target ivc --min-sim 0.5 --minutes 2.5
# ElevenLabs PVC 用（全部連結して 10 分ごとに分割。合計 30 分以上）
python scripts/ondemand/prepare_reference.py --in ondemand/voice/segments/* --out ondemand/voice/reference --target pvc --min-sim 0.5 --chunk 10
```

- 整音は控えめ（ハイパス 80 Hz + loudnorm）。雑音が気になる録音だけ `--denoise`（afftdn）を付ける。かけ過ぎると声が変わる。
- enroll 録音が良質なら、それ自体を XTTS の参照（10〜20 秒を切り出して 22.05 kHz）や IVC の参照（1〜3 分）に使ってよい。会議録音より似ることが多い。
- 参照の品質確認: `& $PY scripts/ondemand/voice_similarity.py --ref ondemand/voice/enroll/enroll.wav ondemand/voice/reference/xtts_ref_01.wav ...` で 0.6 以上を目安にする。
- 2026-10-22 の実行記録: 5.5 の 4 日分（690 本）に `--min-sim 0.6` で 592 本 66 分が残り、`xtts_ref_01〜03.wav`（15 秒 ×3、`auto_enroll.wav` との類似度 0.91〜0.93）と `ivc_reference.mp3`（12 本 2.5 分、類似度 0.98）ができた。enroll が `auto_enroll.wav`（会議録音から集めたもの）のときは類似度が全体に高めに出るので、閾値は 0.5 でなく 0.6 にする。

### 5.7 enroll 録音が無いとき: 会議録音だけから本人を見つける（find_self.py）

Circleback の話者ラベル（Participant N）は会議ごとに振り直されるので、会議をまたいで同じ人を追えない。しかし録音機の装着者（本人）は全部の録音に出ている。`find_self.py` は録音ごと・話者ごとに声の埋め込み（speechbrain ECAPA）の代表ベクトルを作り、会議をまたいでクラスタリングして、本人のクラスターを決める。

**2026-10-22 に分かった落とし穴（スクリプトは対処済み）:**

1. **Circleback の話者区間は粗い。** 1 区間が数分に及び、その大半が無音のことがある（本人がエージェントに口頭で指示している録音では、1 区間 409 秒のうち発話は 30 秒ほど）。区間の先頭 15 秒をそのまま埋め込むと無音を埋め込み、録音機の暗騒音どうしが「全部の録音に共通する声」として選ばれた（最初の `auto_enroll.wav` は音声認識にかけても言葉にならなかった）。→ 今は Silero VAD（`vad_util.py`、faster-whisper 同梱）で **発話区間だけに割ってから** 埋め込む。
2. **雑音を英語の無意味な文に起こした録音がある**（10/12 の録音は全話者がそれだった）。→ 文字起こしの日本語文字がラテン文字より少ない区間は使わず、その割合が 5 割を切る話者は除く（`--min-ja-ratio`）。
3. **「最も多くの録音に出た声」は本人とは限らない。** 本人が黙って聞いている会議では同僚のほうが多く話し、同じ同僚が 3 本に出ていた。三人称の姓の言及（`--not-self-regex`）も、同僚が本人に向かって「〇〇先生は…」と話す・本人が同姓の別人の話をする、で当てにならなかった。→ 録音を 1 本選び、**内容から本人と確定できる話者**（例: エージェントへの口頭指示、講義）を `--anchor "<録音 id の先頭 8 桁>:Participant N"` で渡す。そのクラスターを本人とし、全話者の anchor との類似度の表を出す。

準備: 5.3 で録音 3〜5 本を `ondemand/voice/raw/` に、5.4 でその文字起こし JSON を `ondemand/voice/raw/transcripts/` に置く。録音と JSON は長さ（±1%）で自動で組にし、組を最初に表示する。anchor にする話者は、文字起こし JSON を読んで決める（本人しかいない状況の録音が最良。2026-10-22 は 10/16 の「エージェントに指示している録音」の Participant 2 を使い、音声認識で読み直して文字起こしと一致することを確かめた）。

```powershell
# 空きメモリを確認（3 GB 未満ならブラウザー等を閉じる。話者モデルで約 1 GB 使う。録音全体はメモリに載せない）
Get-CimInstance Win32_OperatingSystem | % { "{0:N1} GB free" -f ($_.FreePhysicalMemory/1MB) }
$env:PYTHONUTF8 = "1"
# 1 回目: anchor なしで表を見る（本人が決まらなくてもよい）
& $PY -u scripts/ondemand/find_self.py --audio-dir ondemand/voice/raw --transcripts ondemand/voice/raw/transcripts --out ondemand/voice/self_search --per-spk 30 --not-self-regex "<姓>(先生|さん)"
# 2 回目: 内容から本人と分かった話者を anchor にする（埋め込みは cache/ にあるので数十秒で終わる）
& $PY -u scripts/ondemand/find_self.py --audio-dir ondemand/voice/raw --transcripts ondemand/voice/raw/transcripts --out ondemand/voice/self_search --per-spk 30 --not-self-regex "<姓>(先生|さん)" --anchor "<id 先頭 8 桁>:Participant N"
# 検証: enroll に使った区間を音声認識で読み直し、文字起こしと一致するか（7 区間中 5 以上で合格）
& $PY -u scripts/ondemand/verify_enroll.py --self-search ondemand/voice/self_search --whole
```

- 出力 `ondemand/voice/self_search/`: `report.md`（クラスターの表、anchor との類似度の表）、`self_map.json`（録音ごとの本人ラベルと類似度）、`auto_enroll.wav`（本人クラスターの代表に近い発話区間を会議をまたいで集めた約 90〜100 秒、16 kHz）、`enroll_segments.json`（その区間の一覧）、`enroll_check.md`（verify_enroll.py の結果）、`cache/`（録音ごとの 16 kHz WAV `<id>.16k.wav`、VAD の発話区間 `<id>.vad.json`、埋め込み `<id>.units.json`。**途中で止まっても再実行すれば済んだ録音は飛ばす**。やり直すときは units.json だけ消す）。
- 採用の目安: anchor との類似度が **本人のラベルで 0.7 以上、他の話者で 0.4 以下**に分かれていること（2026-10-22: 本人 0.74〜0.79、他 0.06〜0.35、境界 0.60 が 1 つ）。本人クラスターに入った録音で本人が発話量 1 位になっているか（装着者はマイクに近い）。`verify_enroll.py` が合格で、認識結果を読んで本人の話（講義、研究指導、エージェントへの指示など）になっていること。
- `auto_enroll.wav` を **必ず再生して本人の声だけか確認**（人が聞けないときは `verify_enroll.py --whole` の認識結果で代用）してから、5.5 の `--enroll ondemand/voice/self_search/auto_enroll.wav` として使う。`--wav16 ondemand/voice/self_search/cache/<id>.16k.wav` を付けると 16 kHz への変換と VAD を省ける。
- 所要時間の目安: 録音 1 本（2〜3 時間）につき変換 1〜2 分 + VAD 15〜30 秒 + 埋め込み 1〜3 分（CPU）。5 本で 20 分ほど。
- 2026-10-22 の実行記録: 録音 5 本（10/12〜10/17、合計約 10 時間）。10/12 は文字起こしが雑音の誤認識で全話者除外。残り 4 本で anchor（10/16 の Participant 2）のクラスターが 4/4 本に出現、各録音で発話量 1 位の話者（45〜56%）が本人だった。`verify_enroll.py` は 7/7 区間で一致率 0.83〜0.98。

## 6. 声を複製して合成する

### 6.1 XTTS v2（ローカル、無料、試作向け）

```powershell
# 1 文で試す
& $PY scripts/ondemand/tts_synth.py --engine xtts --ref ondemand/voice/reference/xtts_ref_01.wav --ref ondemand/voice/reference/xtts_ref_02.wav --text "測量学 第5回、トラバース測量の1回目です。" --out ondemand/work/xtts_test.wav
# 動画（スライド数枚で試してから全体）
& $PY scripts/ondemand/build_video.py --narration <narration.md> --png-dir <preview> --out ondemand/work/lecture05_xtts.mp4 --engine xtts --ref ondemand/voice/reference/xtts_ref_01.wav --ref ondemand/voice/reference/xtts_ref_02.wav --only 1,2
```

- 実測（この PC、2026-10-22、合成音声を参照にした検証）: 日本語 80 字 → 音声 12.1 秒を 129 秒（モデル読込を含む、RTF 約 10.7）。モデル読込後だけを測ると 61 字 → 11.8 秒を 84 秒（RTF 7.1）、78 字 → 13.3 秒を 50 秒（RTF 3.8）。つまり読込を除けば RTF 4〜7 で、音声 60 分の講義なら 4〜7 時間。参照音声との話者類似度 0.81（同一話者の実音声どうしの 0.84 とほぼ同じ）。
- 聞き取りやすさ（`check_asr.py`、faster-whisper small で文字に戻した CER）: 上の XTTS 音声は 9.7%（読みで比較。文字のままなら 21.9%）、edge-tts で作った試作動画の 2 枚は 15.4% と 8.6%。音声認識側も同音の専門用語を取り違える（測角→即格、内角の和→内閣の輪）ので、`check_asr.py` は漢字を読みに直してから比べる。それでも「閉合→平均」のような取り違えは残るので、CER は絶対値でなく edge-tts との比較と、他の枚より目立って高いかで見る。
- 本人の実録音を参照にした実測（2026-10-22、`xtts_ref_01〜03.wav` の 3 本、空きメモリ 3.1 GB）: 第5回 表紙の台本 133 字 → 音声 24.3 秒を 248 秒（読込込み、RTF 10）。`auto_enroll.wav`（本人の実声）との話者類似度 0.69（参照音声そのものは 0.91〜0.93 なので、XTTS の出力は実声より一段似ていない。目安の 0.6 は超えた）。`check_asr.py` の CER 4.3%（読みで比較）。ただし算用数字が読まれず（第5回 → だいかい、2つ → き）、緯距は誤読された。台本は 3 章の規則（数字と専門用語を仮名・漢数字で書く）で書くこと。
- 台本を 3 章の規則で書き直したあとの実測（2026-10-22、第5回の 1・27・37 枚目、`ondemand/work/xtts_demo/`、空きメモリ 1.7〜1.9 GB でも落ちずに動いた）: 1 枚目 179 字 → 32.2 秒、27 枚目 195 字 → 37.8 秒、37 枚目 133 字 → 23.0 秒。1・37 枚目の作り直し（音声 55 秒分）がモデル読込込みで 264 秒（RTF 4.8）。参照音声（xtts_ref_01）との類似度 0.639 / 0.661 / 0.649（目安 0.6 以上）、`check_asr.py` の CER 2.0% / 0.9% / 6.7%（平均 3.2%。37 枚目の差は「北向き→キャムキ」など認識側の揺れで、こさいん・さいん・せい・イキョ・ケイキョは意図どおり読まれた）。
- 表記の候補（イキョの片仮名／平仮名／長音、英語つづりに戻る外来語 14 語、せい・ど ふん びょう）は 1 文ずつ XTTS で合成して faster-whisper で聞き取り、読めた表記だけを 3 章の規則にした（記録は `ondemand/work/xtts_demo/spelling_test*.txt`、ローカルのみ）。
- 90 分の講義（音声約 60 分）は約 10 時間。夜間に `--work` を固定して流し、途中で止まっても再実行すれば続きから（manifest.json）。第5回の全 64 枚（13,700 字、edge-tts で 45 分）なら RTF 10〜13 で 8〜10 時間。
- 似方が足りないときは、参照を変える（息継ぎのない 10〜15 秒、感情の平坦な区間）、本数を 2〜3 本にする、`--denoise` を外す／付ける、の順で試す。
- ライセンスは非商用（CPML）。学内配信の授業用途を超える公開には使わない。

### 6.2 ElevenLabs Instant Voice Clone（本番の第一候補）

手順（ブラウザー操作は講師が行う。エージェントは準備と合成を担当）:

1. ElevenLabs のアカウントを作り、有料プラン（IVC は Starter 以上、PVC は Creator 以上）にする。料金と月間文字数は https://elevenlabs.io/pricing で確認。
2. Voices → Add a new voice → Instant Voice Clone。`ondemand/voice/reference/ivc_reference.mp3`（または enroll 録音 1〜3 分）をアップロード。言語に Japanese、「自分の声である」旨の確認にチェック。
3. 作成した声の **voice_id** を控える（Voices の一覧 → ID をコピー）。
4. Profile → API Keys で API キーを作り、環境変数に入れる（値は書かない）。

```powershell
$env:ELEVENLABS_API_KEY = "<key>"      # そのセッションだけ。恒久化するなら audio2md の .env に ELEVENLABS_API_KEY=... を追記
python scripts/ondemand/tts_synth.py --engine elevenlabs --voice <voice_id> --text "測量学 第5回、トラバース測量の1回目です。" --out ondemand/work/eleven_test.wav
python scripts/ondemand/build_video.py --narration <narration.md> --png-dir <preview> --out ondemand/work/lecture05_eleven.mp4 --engine elevenlabs --voice <voice_id> --model-id eleven_multilingual_v2
```

- モデル: `eleven_multilingual_v2` が安定。表現力を上げるなら `--model-id eleven_v3`（読みの揺れを点検する）。
- 文字数: 90 分の台本で 1.2〜1.8 万字程度。プランの残り文字数を先に見る。合成は 1 スライドずつ呼ぶ（キャッシュが効く）。
- 似方の確認: `& $PY scripts/ondemand/voice_similarity.py --ref ondemand/voice/enroll/enroll.wav ondemand/work/eleven_test.wav`。0.6 以上なら実用、0.7 以上なら良好。

### 6.3 ElevenLabs Professional Voice Clone（似方を上げたいとき）

- 材料: 本人だけの音声 30 分以上（推奨 1〜3 時間）。`--target pvc` の出力（`pvc_part_NN.mp3`）か、PC のマイクで新たに読んだ録音。雑音・他人の声は厳禁。
- Voices → Add a new voice → Professional Voice Clone → ファイルをアップロード → 本人確認（画面の指定文を自分の声で録音）→ 学習（数時間〜1 日）。
- 学習後の voice_id で 6.2 と同じ手順。
- 録音の作り方（推奨）: 第5回の台本をそのまま読む。30〜60 分で材料になり、用語の読みも本人のものになる。

### 6.4 合成結果の点検（共通）

| 観点 | やり方 | 合格の目安 |
| --- | --- | --- |
| 誤読・途切れ（機械で） | `& $PY scripts/ondemand/check_asr.py --narration <narration.md> --work ondemand/work/work_<名前>` で音声認識（faster-whisper）に戻し、認識側の算用数字・ラテン文字を台本と同じ漢数字・片仮名にそろえ、漢字を読みに直して台本と比較。認識結果は `work_*/asr/` に残り、wav が変わらなければ使い回す | 2026-10-22 の第5回（edge-tts、64 枚）で 1 枚 0〜7.6%、平均 2.4%。8% を超える枚、他の枚より目立って高い枚、長い delete（途切れ）がある枚だけ人が聞く。15% 以上は「要確認」と差分が表示される |
| 誤読（人で） | 動画を通しで聞く、または字幕 srt と照合 | 専門用語の誤読ゼロ（台本側で仮名にして直す） |
| 似方 | `voice_similarity.py --ref enroll.wav <合成 wav>` | 0.6 以上 |
| 間・速度 | 1 分あたり 280〜330 字が講義の速さ。`timings.json` の speech 秒 ÷ 文字数で確認 | 速ければ台本に読点を足す（edge は `--rate`） |
| 音量 | `ffmpeg -i <mp4> -af loudnorm=print_format=summary -f null -` | 入力ラウドネス −20〜−16 LUFS |
| 画面 | 任意の時刻の静止画を取り出す | 文字あふれ・白縁の崩れがない |

## 7. 動画の仕上げと公開

- `build_video.py` の既定: 1280x720、10 fps（静止画なので十分）、H.264 crf 20、AAC 128 kbps、各スライドの前後に 0.3 / 0.8 秒の無音。90 分で約 90 MB。
- 章立て: `<out>.timings.json` のスライド開始秒から、動画の概要欄用に「00:00 表紙 / 01:20 到達目標 …」を作る。
- 字幕: `<out>.srt` は文字数比の近似。長い文を分ければ精度が上がる。LMS によっては srt を別途アップロードする。
- 演習パート: 「ここで一時停止して解いてください」の指示を台本に入れ、解答スライドは別の章にする（講義計画の演習 25 分）。
- 公開先（LMS、学内の動画配信、限定公開の動画サイト等）に上げたら、場所と日付を `notes/worklog.md` に記す。mp4 は commit しない。
- 冒頭か概要欄に「ナレーションは講師の声をもとにした合成音声です」と明記する。

## 8. 第5回 トラバース測量 I への適用手順（エージェント向けチェックリスト）

- [x] 第5回のスライドを作る（`materials/slides/第05回_トラバース測量I/`、64 枚、2026-10-22 済。講義計画: 到達目標・講義・演習 25 分・最新技術・試験の型は `materials/lecture_plan_13.md` の「第 5 回」）。
- [x] `extract_notes.py slides.md` → `narration.md` を `台本の書き方.md` の規則で書き直す（2026-10-22 済。64 枚、約 13,700 字、1 枚 130〜300 字。演習は一時停止の指示。数字は漢数字、専門用語と外来語は 3 章の表記、cutlet のローマ字で NG 0）。
- [x] `pptx_export.ps1` で PNG、`build_video.py --engine edge` で仮動画（2026-10-22 済。`ondemand/work/lecture05_edge.mp4`、45.1 分。`check_asr.py` で 64 枚とも CER 7.6% 以下、平均 2.4%。字幕と時刻は `narration_edge.srt` / `narration_edge.timings.json` としてスライドの隣に commit）。
- [x] enroll 録音（5.2）の代わりに 5.7 の `find_self.py --anchor` で `auto_enroll.wav` を作り、`verify_enroll.py` で本人の発話と確認（2026-10-22 済。`ondemand/voice/self_search/`、ローカルのみ）。講師が静かな enroll 録音をくれたらそちらに置き換える。
- [x] PLAUD 4 本 → Circleback JSON → `extract_speaker.py --enroll ondemand/voice/self_search/auto_enroll.wav --wav16 ... --min-sim 0.5`（690 本 73 分）→ 音声認識で確認 → `prepare_reference.py --min-sim 0.6 --target xtts` と `--target ivc`（2026-10-22 済。`ondemand/voice/reference/`、ローカルのみ。耳での確認は講師に依頼）。
- [x] XTTS で表紙 1 枚を試作し、似方 0.69（目安 0.6 以上）と誤読（算用数字が読まれない → 3 章の規則）を確認（2026-10-22 済。`ondemand/work/xtts_self_sample.wav`）。
- [x] 書き直した台本で 1・27・37 枚目を XTTS で合成し、本人との類似度と CER を確認（2026-10-22 済。`ondemand/work/xtts_demo/`、6.1 の実測）。
- [ ] 全 64 枚を XTTS で合成する: `powershell -ExecutionPolicy Bypass -File scripts/ondemand/build_xtts_full.ps1`（6.1 のコマンドを優先度 低の別プロセスで動かし `ondemand/work/build_xtts.log` に記録。CPU で 8〜10 時間。空きメモリ 2.5 GB 未満なら起動を断るので、他のアプリを閉じて夜間に流す。途中で止まったら同じコマンドで続きから。進み具合は log の `[tts] slide` 行の数）。終わったら `check_asr.py --work ondemand/work/work_lecture05_xtts` と `voice_similarity.py` で 6.4 の点検。
- [ ] 講師が ElevenLabs のプランと voice_id を用意したら、`--engine elevenlabs` で全体を合成。
- [ ] 6.4 の点検 → 章立て・字幕 → 公開先へ。`notes/worklog.md` に記録、`narration.md` と `timings.json` を commit（音声・動画は除く）。

## 9. 困ったとき

| 状況 | 対処 |
| --- | --- |
| 話者判定で本人が決まらない | enroll を 3 分以上の静かな録音にする。`--probe 40` で判定に使う区間を増やす。それでも駄目なら `--participant` で指定し、耳で確認 |
| `auto_enroll.wav` が言葉になっていない（verify_enroll.py が不合格） | 無音や雑音を埋め込んでいる。`cache/*.units.json` を消して再実行（VAD 版で作り直す）。文字起こしが英語の無意味な文の録音は除外されているか `report.md` で確認 |
| XTTS が数字を飛ばす（第5回 → だいかい） | XTTS の日本語前処理（cutlet）は算用数字を展開しない。台本の数字を漢数字・仮名に書き直す（3 章）。専門用語の誤読も同じく仮名で書く |
| XTTS が「正」を「ただし」、「度、分、秒」を「たび、ぶん」と読む | 符号の正は「せい」、単独で並べる度分秒は「ど、ふん、びょう」と書く（3 章）。台本全体を cutlet でローマ字にして Tadashi・tabi が無いか見る |
| XTTS が片仮名の外来語を英語風に読む（コサイン → コシン、ミス → ミステー） | cutlet が英語つづり（cosine、mistake）に戻している。平仮名（こさいん）か別の語（誤り）にする。読める語の一覧は 3 章 |
| XTTS が「イキョ、」を「イキ」と読む | 句読点の直前で ョ が落ちる。「イキョの計算、」のように語を続ける |
| check_asr.py の CER が 20% 以上なのに聞くと正しい | 認識側が算用数字・ラテン文字（360、TS）で書く表記差。2026-10-22 以降の check_asr.py は漢数字・片仮名にそろえてから比べる（edge-tts で平均 2〜3% になる） |
| find_self.py が同僚を本人にする | 本人が黙っている会議が多い。本人しか話していない録音（エージェントへの指示、講義）を 1 本入れ、その話者を `--anchor` で指定 |
| 切り出した区間に他人の声が混ざる | `--min-dur 4` で短い相づちを除く。`--min-sim` を上げる。会議の種類を変える（一人で話す録音を優先） |
| XTTS がメモリ不足で落ちる | 他のアプリを閉じる（モデルで約 3 GB）。`--only` で数枚ずつ。台本の 1 文を短くする |
| XTTS の日本語が途切れる | 1 文 71 字の上限。`。` を増やす |
| ElevenLabs が 401 / 402 | API キー、プランの文字数残を確認 |
| 動画と音声の長さが違う | `build_video.py` は `-t` で明示しているので起きないはず。起きたら `work_*/all.wav` の長さと `timings.json` の最後の end を比べる |
| PowerPoint の PNG が出ない | `preview/` を削除してから実行。PowerPoint が他のファイルを開いていたら閉じる |

## 10. ファイルと責任の対応

| ファイル | 役割 | 実行環境 |
| --- | --- | --- |
| `scripts/ondemand/extract_notes.py` | pptx のノート、または Marp slides.md の `<!-- -->` → narration.md の下書き | system |
| `scripts/ondemand/build_video.py` | narration.md + PNG → mp4/srt/timings | system（xtts のときは venv） |
| `scripts/ondemand/tts_synth.py` / `tts_backends.py` | TTS エンジン共通 | system（xtts は venv） |
| `scripts/ondemand/plaud_download.py` | PLAUD 一覧・取得 | system |
| `scripts/ondemand/extract_speaker.py` | 本人の区間の切り出し | venv |
| `scripts/ondemand/find_self.py` | enroll なしで会議録音をまたいで本人を見つける（5.7） | venv |
| `scripts/ondemand/verify_enroll.py` | auto_enroll.wav に使った区間を音声認識で読み直し、文字起こしと一致するか検証（5.7） | venv |
| `scripts/ondemand/vad_util.py` | Silero VAD で発話区間を出す補助（find_self / extract_speaker が使う） | venv（自動で使われる） |
| `scripts/ondemand/prepare_reference.py` | 参照音声の整音・連結 | system |
| `scripts/ondemand/voice_similarity.py` | 話者類似度の確認 | venv |
| `scripts/ondemand/check_asr.py` | 合成音声を音声認識に戻して台本と比較（誤読・途切れの検出）。認識側の数字・英字を台本の表記にそろえ、結果は `work_*/asr/` に残す | venv |
| `scripts/ondemand/audio_io.py` | torchaudio.load の差し替え | venv（自動で使われる） |
| `scripts/pptx_export.ps1` | pptx → PDF/PNG | PowerShell + PowerPoint |
| `ondemand/台本の書き方.md` | 台本の規則 | — |
| `ondemand/02_TTSと声の複製の選択肢_20261022.md` | 選択肢の比較と出典 | — |
