"""
build_course_context.py

把 markdown/ 中的课程资料整理为知识框架生成所需的索引和上下文。

用法：
    python scripts/build_course_context.py
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_DIR = ROOT / "markdown"
OUTPUTS_DIR = ROOT / "outputs"

COURSE_CONTEXT = OUTPUTS_DIR / "_course_context.md"
MATERIALS_INDEX = OUTPUTS_DIR / "_materials_index.md"
CHAPTER_INDEX = OUTPUTS_DIR / "_chapter_index.md"
QUALITY_REPORT = OUTPUTS_DIR / "_source_quality_report.md"

MIN_REASONABLE_CHARS = 800
MIN_REASONABLE_HEADINGS = 2

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


@dataclass
class Heading:
    level: int
    title: str
    line: int


@dataclass
class MaterialSummary:
    index: int
    path: Path
    text: str
    source_file: str
    source_suffix: str
    conversion_engine: str
    char_count: int
    heading_count: int
    table_count: int
    image_count: int
    headings: list[Heading]
    warnings: list[str]


def markdown_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def extract_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}

    lines = text.splitlines()
    if len(lines) < 3:
        return {}

    metadata: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()
    return metadata


def extract_headings(text: str) -> list[Heading]:
    headings: list[Heading] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            headings.append(
                Heading(
                    level=len(match.group(1)),
                    title=match.group(2).strip(),
                    line=line_number,
                )
            )
    return headings


def estimate_table_count(text: str) -> int:
    count = 0
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            count += 1
    return count


def estimate_image_count(text: str) -> int:
    markdown_images = len(re.findall(r"!\[[^\]]*\]\([^)]+\)", text))
    html_images = text.lower().count("<img")
    return markdown_images + html_images


def build_warnings(summary: MaterialSummary) -> list[str]:
    warnings: list[str] = []

    if summary.char_count < MIN_REASONABLE_CHARS:
        warnings.append("文本较短，可能有图片型页面、扫描页或转换不完整。")
    if summary.heading_count < MIN_REASONABLE_HEADINGS:
        warnings.append("标题较少，章节结构可能需要人工从原课件确认。")
    if summary.image_count > 0:
        warnings.append("包含图片引用，图中标签或结构可能需要人工查看原图补充。")
    if summary.table_count == 0 and any(
        keyword in summary.text for keyword in ("表", "对比", "分类", "流程", "结构")
    ):
        warnings.append("文本提到表格/流程/结构，但未检测到 Markdown 表格，需检查是否漏表。")

    return warnings


def load_materials() -> list[MaterialSummary]:
    summaries: list[MaterialSummary] = []
    md_files = sorted(p for p in MARKDOWN_DIR.glob("*.md") if p.is_file())

    for i, file_path in enumerate(md_files, start=1):
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        metadata = extract_frontmatter(text)
        headings = extract_headings(text)

        summary = MaterialSummary(
            index=i,
            path=file_path,
            text=text,
            source_file=metadata.get("source_file", file_path.name),
            source_suffix=metadata.get("source_suffix", file_path.suffix),
            conversion_engine=metadata.get("conversion_engine", "unknown"),
            char_count=len(text.strip()),
            heading_count=len(headings),
            table_count=estimate_table_count(text),
            image_count=estimate_image_count(text),
            headings=headings,
            warnings=[],
        )
        summary.warnings = build_warnings(summary)
        summaries.append(summary)

    return summaries


def render_materials_index(summaries: list[MaterialSummary]) -> str:
    parts = [
        "# 课程资料索引",
        "",
        "| 序号 | Markdown 文件 | 原始资料 | 转换引擎 | 字符数 | 标题数 | 表格行数 | 图片数 | 质量提醒 |",
        "|---:|---|---|---|---:|---:|---:|---:|---|",
    ]

    for item in summaries:
        warning_text = "<br>".join(markdown_escape(w) for w in item.warnings) if item.warnings else "无明显提醒"
        parts.append(
            "| {index} | `{md}` | {source} | {engine} | {chars} | {headings} | {tables} | {images} | {warnings} |".format(
                index=item.index,
                md=markdown_escape(item.path.name),
                source=markdown_escape(item.source_file),
                engine=markdown_escape(item.conversion_engine),
                chars=item.char_count,
                headings=item.heading_count,
                tables=item.table_count,
                images=item.image_count,
                warnings=warning_text,
            )
        )

    return "\n".join(parts)


def render_chapter_index(summaries: list[MaterialSummary]) -> str:
    parts = [
        "# 章节与标题索引",
        "",
        "用于判断课程结构、章节边界和知识框架生成顺序。",
        "",
    ]

    for item in summaries:
        parts.extend([
            f"## 资料 {item.index}：{item.source_file}",
            "",
            f"- Markdown 文件：`{item.path.name}`",
            f"- 标题数量：{item.heading_count}",
            "",
        ])

        if not item.headings:
            parts.extend(["无明显标题。", ""])
            continue

        for heading in item.headings:
            indent = "  " * max(heading.level - 1, 0)
            parts.append(f"{indent}- L{heading.line} H{heading.level} {heading.title}")
        parts.append("")

    return "\n".join(parts)


def render_quality_report(summaries: list[MaterialSummary]) -> str:
    parts = [
        "# 资料转换质量报告",
        "",
        "生成知识框架前先检查这些提醒。被标记的资料不一定不可用，但需要避免把缺失内容当作确定知识点。",
        "",
    ]

    problem_items = [item for item in summaries if item.warnings]
    if not problem_items:
        parts.append("未发现明显转换质量问题。")
        return "\n".join(parts)

    for item in problem_items:
        parts.extend([
            f"## 资料 {item.index}：{item.source_file}",
            "",
            f"- Markdown 文件：`{item.path.name}`",
            f"- 字符数：{item.char_count}",
            f"- 标题数：{item.heading_count}",
            f"- 表格行数：{item.table_count}",
            f"- 图片数：{item.image_count}",
        ])
        for warning in item.warnings:
            parts.append(f"- 提醒：{warning}")
        parts.append("")

    return "\n".join(parts)


def render_course_context(summaries: list[MaterialSummary], max_chars_per_file: int) -> str:
    parts = [
        "# 课程资料框架输入",
        "",
        "以下内容由 markdown/ 中的课程资料整理而来，供 Codex / Agent 生成期末知识框架使用。",
        "",
        "默认核心输出：",
        "",
        "- outputs/课程知识总框架.md",
        "- outputs/章节知识树.md",
        "- outputs/概念关系与易混点.md",
        "- outputs/资料来源索引.md",
        "",
        "生成时必须标注资料来源；资料不足时写“资料中未充分说明，需要结合教材或课堂补充”。",
        "",
        "## 资料概览",
        "",
        "| 序号 | 原始资料 | Markdown 文件 | 字符数 | 标题数 | 质量提醒 |",
        "|---:|---|---|---:|---:|---|",
    ]

    for item in summaries:
        warning_text = "<br>".join(markdown_escape(w) for w in item.warnings) if item.warnings else "无明显提醒"
        parts.append(
            f"| {item.index} | {markdown_escape(item.source_file)} | `{markdown_escape(item.path.name)}` | {item.char_count} | {item.heading_count} | {warning_text} |"
        )

    parts.extend([
        "",
        "## 资料正文",
        "",
    ])

    for item in summaries:
        text = item.text.strip()
        truncated = False
        if max_chars_per_file > 0 and len(text) > max_chars_per_file:
            text = text[:max_chars_per_file].rstrip()
            truncated = True

        parts.extend([
            "---",
            "",
            f"# 资料 {item.index}：{item.source_file}",
            "",
            f"- Markdown 文件：`{item.path.name}`",
            f"- 转换引擎：{item.conversion_engine}",
            f"- 字符数：{item.char_count}",
            f"- 标题数：{item.heading_count}",
            "",
        ])

        if item.warnings:
            parts.append("质量提醒：")
            for warning in item.warnings:
                parts.append(f"- {warning}")
            parts.append("")

        if truncated:
            parts.append(f"> 此处仅保留前 {max_chars_per_file} 字符；需要细节时回看 `markdown/{item.path.name}`。")
            parts.append("")

        parts.extend([text, ""])

    return "\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max-chars-per-file",
        type=int,
        default=50000,
        help="写入 _course_context.md 的每个 Markdown 文件最大字符数；设为 0 表示不截断。",
    )
    args = parser.parse_args()

    MARKDOWN_DIR.mkdir(exist_ok=True)
    OUTPUTS_DIR.mkdir(exist_ok=True)

    summaries = load_materials()
    if not summaries:
        print("markdown/ 中没有 .md 文件。请先运行 python scripts/convert_materials.py")
        return 0

    MATERIALS_INDEX.write_text(render_materials_index(summaries), encoding="utf-8")
    CHAPTER_INDEX.write_text(render_chapter_index(summaries), encoding="utf-8")
    QUALITY_REPORT.write_text(render_quality_report(summaries), encoding="utf-8")
    COURSE_CONTEXT.write_text(
        render_course_context(summaries, args.max_chars_per_file),
        encoding="utf-8",
    )

    print(f"已生成：{MATERIALS_INDEX}")
    print(f"已生成：{CHAPTER_INDEX}")
    print(f"已生成：{QUALITY_REPORT}")
    print(f"已生成：{COURSE_CONTEXT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
