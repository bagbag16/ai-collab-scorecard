from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)


def require(path: str) -> Path:
    candidate = ROOT / path
    if not candidate.exists():
        fail(f"Missing required path: {path}")
    return candidate


def load_json(path: str):
    candidate = require(path)
    if not candidate.exists():
        return {}
    try:
        return json.loads(candidate.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic path
        fail(f"Invalid JSON in {path}: {exc}")
        return {}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def check_skill_frontmatter() -> None:
    skill_path = require("SKILL.md")
    if not skill_path.exists():
        return
    text = skill_path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not match:
        fail("SKILL.md is missing YAML frontmatter")
        return
    frontmatter = match.group(1)
    name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.M)
    desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.M)
    if not name_match or name_match.group(1).strip() != "ai-collab-scorecard":
        fail("SKILL.md frontmatter name must be ai-collab-scorecard")
    if not desc_match or len(desc_match.group(1).strip()) < 80:
        fail("SKILL.md frontmatter description is missing or too short")


def check_required_structure() -> None:
    for path in [
        "README.md",
        "PRIVACY.md",
        "SECURITY.md",
        "CHANGELOG.md",
        "LICENSE",
        "CONTRIBUTING.md",
        "agents/openai.yaml",
        "references/rubric.md",
        "references/output-schema.md",
        "references/worktypes.md",
        "references/setup-and-data-sources.md",
        "references/share-copy.json",
        "references/render-lock.json",
        "scripts/bootstrap.ps1",
        "scripts/check_environment.ps1",
        "scripts/render_share_card_png.ps1",
        "scripts/self_check_render_determinism.ps1",
        "assets/fonts/NotoSansSC-VF.ttf",
        "assets/worktype-illustrations/manifest.json",
        "examples/sample-scorecard.json",
        "examples/sample-share-card.png",
        ".github/workflows/validate.yml",
    ]:
        require(path)


def check_assets() -> None:
    manifest = load_json("assets/worktype-illustrations/manifest.json")
    asset_root = manifest.get("asset_root", "assets/worktype-illustrations")
    types = manifest.get("types", {})
    if len(types) != 10:
        fail(f"Expected 10 worktype assets, found {len(types)}")
    for type_id, entry in types.items():
        if entry.get("status") != "confirmed":
            fail(f"Worktype asset is not confirmed: {type_id}")
        file_name = entry.get("file")
        if not file_name:
            fail(f"Worktype asset has no file: {type_id}")
            continue
        require(str(Path(asset_root) / file_name))


def check_render_lock() -> None:
    render_lock = load_json("references/render-lock.json")
    font = render_lock.get("font", {})
    font_path = require(font.get("path", "assets/fonts/NotoSansSC-VF.ttf"))
    expected_hash = str(font.get("sha256", "")).upper()
    if font_path.exists() and expected_hash and sha256(font_path) != expected_hash:
        fail("Pinned font hash does not match references/render-lock.json")
    fixture = render_lock.get("validation", {}).get("reference_fixture", {})
    if fixture.get("input"):
        require(fixture["input"])


def check_copybook_alignment() -> None:
    manifest = load_json("assets/worktype-illustrations/manifest.json")
    copybook = load_json("references/share-copy.json")
    manifest_types = set((manifest.get("types") or {}).keys())
    name_types = set((copybook.get("type_names") or {}).keys())
    copy_types = set((copybook.get("type_copy") or {}).keys())
    if manifest_types != name_types:
        fail("share-copy type_names keys do not match asset manifest type keys")
    if manifest_types != copy_types:
        fail("share-copy type_copy keys do not match asset manifest type keys")


def check_example() -> None:
    sample = load_json("examples/sample-scorecard.json")
    for key in ["subject", "scores", "composite", "worktype", "share_card"]:
        if key not in sample:
            fail(f"Sample scorecard missing key: {key}")
    score_keys = {
        "problem_framing",
        "reasoning_modeling",
        "evidence_verification",
        "ai_orchestration",
        "delivery_iteration",
    }
    scores = sample.get("scores", {})
    if set(scores.keys()) != score_keys:
        fail("Sample scorecard score keys do not match the five dimensions")
    for key in score_keys:
        value = scores.get(key, {}).get("score")
        if not isinstance(value, int) or not 0 <= value <= 100:
            fail(f"Sample score is not an integer from 0 to 100: {key}")


def main() -> int:
    check_required_structure()
    check_skill_frontmatter()
    check_assets()
    check_render_lock()
    check_copybook_alignment()
    check_example()
    if ERRORS:
        for error in ERRORS:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Repository validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
