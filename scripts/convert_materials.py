"""
convert_materials.py

把 materials/ 中的课程资料转换为 markdown/ 中的 Markdown 文件。

默认优先使用 MarkItDown。
可选启用 Docling 兜底，适合 PPT 导出的 PDF、结构图多、表格多、扫描页多的课件。

依赖：
    pip install -r requirements.txt

可选依赖：
    pip install -r requirements-optional.txt

用法：
    python scripts/convert_materials.py
    python scripts/convert_materials.py --docling-fallback
    python scripts/convert_materials.py --prefer-docling
"""

from __future__ import annotations

from pathlib import Path
import argparse
import sys
import traceback


ROOT = Path(__file__).resolve().parents[1]
MATERIALS_DIR = ROOT / "materials"
MARKDOWN_DIR = ROOT / "markdown"

SUPPORTED_SUFFIXES = {
    ".pdf",
    ".ppt",
    ".pptx",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".html",
    ".htm",
    ".txt",
    ".md",
    ".csv",
    ".json",
    ".xml",
    ".epub",
    ".zip",
}

# 如果转换出的文本少于这个字符数，就认为可能提取质量不足。
MIN_REASONABLE_CHARS = 800


def safe_stem(path: Path) -> str:
    allowed_extra = "._-（）()[]【】 第章节系统细胞组织器官"
    return "".join(ch if ch.isalnum() or ch in allowed_extra else "_" for ch in path.stem)


def convert_with_markitdown(file_path: Path) -> str:
    from markitdown import MarkItDown

    md_converter = MarkItDown()
    result = md_converter.convert(str(file_path))
    return result.text_content or ""


def convert_with_docling(file_path: Path) -> str:
    from docling.document_converter import DocumentConverter

    converter = DocumentConverter()
    result = converter.convert(str(file_path))
    return result.document.export_to_markdown()


def write_output(file_path: Path, text: str, engine: str) -> Path:
    out_path = MARKDOWN_DIR / f"{safe_stem(file_path)}.md"
    header = [
        "---",
        f"source_file: {file_path.name}",
        f"source_suffix: {file_path.suffix}",
        f"conversion_engine: {engine}",
        "---",
        "",
        f"# {file_path.stem}",
        "",
    ]
    out_path.write_text("\n".join(header) + text, encoding="utf-8")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--docling-fallback",
        action="store_true",
        help="当 MarkItDown 转换失败或文本过短时，尝试用 Docling 兜底。",
    )
    parser.add_argument(
        "--prefer-docling",
        action="store_true",
        help="优先使用 Docling 转换，失败后再尝试 MarkItDown。",
    )
    args = parser.parse_args()

    MATERIALS_DIR.mkdir(exist_ok=True)
    MARKDOWN_DIR.mkdir(exist_ok=True)

    files = [
        p for p in sorted(MATERIALS_DIR.iterdir())
        if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES
    ]

    if not files:
        print(f"未在 {MATERIALS_DIR} 中找到可转换资料。")
        print("请放入 PDF / PPTX / DOCX / TXT / MD 等文件。")
        return 0

    ok = 0
    failed = 0
    warnings = []

    for file_path in files:
        print(f"\n处理：{file_path.name}")
        text = ""
        engine = ""

        if args.prefer_docling:
            try:
                print("  使用 Docling...")
                text = convert_with_docling(file_path)
                engine = "docling"
            except Exception:
                print("  Docling 失败，尝试 MarkItDown...")
                try:
                    text = convert_with_markitdown(file_path)
                    engine = "markitdown"
                except Exception:
                    failed += 1
                    err_path = MARKDOWN_DIR / f"{safe_stem(file_path)}.ERROR.txt"
                    err_path.write_text(traceback.format_exc(), encoding="utf-8")
                    print(f"  转换失败，错误已写入 {err_path.name}", file=sys.stderr)
                    continue
        else:
            try:
                print("  使用 MarkItDown...")
                text = convert_with_markitdown(file_path)
                engine = "markitdown"
            except Exception:
                if args.docling_fallback:
                    print("  MarkItDown 失败，尝试 Docling...")
                    try:
                        text = convert_with_docling(file_path)
                        engine = "docling"
                    except Exception:
                        failed += 1
                        err_path = MARKDOWN_DIR / f"{safe_stem(file_path)}.ERROR.txt"
                        err_path.write_text(traceback.format_exc(), encoding="utf-8")
                        print(f"  转换失败，错误已写入 {err_path.name}", file=sys.stderr)
                        continue
                else:
                    failed += 1
                    err_path = MARKDOWN_DIR / f"{safe_stem(file_path)}.ERROR.txt"
                    err_path.write_text(traceback.format_exc(), encoding="utf-8")
                    print(f"  转换失败，错误已写入 {err_path.name}", file=sys.stderr)
                    continue

            if args.docling_fallback and len((text or "").strip()) < MIN_REASONABLE_CHARS:
                try:
                    print(f"  MarkItDown 输出较短（{len(text.strip())} 字符），尝试 Docling 兜底...")
                    docling_text = convert_with_docling(file_path)
                    if len(docling_text.strip()) > len(text.strip()):
                        text = docling_text
                        engine = "docling_fallback"
                except Exception:
                    warnings.append(f"{file_path.name}: MarkItDown 输出较短，但 Docling 兜底失败。")

        if not text or not text.strip():
            failed += 1
            warnings.append(f"{file_path.name}: 转换结果为空，可能是扫描件或图片型 PDF。")
            continue

        out_path = write_output(file_path, text, engine)
        print(f"  输出：{out_path.name}，字符数：{len(text.strip())}，引擎：{engine}")

        if len(text.strip()) < MIN_REASONABLE_CHARS:
            warnings.append(
                f"{file_path.name}: 转换文本较短，建议人工检查是否有大量图片/扫描页/结构图未提取。"
            )

        ok += 1

    if warnings:
        warning_path = MARKDOWN_DIR / "_conversion_warnings.md"
        warning_path.write_text(
            "# 转换质量提醒\n\n" + "\n".join(f"- {w}" for w in warnings),
            encoding="utf-8",
        )
        print(f"\n存在转换质量提醒，已写入：{warning_path}")

    print(f"\n完成：成功 {ok} 个，失败 {failed} 个。")
    print(f"Markdown 输出目录：{MARKDOWN_DIR}")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())