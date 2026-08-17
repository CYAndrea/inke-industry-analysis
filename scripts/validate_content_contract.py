#!/usr/bin/env python3
"""Validate narrative blocks before delivery."""

import argparse
import json
import re
import sys
from pathlib import Path


def sentence_count(text):
    return len([x for x in re.split(r"[。！？!?；;]+", text) if x.strip()])


def validate(block):
    errors = []
    text = block.get("text", "")
    if not isinstance(text, str) or len(text.strip()) < 35:
        errors.append("text is too short")
        return errors
    if block.get("kind") == "engineering_bottleneck":
        if sentence_count(text) < 2:
            errors.append("engineering_bottleneck needs at least two sentences")
        if text.count("、") + text.count(",") >= max(3, sentence_count(text) * 2):
            errors.append("engineering_bottleneck appears to be a keyword list")
        required = block.get("required_elements", ["问题", "原因", "影响"])
        missing = [item for item in required if item not in text]
        if missing:
            errors.append("missing elements: " + ", ".join(missing))
    if block.get("kind") == "investment_point":
        for item in block.get("required_elements", ["依据", "失效", "待验证"]):
            if item not in text:
                errors.append("investment point missing: " + item)
    return errors


parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
args = parser.parse_args()
data = json.loads(Path(args.input).read_text(encoding="utf-8-sig"))
blocks = data.get("blocks", data if isinstance(data, list) else [])
errors = []
for index, block in enumerate(blocks, start=1):
    for error in validate(block):
        errors.append(f"block[{index}]: {error}")
if errors:
    print("FAIL")
    print("\n".join("- " + error for error in errors))
    sys.exit(1)
print(f"PASS: {len(blocks)} narrative blocks validated")
