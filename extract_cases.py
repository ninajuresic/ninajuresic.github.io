#!/usr/bin/env python3
"""
Targeted extraction: read specific function blocks to identify which
function is which case study, then extract per-function details.
"""
import re

FILE = "component.js"
with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()
lines = content.splitlines()

# Build function boundary table
func_starts = {}
for i, line in enumerate(lines, 1):
    m = re.match(r'^function\s+(\w+)\s*\(', line)
    if m:
        func_starts[m.group(1)] = i

sorted_funcs = sorted(func_starts.items(), key=lambda x: x[1])

def func_body(name):
    start = func_starts[name]
    # find next function start
    idx = [n for n, _ in sorted_funcs].index(name)
    end = sorted_funcs[idx+1][1] - 1 if idx+1 < len(sorted_funcs) else len(lines)
    return "\n".join(lines[start-1:end]), start, end

def extract_classnames(text):
    return re.findall(r'className:\s*["`]([^"`]+)["`]', text)

def extract_children_text(text):
    results = []
    for m in re.finditer(r'children:\s*"([^"]{2,})"', text):
        val = m.group(1)
        if not val.startswith("data:") and "/" not in val[:2]:
            results.append(val)
    return results

def extract_hrefs(text):
    return re.findall(r'href:\s*"([^"]+)"', text)

def extract_srcs(text):
    return [v for v in re.findall(r'src:\s*"([^"]+)"', text) if not v.startswith("data:")]

def extract_youtube(text):
    return re.findall(r'(https?://(?:www\.)?youtube(?:-nocookie)?\.com/embed/[^\s"\'<>]+)', text)

def sniff_section(name):
    body, start, end = func_body(name)
    texts = extract_children_text(body)
    yt = extract_youtube(body)
    hrefs = extract_hrefs(body)
    srcs = extract_srcs(body)
    
    # Use first few unique texts as a fingerprint
    sample = texts[:6]
    return {
        "name": name,
        "lines": f"{start}-{end}",
        "texts_sample": sample,
        "youtube": yt,
        "hrefs": hrefs,
        "srcs": [s for s in srcs if not s.startswith("data:")],
    }

# Print fingerprints for all larger functions (>50 lines)
print("=" * 70)
print("FUNCTION FINGERPRINTS (non-trivial functions)")
print("=" * 70)
for fname, fstart in sorted_funcs:
    idx = [n for n, _ in sorted_funcs].index(fname)
    fend = sorted_funcs[idx+1][1] - 1 if idx+1 < len(sorted_funcs) else len(lines)
    size = fend - fstart
    if size < 30:
        continue
    body = "\n".join(lines[fstart-1:fend])
    texts = extract_children_text(body)
    yt = extract_youtube(body)
    hrefs = extract_hrefs(body)
    print(f"\nfunction {fname}()  lines {fstart}-{fend}  ({size} lines)")
    if texts:
        print(f"  First texts: {texts[:4]}")
    if yt:
        print(f"  YouTube: {yt}")
    if hrefs:
        print(f"  hrefs: {hrefs[:3]}")

# ── Now do detailed per-section extraction for the big case study functions ──

print("\n\n" + "=" * 70)
print("DETAILED CASE STUDY SECTIONS")
print("=" * 70)

def report(fname, section_title):
    body, start, end = func_body(fname)
    classnames = list(dict.fromkeys(extract_classnames(body)))
    texts      = list(dict.fromkeys(extract_children_text(body)))
    hrefs      = list(dict.fromkeys(extract_hrefs(body)))
    srcs       = list(dict.fromkeys(extract_srcs(body)))
    yt         = list(dict.fromkeys(extract_youtube(body)))

    print(f"\n{'='*70}")
    print(f"  {section_title}  (function {fname}, lines {start}-{end})")
    print(f"{'='*70}")

    print("\n--- classNames ---")
    for c in classnames:
        print(f"  {c}")

    print("\n--- text content ---")
    for t in texts:
        print(f"  {repr(t)}")

    if hrefs:
        print("\n--- hrefs ---")
        for h in hrefs:
            print(f"  {h}")

    if srcs:
        print("\n--- srcs ---")
        for s in srcs:
            print(f"  {s}")

    if yt:
        print("\n--- YouTube embeds ---")
        for u in yt:
            print(f"  {u}")

# Report every substantial function individually
for fname, fstart in sorted_funcs:
    idx = [n for n, _ in sorted_funcs].index(fname)
    fend = sorted_funcs[idx+1][1] - 1 if idx+1 < len(sorted_funcs) else len(lines)
    size = fend - fstart
    if size >= 50:
        report(fname, f"FUNCTION {fname}")

print("\n✓ Done.")
