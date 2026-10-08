"""GitHub main取得後、Surveyingの全ファイルを読み取り照合する。削除しない。"""
import argparse
import csv
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path


def git(root, *args, data=None, check=True):
    return subprocess.run(
        ["git", "-C", str(root), *args], input=data,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check,
    ).stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", help="Surveying内のCSV保存先（省略時は読み取りのみ）")
    args = parser.parse_args()
    survey = Path(__file__).resolve().parents[1]
    root = Path(git(survey, "rev-parse", "--show-toplevel").decode().strip())
    prefix = survey.relative_to(root).as_posix() + "/"
    out = (survey / args.inventory).resolve() if args.inventory else None
    if out is not None and not out.is_relative_to(survey):
        raise RuntimeError("出力先はSurveying内に限定")
    remote = git(root, "rev-parse", "origin/main").decode().strip()
    advertised = git(root, "ls-remote", "origin", "refs/heads/main").decode().split()[0]
    if remote != advertised:
        raise RuntimeError("origin/mainがGitHub mainと異なります。git fetch origin main後に再実行してください")
    tree = {}
    for entry in git(root, "ls-tree", "-r", "-z", remote, "--", prefix).split(b"\0"):
        if not entry:
            continue
        meta, name = entry.split(b"\t", 1)
        mode, kind, oid = meta.decode().split()
        if kind != "blob":
            raise RuntimeError("通常ファイル以外のGitエントリを検出")
        tree[name.decode("utf-8")] = (mode, oid)
    tracked = set(x.decode("utf-8") for x in git(root, "ls-files", "-z", "--", prefix).split(b"\0") if x)
    local = {}
    links = []
    for path in survey.rglob("*"):
        if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
            links.append(path.relative_to(survey).as_posix())
        if path.is_file():
            if out is not None and path.resolve() == out:
                continue  # 一覧自身は保存で内容が変わるため、出力時だけ集計外。
            local[path.relative_to(root).as_posix()] = path
    # fetch済みコミットから全blobを読み出し、復元元の実体とSHA-256を検証。
    blobs = {}
    for _, oid in tree.values():
        if oid not in blobs:
            raw = git(root, "cat-file", "blob", oid)
            if hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() != oid:
                raise RuntimeError("Git blobハッシュ不一致")
            blobs[oid] = raw
    history = set(line.split(b" ", 1)[0].decode() for line in
                  git(root, "rev-list", "--objects", remote).splitlines())
    rows = []
    duplicate = {}
    for name, (_, oid) in tree.items():
        duplicate.setdefault(hashlib.sha256(blobs[oid]).hexdigest(), []).append(name[len(prefix):])
    for name in sorted(set(local) | set(tree)):
        path = local.get(name)
        raw = path.read_bytes() if path else None
        sha = hashlib.sha256(raw).hexdigest() if raw is not None else ""
        ignored = git(root, "check-ignore", "-v", "--", name, check=False).decode("utf-8").strip()
        target = tree.get(name)
        oid = target[1] if target else ""
        normalized = git(root, "hash-object", "--path=" + name, "--stdin", data=raw).decode().strip() if raw is not None else ""
        if path is None:
            status = "GitHubのみ（ローカル欠落）"
        elif target and raw == blobs[oid]:
            status = "完全一致"
        elif target and normalized == oid:
            status = "Git正規化後一致（改行等）"
        elif target:
            status = "GitHubと内容相違"
        elif name in tracked:
            status = "ローカル追跡のみ"
        elif ignored:
            status = "gitignore対象"
        else:
            status = "未追跡"
        pointer = bool(raw and raw.startswith(b"version https://git-lfs.github.com/spec/v1\n"))
        rows.append({
            "ファイル": name[len(prefix):], "判定": status,
            "ローカルバイト数": len(raw) if raw is not None else "",
            "ローカルSHA256": sha, "Git正規化blob": normalized,
            "GitHub_blob": oid,
            "GitHub_SHA256": hashlib.sha256(blobs[oid]).hexdigest() if oid else "",
            "除外規則": ignored,
            "GitHub内の同一バイト資料": " | ".join(duplicate.get(sha, [])) if not target else "",
            "GitHub_main履歴にblobあり": normalized in history,
            "50MB超": bool(raw is not None and len(raw) > 50_000_000),
            "LFSポインタ": pointer,
        })
    if args.inventory:
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    summary = {
        "GitHub_main": remote, "HEAD": git(root, "rev-parse", "HEAD").decode().strip(),
        "ローカルファイル数": len(local), "GitHubファイル数": len(tree),
        "判定件数": dict(Counter(r["判定"] for r in rows)),
        "シンボリックリンク等": links,
        "50MB超": [r["ファイル"] for r in rows if r["50MB超"]],
        "LFSポインタ": [r["ファイル"] for r in rows if r["LFSポインタ"]],
        "要確認": [r for r in rows if r["判定"] not in ("完全一致", "Git正規化後一致（改行等）")],
        "mainとorigin/mainの差": git(root, "rev-list", "--left-right", "--count", "main...origin/main").decode().strip(),
        "Surveyingの状態": git(root, "-c", "core.quotepath=false", "status", "--porcelain=v1", "--untracked-files=all", "--ignored", "--", prefix).decode("utf-8"),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
