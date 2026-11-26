#!/usr/bin/env python3
"""Checks for the uniqaiapp organisation profile repository. Python 3 stdlib only.

    python3 scripts/check.py                   # brand-only strings, UTM links, banners, emoji
    python3 scripts/check.py --repos path.json # also compare the showcase with a repos.json list

Exit code 0 when every check passes, 1 otherwise. Warnings never change the exit code.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import xml.dom.minidom

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILE = os.path.join(ROOT, "profile", "README.md")
ASSETS = os.path.join(ROOT, "profile", "assets")
ORG = "uniqaiapp"
UTM = {"utm_source": "github", "utm_medium": "org_profile", "utm_campaign": ORG}
MAX_UNIQAI_LINKS = 3
BANNER_TARGET_KB, BANNER_CAP_KB = 15, 30
RASTER_CAP_KB = 200

# Built from code points so this file never contains the strings it forbids.
_FORBIDDEN_CODEPOINTS = [
    [97, 101, 111, 114, 105, 97],                    # a personal GitHub handle
    [114, 105, 99, 104, 112, 101, 97, 99, 104],      # a personal machine user name
]
FORBIDDEN = ["".join(map(chr, c)) for c in _FORBIDDEN_CODEPOINTS] + [
    "/Users/", "/Volumes/", "node_modules", "sk-ant-", "sk_live", "api_key=", "TODO: fill", "lorem ipsum",
]
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F900-\U0001F9FF]")

failures, warnings = [], []


def fail(msg):
    failures.append(msg)


def warn(msg):
    warnings.append(msg)


def tracked_files():
    try:
        out = subprocess.run(["git", "-C", ROOT, "ls-files"], capture_output=True, text=True, check=True).stdout
        files = [os.path.join(ROOT, f) for f in out.split("\n") if f]
        if files:
            return files
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    files = []
    for base, dirs, names in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d != ".git"]
        files += [os.path.join(base, n) for n in names]
    return files


def is_text(path):
    return not path.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico", ".woff", ".woff2", ".ttf"))


def check_forbidden():
    self_path = os.path.abspath(__file__)
    for path in tracked_files():
        if not is_text(path) or os.path.abspath(path) == self_path:
            continue  # this file holds the list itself; it is still scanned for e-mail addresses below
        rel = os.path.relpath(path, ROOT)
        with open(path, encoding="utf-8", errors="replace") as fh:
            for n, line in enumerate(fh, 1):
                low = line.lower()
                if rel == ".gitignore" and "node_modules" in low:
                    continue
                for s in FORBIDDEN:
                    if s.lower() in low:
                        fail(f"{rel}:{n}: forbidden string {s!r}")
                if "copyright (c)" in low and "uniqai" not in low:
                    fail(f"{rel}:{n}: copyright line without UniqAI")
    # the only e-mail address allowed anywhere is the support one
    for path in tracked_files():
        if not is_text(path):
            continue
        text = open(path, encoding="utf-8", errors="replace").read()
        for m in re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text):
            if m.lower() != "support@uniqai.app":
                fail(f"{os.path.relpath(path, ROOT)}: unexpected e-mail address {m}")


def check_profile():
    if not os.path.exists(PROFILE):
        fail("profile/README.md is missing")
        return set()
    text = open(PROFILE, encoding="utf-8").read()
    if EMOJI.search(text):
        fail("profile/README.md contains emoji")
    links = re.findall(r"https://uniqai\.app[^\s\"'<>)]*", text)
    if not links:
        fail("profile/README.md has no link to uniqai.app")
    if len(links) > MAX_UNIQAI_LINKS:
        fail(f"profile/README.md has {len(links)} uniqai.app links, limit is {MAX_UNIQAI_LINKS}")
    for link in links:
        query = link.split("?", 1)[1] if "?" in link else ""
        params = dict(p.split("=", 1) for p in query.split("&") if "=" in p)
        for k, v in UTM.items():
            if params.get(k) != v:
                fail(f"profile/README.md: {link} lacks {k}={v}")
    if text.count("Made by") != 1:
        fail("profile/README.md must contain exactly one 'Made by' footer")
    for word in ("Uniq AI", "UniqAi", "uniqai app"):
        if word in text:
            fail(f"profile/README.md: inconsistent brand spelling {word!r}")
    repos = set(re.findall(rf"https://github\.com/{ORG}/([A-Za-z0-9_.-]+)", text))
    repos.discard(".github")
    for r in sorted(repos):
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", r):
            fail(f"profile/README.md: repository name {r!r} is not kebab-case")
    # the banner <picture> must point at this repository on the main branch
    for name in ("banner-dark.jpg", "banner-light.jpg"):
        if f"https://raw.githubusercontent.com/{ORG}/.github/main/profile/assets/{name}" not in text:
            fail(f"profile/README.md does not reference profile/assets/{name} by its raw URL")
    return repos


def check_raster_banners():
    for name in ("banner-dark.jpg", "banner-light.jpg"):
        path = os.path.join(ASSETS, name)
        if not os.path.exists(path):
            fail(f"profile/assets/{name} is missing")
        elif os.path.getsize(path) / 1024 > RASTER_CAP_KB:
            fail(f"profile/assets/{name}: above the {RASTER_CAP_KB} KB cap")


def check_banners():
    for name in ("banner.svg", "banner-light.svg"):
        path = os.path.join(ASSETS, name)
        if not os.path.exists(path):
            fail(f"profile/assets/{name} is missing")
            continue
        try:
            xml.dom.minidom.parse(path)
        except Exception as e:  # noqa: BLE001
            fail(f"profile/assets/{name}: not well-formed XML ({e})")
            continue
        svg = open(path, encoding="utf-8").read()
        if "prefers-reduced-motion" not in svg:
            fail(f"profile/assets/{name}: no prefers-reduced-motion fallback")
        for bad in ("<script", "<image", "href=\"http"):
            if bad in svg:
                fail(f"profile/assets/{name}: contains {bad!r}, which GitHub's image proxy blocks")
        kb = os.path.getsize(path) / 1024
        if kb > BANNER_CAP_KB:
            fail(f"profile/assets/{name}: {kb:.1f} KB exceeds the {BANNER_CAP_KB} KB cap")
        elif kb > BANNER_TARGET_KB:
            warn(f"profile/assets/{name}: {kb:.1f} KB is above the {BANNER_TARGET_KB} KB target")


def check_repo_list(repos_json, listed):
    try:
        data = json.load(open(repos_json, encoding="utf-8"))
    except (OSError, ValueError) as e:
        fail(f"--repos: cannot read {repos_json}: {e}")
        return
    expected = {r["name"] for r in data.get("repos", [])}
    for missing in sorted(expected - listed):
        fail(f"profile/README.md does not list {missing}")
    for extra in sorted(listed - expected):
        fail(f"profile/README.md lists {extra}, which is not in {os.path.basename(repos_json)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--repos", help="repos.json to compare the showcase against (optional)")
    a = ap.parse_args()
    check_forbidden()
    listed = check_profile()
    check_banners()
    check_raster_banners()
    if a.repos:
        check_repo_list(a.repos, listed)
    for w in warnings:
        print(f"warn: {w}")
    for f in failures:
        print(f"FAIL: {f}")
    print(f"{len(failures)} failure(s), {len(warnings)} warning(s), {len(listed)} repositories listed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
