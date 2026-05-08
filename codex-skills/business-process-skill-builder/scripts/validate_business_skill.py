from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_FREEZING_TERMS = [
    "verify",
    "validate",
    "input",
    "output",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter.")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("SKILL.md frontmatter must end with --- on its own line.")
    raw = text[4:end]
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"Invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return [f"Missing {skill_md}"]

    text = read_text(skill_md)
    try:
        frontmatter = parse_frontmatter(text)
    except ValueError as exc:
        return [str(exc)]

    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")

    if not re.fullmatch(r"[a-z0-9-]{1,63}", name):
        errors.append("Frontmatter name must be lowercase hyphen-case and under 64 chars.")
    if skill_dir.name != name:
        errors.append(f"Folder name must match skill name: expected {name!r}.")
    if len(description.split()) < 12:
        errors.append("Description is too short to trigger reliably.")
    if "use when" not in description.lower() and "trigger" not in description.lower():
        errors.append("Description should include explicit use/trigger contexts.")

    lower = text.lower()
    for term in REQUIRED_FREEZING_TERMS:
        if term not in lower:
            errors.append(f"SKILL.md should mention {term!r} for business workflow freezing.")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python validate_business_skill.py <skill-folder>", file=sys.stderr)
        return 2

    skill_dir = Path(sys.argv[1]).resolve()
    errors = validate_skill(skill_dir)
    if errors:
        print("Business skill validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Business skill validation passed: {skill_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
