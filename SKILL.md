---
name: final-review-knowledge-framework
description: Build Chinese final-review knowledge frameworks from course materials such as PPT/PPTX, PDF, DOCX, Markdown notes, textbook excerpts, teacher review outlines, homework, and past exam materials. Use when the user wants Codex to read course files and organize a chapter-based knowledge map, concept relationships, mechanisms/processes, confusing points, and source-backed review notes for an exam, especially when the priority is framework整理 rather than question prediction or a cram schedule.
---

# Final Review Knowledge Framework

Turn course materials into a source-backed Chinese knowledge framework for final exam review. The main job is to extract the course structure, chapter logic, concept relationships, mechanisms/processes, confusing points, and source references. Do not lead with question prediction or cram planning unless the user explicitly asks for them.

## Workflow

1. Locate the user's course work area. Prefer the current folder when it contains `materials/`, `markdown/`, or course files.
2. Put raw course files in `materials/` if the user has not already organized them. Keep original filenames.
3. If `markdown/` is empty or stale, run:

```bash
python scripts/convert_materials.py
```

4. If conversion looks incomplete, such as very short Markdown, image-only slides, missing tables, or many diagrams, retry with:

```bash
python scripts/convert_materials.py --docling-fallback
```

Use `--prefer-docling` only when the materials are clearly diagram-heavy or slide-image PDFs.

5. Build the course context and source indexes:

```bash
python scripts/build_course_context.py
```

6. Read `outputs/_materials_index.md`, `outputs/_chapter_index.md`, `outputs/_source_quality_report.md`, and then the relevant parts of `outputs/_course_context.md`.
7. Generate the core framework outputs in `outputs/`.

## Core Outputs

Generate these files by default:

```text
outputs/课程知识总框架.md
outputs/章节知识树.md
outputs/概念关系与易混点.md
outputs/资料来源索引.md
```

Only generate `可能考题.md`, `三天冲刺计划.md`, or `错题与薄弱点追踪表.md` when the user explicitly asks for practice questions, a cram plan, or weak-point tracking.

## Output Requirements

For each chapter or major unit, organize:

- 本章核心问题
- 知识模块
- 关键概念
- 概念之间的关系
- 重点过程 / 机制 / 步骤
- 易混点
- 与前后章节的联系
- 来源文件

For each important knowledge point, include a source reference whenever possible, using the source filename or converted Markdown filename. If the material does not explain something clearly, write `资料中未充分说明，需要结合教材或课堂补充` instead of inventing details.

For diagrams, flowcharts, structure images, tables, slide annotations, red text, or highlighted content, mark the item as `可能需要人工查看原图补充` when the text extraction cannot prove the details.

## Style

Write in Chinese. Keep the result clear, structured, and suitable for review. Prefer headings, tables, and tree-shaped outlines. Do not write a generic summary, a long essay, or unsupported exam predictions.

