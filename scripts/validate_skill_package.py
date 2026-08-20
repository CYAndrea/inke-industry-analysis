#!/usr/bin/env python3
"""Validate the root skill package, internal references, and portability basics."""

import argparse
import re
import sys
from pathlib import Path


FRONTMATTER = re.compile(r"\A---\s*\n(?P<body>.*?)\n---\s*\n", re.DOTALL)
RESOURCE_REF = re.compile(r"`((?:references|assets|scripts|subskills)/[^`<>\s]+)`")
ABSOLUTE_PATH = re.compile(r"(?:[A-Za-z]:[\\/]Users[\\/]|/Users/|/home/)")


def frontmatter_value(body, key):
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+?)\s*$", body)
    return match.group(1).strip().strip('"\'') if match else ""


def validate_skill(path, expected_name=None):
    errors = []
    skill_file = path / "SKILL.md"
    if not skill_file.exists():
        return [f"missing {skill_file}"]
    text = skill_file.read_text(encoding="utf-8-sig")
    match = FRONTMATTER.match(text)
    if not match:
        return [f"{skill_file}: invalid frontmatter"]
    name = frontmatter_value(match.group("body"), "name")
    description = frontmatter_value(match.group("body"), "description")
    if not re.fullmatch(r"[a-z0-9-]{1,63}", name):
        errors.append(f"{skill_file}: invalid name {name!r}")
    if expected_name and name != expected_name:
        errors.append(f"{skill_file}: name must match folder {expected_name!r}")
    if len(description) < 20:
        errors.append(f"{skill_file}: description is too short")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    errors = validate_skill(root)
    required = [
        "agents/openai.yaml",
        "references/execution-contracts.md",
        "references/research-artifact-schema.json",
        "references/output-profile-contracts.json",
        "assets/excel-style.json",
        "assets/completion-audit.json",
        "scripts/build_research_excel.mjs",
        "scripts/validate_artifact_bundle.py",
    ]
    for relative in required:
        if not (root / relative).exists():
            errors.append(f"missing required resource: {relative}")
    subskills = root / "subskills"
    if not subskills.exists():
        errors.append("missing subskills directory")
    else:
        for child in sorted(item for item in subskills.iterdir() if item.is_dir()):
            errors.extend(validate_skill(child, child.name))
    text_files = [
        path
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.parts and "__pycache__" not in path.parts
        and path.suffix.lower() in {".md", ".json", ".py", ".mjs", ".yaml", ".yml"}
    ]
    for path in text_files:
        text = path.read_text(encoding="utf-8-sig")
        if path.resolve() != Path(__file__).resolve() and ABSOLUTE_PATH.search(text):
            errors.append(f"{path.relative_to(root)} contains a personal absolute path")
        if path.name == "SKILL.md":
            for relative in RESOURCE_REF.findall(text):
                if not (root / relative).exists():
                    errors.append(f"{path.relative_to(root)} references missing {relative}")
    if errors:
        print("FAIL")
        for error in errors:
            print("- " + error)
        sys.exit(1)
    print("PASS: skill package structure, references, and portability validated")


if __name__ == "__main__":
    main()
