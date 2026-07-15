#!/usr/bin/env python3
"""
Extract classNames, text content, hrefs, srcs, and YouTube URLs from component.js,
grouped by page/section.
"""

import re
import sys

FILE = "component.js"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

lines = content.splitlines()

# ── helpers ──────────────────────────────────────────────────────────────────

def extract_strings(text):
    """Return all double-quoted and single-quoted string literals."""
    return re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', text) + \
           re.findall(r"'([^'\\]*(?:\\.[^'\\]*)*)'", text)

def extract_classnames(text):
    """Return values of className: "..." patterns (including template literals)."""
    results = []
    for m in re.finditer(r'className:\s*["`]([^"`]+)["`]', text):
        results.append(m.group(1))
    return results

def extract_children_text(text):
    """Return plain-text children strings (children: "...") that look like real copy."""
    results = []
    for m in re.finditer(r'children:\s*"([^"]{2,})"', text):
        val = m.group(1)
        if not val.startswith("data:") and "/" not in val[:3]:
            results.append(val)
    return results

def extract_hrefs(text):
    return re.findall(r'href:\s*"([^"]+)"', text)

def extract_srcs(text):
    results = []
    for m in re.finditer(r'src:\s*"([^"]+)"', text):
        v = m.group(1)
        if not v.startswith("data:"):
            results.append(v)
    return results

def extract_youtube(text):
    return re.findall(r'(https?://(?:www\.)?youtube(?:-nocookie)?\.com/embed/[^\s"\'<>]+)', text)

# ── section boundaries ────────────────────────────────────────────────────────
# We'll scan for function definitions and key identifiers to carve out sections.

# Find all top-level function declarations and their line numbers
func_starts = {}
for i, line in enumerate(lines, 1):
    m = re.match(r'^function\s+(\w+)\s*\(', line)
    if m:
        func_starts[m.group(1)] = i

print("=" * 70)
print("ALL FUNCTION DEFINITIONS AND LINE NUMBERS")
print("=" * 70)
for name, lineno in sorted(func_starts.items(), key=lambda x: x[1]):
    print(f"  line {lineno:4d}  function {name}()")

# ── locate key sections by content ───────────────────────────────────────────

def find_line(pattern):
    rx = re.compile(pattern, re.IGNORECASE)
    for i, line in enumerate(lines, 1):
        if rx.search(line):
            return i
    return None

section_markers = {
    "HOME / function q": find_line(r'onProjectClick'),
    "HEALTHTALK case study": find_line(r'"healthtalk"|HealthTalk'),
    "PITCH V2 case study": find_line(r'"pitch-v2"|Pitch V2|PitchV2'),
    "LOCALIZATION case study": find_line(r'"localization"|Localization System'),
    "CV MODAL": find_line(r'CV-Nina Juresic|cv-printable'),
}

print("\n" + "=" * 70)
print("KEY SECTION FIRST-OCCURRENCE LINE NUMBERS")
print("=" * 70)
for section, lineno in section_markers.items():
    print(f"  {section}: line {lineno}")

# ── per-section extraction ────────────────────────────────────────────────────

def section_slice(start_line, end_line):
    return "\n".join(lines[start_line - 1 : end_line])

def report_section(title, text_block):
    print("\n" + "=" * 70)
    print(f"  SECTION: {title}")
    print("=" * 70)

    classnames = extract_classnames(text_block)
    children   = extract_children_text(text_block)
    hrefs      = extract_hrefs(text_block)
    srcs       = extract_srcs(text_block)
    yt         = extract_youtube(text_block)

    if classnames:
        print("\n--- classNames ---")
        for c in dict.fromkeys(classnames):   # deduplicated, order-preserved
            print(f"  {c}")

    if children:
        print("\n--- text content (children) ---")
        for c in dict.fromkeys(children):
            print(f"  {repr(c)}")

    if hrefs:
        print("\n--- href values ---")
        for h in dict.fromkeys(hrefs):
            print(f"  {h}")

    if srcs:
        print("\n--- src values ---")
        for s in dict.fromkeys(srcs):
            print(f"  {s}")

    if yt:
        print("\n--- YouTube embed URLs ---")
        for u in dict.fromkeys(yt):
            print(f"  {u}")

