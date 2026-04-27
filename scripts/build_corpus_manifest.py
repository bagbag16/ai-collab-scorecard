#!/usr/bin/env python3
"""Build a repeatable corpus manifest from user-authorized source paths."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


DEFAULT_EXTENSIONS = {
    ".json",
    ".jsonl",
    ".md",
    ".txt",
    ".log",
    ".html",
    ".htm",
    ".patch",
    ".diff",
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".ps1",
    ".yaml",
    ".yml",
    ".csv",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def infer_kind(path: Path) -> str:
    name = path.name.lower()
    suffix = path.suffix.lower()
    if "codex" in str(path).lower() or "session" in name or suffix in {".jsonl", ".json"}:
        return "codex-session"
    if suffix in {".patch", ".diff"}:
        return "diff"
    if suffix in {".log"}:
        return "tool-log"
    if suffix in {".py", ".js", ".ts", ".tsx", ".jsx", ".ps1", ".yaml", ".yml"}:
        return "artifact"
    return "other"


def iter_files(sources: Iterable[Path], recursive: bool) -> Iterable[Path]:
    for source in sources:
        if source.is_file():
            yield source
        elif source.is_dir():
            pattern = "**/*" if recursive else "*"
            for path in source.glob(pattern):
                if path.is_file():
                    yield path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subject-id", required=True)
    parser.add_argument("--source", action="append", required=True, type=Path)
    parser.add_argument("--start", default="")
    parser.add_argument("--end", default="")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--non-recursive", action="store_true")
    parser.add_argument("--max-mb", type=float, default=50.0)
    parser.add_argument("--include-ext", action="append", default=[])
    args = parser.parse_args()

    allowed_exts = set(DEFAULT_EXTENSIONS)
    allowed_exts.update(ext.lower() if ext.startswith(".") else "." + ext.lower() for ext in args.include_ext)
    max_bytes = int(args.max_mb * 1024 * 1024)

    sources = []
    exclusions = []
    seen = set()
    source_roots = [path.resolve() for path in args.source]

    for source in source_roots:
        if not source.exists():
            exclusions.append({"path_or_id": str(source), "reason": "missing"})
            continue
        for path in iter_files([source], recursive=not args.non_recursive):
            resolved = path.resolve()
            key = str(resolved).lower()
            if key in seen:
                exclusions.append({"path_or_id": str(resolved), "reason": "duplicate"})
                continue
            seen.add(key)
            try:
                stat = resolved.stat()
            except OSError as exc:
                exclusions.append({"path_or_id": str(resolved), "reason": f"unreadable:{exc.__class__.__name__}"})
                continue
            if resolved.suffix.lower() not in allowed_exts:
                exclusions.append({"path_or_id": str(resolved), "reason": "unsupported-extension"})
                continue
            if stat.st_size > max_bytes:
                exclusions.append({"path_or_id": str(resolved), "reason": "too-large"})
                continue
            try:
                digest = sha256(resolved)
            except OSError as exc:
                exclusions.append({"path_or_id": str(resolved), "reason": f"hash-failed:{exc.__class__.__name__}"})
                continue
            sources.append(
                {
                    "path_or_id": str(resolved),
                    "kind": infer_kind(resolved),
                    "size_bytes": stat.st_size,
                    "sha256": digest,
                    "modified_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                    "included": True,
                    "reason": "authorized source path",
                }
            )

    manifest = {
        "schema_version": 1,
        "subject_id": args.subject_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "time_window": {"start": args.start, "end": args.end},
        "source_roots": [str(path) for path in source_roots],
        "sources": sorted(sources, key=lambda item: item["path_or_id"].lower()),
        "exclusions": sorted(exclusions, key=lambda item: item["path_or_id"].lower()),
    }
    manifest["source_count"] = len(manifest["sources"])
    stable_hash_basis = {
        k: v for k, v in manifest.items()
        if k not in {"created_at", "manifest_sha256"}
    }
    manifest["manifest_sha256"] = hashlib.sha256(
        json.dumps(stable_hash_basis, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest().upper()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "source_count": manifest["source_count"], "out": str(args.out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
