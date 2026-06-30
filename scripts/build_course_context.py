"""
build_course_context.py

把 markdown/ 中的文件合并为一个课程上下文文件，便于 Codex / Agent 阅读。

用法：
    python scripts/build_course_context.py
"""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_DIR = ROOT / "markdown"
OUTPUTS_DIR = ROOT / "outputs"

COURSE_CONTEXT = OUTPUTS_DIR / "_course_context.md"
MATERIALS_INDEX = OUTPUTS_DIR / "_materials_index.md"


def extract_headings(text: str) -> list[str]:
    headings = []
    for line in text.splitlines():
        if line.startswith("#"):
            headings.append(line.strip())
    return headings


def main() -> int:
    MARKDOWN_DIR.mkdir(exist_ok=True)
    OUTPUTS_DIR.mkdir(exist_ok=True)

    md_files = sorted(MARKDOWN_DIR.glob("*.md"))

    if not md_files:
        print("markdown/ 中没有 .md 文件。请先运行 python scripts/convert_materials.py")
        return 0

    context_parts = [
        "# 课程资料总上下文",
        "",
        "以下内容由 markdown/ 中的课程资料合并而来，供 Codex / Agent 生成期末复习资料使用。",
        "",
    ]

    index_parts = [
        "# 课程资料索引",
        "",
        "| 序号 | 文件 | 标题/小标题数量 | 主要标题 |",
        "|---|---|---:|---|",
    ]

    for i, file_path in enumerate(md_files, start=1):
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        headings = extract_headings(text)
        preview_headings = "<br>".join(h.replace("|", "\\|") for h in headings[:8]) if headings else "无明显标题"

        index_parts.append(
            f"| {i} | `{file_path.name}` | {len(headings)} | {preview_headings} |"
        )

        context_parts.extend([
            "",
            "---",
            "",
            f"# 资料 {i}：{file_path.name}",
            "",
            text,
            "",
        ])

    COURSE_CONTEXT.write_text("\n".join(context_parts), encoding="utf-8")
    MATERIALS_INDEX.write_text("\n".join(index_parts), encoding="utf-8")

    print(f"已生成：{COURSE_CONTEXT}")
    print(f"已生成：{MATERIALS_INDEX}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())