# ── find the function that contains each marker line ─────────────────────────

sorted_funcs = sorted(func_starts.items(), key=lambda x: x[1])

def func_range_for_line(target_line):
    """Return (func_name, start, end) for the function that contains target_line."""
    prev_name, prev_start = None, None
    for name, start in sorted_funcs:
        if prev_name and prev_start <= target_line < start:
            return prev_name, prev_start, start - 1
        prev_name, prev_start = name, start
    # last function
    if prev_name:
        return prev_name, prev_start, len(lines)
    return None, 1, len(lines)

# For broader sections (case studies) we want everything from the first
# function that mentions the keyword up to the next major section.
def keyword_section_range(keyword_pattern, extra_lines=250):
    """
    Find the function containing the keyword, then grab a window around it.
    Returns (start_line, end_line).
    """
    first = find_line(keyword_pattern)
    if first is None:
        return None, None
    fn_name, fn_start, fn_end = func_range_for_line(first)
    # expand to capture the whole section – grab extra_lines beyond fn_end
    return fn_start, min(fn_end + extra_lines, len(lines))

# ── HOME PAGE ─────────────────────────────────────────────────────────────────
home_line = find_line(r'onProjectClick')
fn_name, fn_start, fn_end = func_range_for_line(home_line) if home_line else ("?", 1, 200)

# Broaden: grab from fn_start to a generous window that includes nav + hero + cards
home_end = min(fn_end + 100, len(lines))
report_section(f"HOME PAGE  (function {fn_name}, lines {fn_start}-{home_end})",
               section_slice(fn_start, home_end))

# ── HEALTHTALK ────────────────────────────────────────────────────────────────
ht_start, ht_end = keyword_section_range(r'"healthtalk"|HealthTalk', extra_lines=400)
if ht_start:
    report_section(f"HEALTHTALK CASE STUDY  (lines {ht_start}-{ht_end})",
                   section_slice(ht_start, ht_end))

# ── PITCH V2 ──────────────────────────────────────────────────────────────────
pv_start, pv_end = keyword_section_range(r'"pitch-v2"|Pitch\s*V2|PitchV2', extra_lines=400)
if pv_start:
    report_section(f"PITCH V2 CASE STUDY  (lines {pv_start}-{pv_end})",
                   section_slice(pv_start, pv_end))

# ── LOCALIZATION ──────────────────────────────────────────────────────────────
loc_start, loc_end = keyword_section_range(r'"localization"|Localization\s*System', extra_lines=400)
if loc_start:
    report_section(f"LOCALIZATION CASE STUDY  (lines {loc_start}-{loc_end})",
                   section_slice(loc_start, loc_end))

# ── CV MODAL ──────────────────────────────────────────────────────────────────
cv_start, cv_end = keyword_section_range(r'CV-Nina Juresic|cv-printable', extra_lines=300)
if cv_start:
    report_section(f"CV MODAL  (lines {cv_start}-{cv_end})",
                   section_slice(cv_start, cv_end))

# ── GLOBAL YouTube scan ───────────────────────────────────────────────────────
yt_all = extract_youtube(content)
print("\n" + "=" * 70)
print("  ALL YOUTUBE EMBED URLs IN FILE")
print("=" * 70)
if yt_all:
    for u in dict.fromkeys(yt_all):
        print(f"  {u}")
else:
    print("  (none found)")

# ── ALL hrefs ─────────────────────────────────────────────────────────────────
all_hrefs = extract_hrefs(content)
print("\n" + "=" * 70)
print("  ALL href VALUES IN FILE")
print("=" * 70)
for h in dict.fromkeys(all_hrefs):
    print(f"  {h}")

print("\n✓ Done.")
