"""Check complete record XML locally; never reads or writes Feishu documents."""

import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


FORBIDDEN_HEADINGS = {
    "后续事项", "后续计划", "后续工作", "未来计划", "下一步",
    "待办", "待办事项", "待完成或待确认事项",
    "follow-up work", "follow-up items", "next steps", "open items",
}


def text_content(element):
    """Restore XML text and br line breaks without trimming source whitespace."""
    result = element.text or ""
    for child in element:
        result += "\n" if child.tag == "br" else text_content(child)
        result += child.tail or ""
    return result


def validate_record(xml, sources=None, original_title=None):
    """Return diagnostics for a complete candidate document or full read-back."""
    errors = []

    def error(code, message):
        errors.append({"code": code, "message": message})

    try:
        root = ET.fromstring("<record>" + xml + "</record>")
    except ET.ParseError as exc:
        error("xml", str(exc))
        return errors

    nodes = list(root)
    titles = root.findall("title")
    if len(titles) != 1 or not nodes or nodes[0].tag != "title":
        error("title", "A complete document must begin with one title.")
    elif titles:
        title = text_content(titles[0])
        match = re.fullmatch(r"(.{1,15})_(\d{8})", title)
        valid_date = False
        if match:
            try:
                datetime.strptime(match[2], "%Y%m%d")
                valid_date = True
            except ValueError:
                pass
        if original_title is not None and title != original_title:
            error("title_changed", "Keep the original document title and creation date.")
        elif original_title is None and not valid_date:
            error("name", "Use a summary of 1-15 characters and a valid YYYYMMDD date.")

    if (root.text or "").strip() or any((node.tail or "").strip() for node in nodes):
        error("loose_text", "Top-level text must be inside document blocks.")
    if len(nodes) < 2 or nodes[1].tag != "h1":
        error("preamble", "The first module must immediately follow the title.")

    previous_level = 0
    for element in root.iter():
        if re.fullmatch(r"h[1-9]", element.tag):
            level = int(element.tag[1:])
            if level > previous_level + 1:
                error("heading_level", "Heading levels must not skip levels.")
            previous_level = level
            heading = text_content(element).strip()
            heading = re.sub(r"^\d+(?:\.\d+)*[.、\s]*", "", heading).strip()
            if heading.casefold() in FORBIDDEN_HEADINGS:
                error("follow_up", "Remove the follow-up or to-do chapter.")
            if element.get("seq") != "auto" and not element.get("seq-marker"):
                error("numbering", "Headings need automatic numbering.")

    for table in root.iter("table"):
        rows = list(table.iter("tr"))
        # Row-spanning tables are checked by the CLI; do not misreport their width.
        try:
            cells = [c for row in rows for c in row if c.tag in {"th", "td"}]
            spans = [int(c.get(attr, "1")) for c in cells for attr in ("rowspan", "colspan")]
            if any(span < 1 for span in spans):
                raise ValueError("Invalid span")
            if any(int(c.get("rowspan", "1")) > 1 for c in cells):
                continue
            widths = [sum(int(c.get("colspan", "1")) for c in row
                          if c.tag in {"th", "td"}) for row in rows]
        except ValueError:
            error("table", "Table spans must be positive integers.")
            continue
        if not widths or not widths[0] or any(w != widths[0] for w in widths):
            error("table", "Table header and data rows must have equal width.")

    for label, expected in (sources or {}).items():
        fragments = []
        for block in root.iter("pre"):
            if block.get("caption", "").strip() == label + "/SKILL.md":
                code = block.find("code")
                if code is not None:
                    fragments.append(text_content(code))
        if not fragments:
            error("source_missing", "Missing source blocks for " + label)
        elif "".join(fragments) != expected:
            error("source_mismatch", "Source differs from its snapshot: " + label)
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("xml", type=Path, help="Complete candidate document XML")
    parser.add_argument("--original-title", help="Observed title to preserve when updating")
    parser.add_argument("--skill-source", action="append", default=[],
                        metavar="NAME=PATH", help="Source snapshot; repeat for multiple skills")
    args = parser.parse_args(argv)
    try:
        sources = {}
        for spec in args.skill_source:
            label, path = spec.split("=", 1)
            if not label or not path or label in sources:
                raise ValueError("Source labels must be nonempty and unique.")
            sources[label] = Path(path).read_bytes().decode("utf-8")
        errors = validate_record(args.xml.read_bytes().decode("utf-8"), sources,
                                 original_title=args.original_title)
    except (OSError, UnicodeError, ValueError) as exc:
        errors = [{"code": "input", "message": str(exc)}]
    print(json.dumps({"status": "failed" if errors else "passed", "errors": errors},
                     ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
