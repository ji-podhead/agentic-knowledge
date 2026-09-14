#!/usr/bin/env python3
"""OKF Portal Builder — generates manifest.json + _sidebar.md from OKF docs.

Parses the YAML frontmatter of every .md file (except README/_sidebar),
builds the GraphRAG entity graph (docs, topics, subtopics, tags), and emits:
  - manifest.json : { docs: [...], nodes: [...], links: [...] }
  - _sidebar.md  : Docsify navigation grouped by topic/subtopic

Runs in CI (pages.yml) AND can run locally:  python3 scripts/build_okf_portal.py
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCLUDE = {"README.md", "_sidebar.md", "manifest.json"}

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    m = FM_RE.match(text)
    if not m:
        return {}
    fm: dict = {}
    key = None
    for line in m.group(1).splitlines():
        if line.startswith("  - ") or line.startswith("- "):  # list item
            if key:
                fm.setdefault(key, [])
                if isinstance(fm[key], list):
                    fm[key].append(line.strip("- ").strip())
            continue
        if ":" in line:
            k, _, v = line.partition(":")
            key = k.strip()
            v = v.strip().strip('"')
            fm[key] = v
    return fm


def chunks(text: str) -> list:
    """Split a doc into chunks by headings for the multi-hop chunk panel."""
    parts = re.split(r"\n(?=#{1,3} )", text)
    out = []
    for p in parts:
        heading = p.splitlines()[0].lstrip("# ").strip() if p.strip() else ""
        body = p.strip()
        if heading and len(body) > 40:
            out.append({"heading": heading[:80], "chars": len(body)})
    return out


def main() -> int:
    docs, topics = [], {}
    for path in sorted(ROOT.rglob("*.md")):
        rel = path.relative_to(ROOT).as_posix()
        if rel in EXCLUDE or path.parent.name == ".git":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(text)
        if not fm.get("id"):  # not OKF — skip honestly
            continue
        topic = fm.get("topic", "unsorted")
        if topic.startswith("general/"):
            topic = topic[len("general/"):]
        if topic.startswith("infrastructure-automation/"):
            topic = "infrastructure-automation"
        subtopic = fm.get("subtopic", "")
        tags = fm.get("tags", [])
        if isinstance(tags, str):
            tags = [t for t in re.split(r"[,\s]+", tags) if t]
        docs.append({
            "id": fm.get("id", rel),
            "title": fm.get("title", path.stem),
            "path": rel,
            "topic": topic,
            "subtopic": subtopic,
            "tags": tags,
            "summary": fm.get("summary", "")[:180],
            "status": fm.get("status", ""),
            "chunks": chunks(text),
        })
        topics.setdefault(topic, {}).setdefault(subtopic or "_", []).append(fm.get("title", path.stem))

    # ── GraphRAG nodes & links ──
    nodes, links, seen = [], [], set()

    def node(nid: str, ntype: str, label: str, path: str = "", size: int = 0):
        if nid in seen:
            return
        seen.add(nid)
        nodes.append({"id": nid, "type": ntype, "label": label, "path": path, "size": size})

    for d in docs:
        did = f"doc:{d['id']}"
        node(did, "doc", d["title"], d["path"], len(d["chunks"]))
        if d["topic"]:
            node(f"topic:{d['topic']}", "topic", d["topic"], "", 0)
            links.append({"source": f"topic:{d['topic']}", "target": did})
        if d["subtopic"]:
            node(f"sub:{d['subtopic']}", "subtopic", d["subtopic"], "", 0)
            links.append({"source": f"sub:{d['subtopic']}", "target": did})
        for t in d["tags"]:
            if t:
                node(f"tag:{t}", "tag", t, "", 0)
                links.append({"source": did, "target": f"tag:{t}"})

    (ROOT / "manifest.json").write_text(json.dumps(
        {"docs": docs, "nodes": nodes, "links": links}, ensure_ascii=False, indent=1))

    # ── _sidebar.md ──
    lines = ["- [🏠 Home](/)", "- [🔍 Search](#/)"]
    for topic in sorted(topics):
        t_title = topic.replace("-", " ").title()
        lines.append(f"- **{t_title}**")
        for sub in sorted(topics[topic]):
            for title in topics[topic][sub]:
                doc = next(x for x in docs if x["title"] == title)
                sub_label = f" ({sub.replace('-', ' ')})" if sub != "_" else ""
                lines.append(f"  - [{title}{sub_label}](/{doc['path']})")
    (ROOT / "_sidebar.md").write_text("\n".join(lines) + "\n")

    print(f"OKF portal: {len(docs)} docs, {len(nodes)} nodes, {len(links)} links -> manifest.json + _sidebar.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
