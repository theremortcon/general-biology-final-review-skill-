# 期末知识框架 Skill

这是一个面向 Codex / Agent 的中文期末知识框架 Skill。它的重点是根据课件和资料整理课程知识地图，而不是优先生成押题、刷题或冲刺计划。

核心用途：

1. 把课程资料 PDF / PPTX / DOCX 放进 `materials/`
2. 用 MarkItDown 转成 Markdown
3. 用脚本生成资料索引、章节索引和转换质量报告
4. 让 Codex 生成章节知识树、概念关系、重点过程机制、易混点和资料来源索引

## 目录结构

```text
final-review-skill-template/
├── SKILL.md
├── AGENTS.md
├── README.md
├── requirements.txt
├── materials/                 # 放课件、教材、复习提纲
├── markdown/                  # 转换后的 Markdown
├── outputs/                   # 最终复习资料
├── prompts/
│   └── universal_final_review_prompt.md
├── scripts/
│   ├── convert_materials.py
│   └── build_course_context.py
└── templates/
    ├── weak_points_tracker.md
    └── exam_review_outputs.md
```

## 安装

建议使用 Python 3.10 或以上版本。

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

## 使用方法

### 1. 放入课程资料

把 PDF、PPTX、DOCX、TXT、MD 等文件放入：

```text
materials/
```

### 2. 转换为 Markdown

```bash
python scripts/convert_materials.py
```

转换结果会保存到：

```text
markdown/
```

### 3. 生成课程上下文索引

```bash
python scripts/build_course_context.py
```

它会生成：

```text
outputs/_materials_index.md
outputs/_chapter_index.md
outputs/_source_quality_report.md
outputs/_course_context.md
```

### 4. 让 Codex 生成知识框架

对 Codex 说：

```text
请根据 SKILL.md、outputs/_materials_index.md、outputs/_chapter_index.md、outputs/_source_quality_report.md 和 outputs/_course_context.md，生成课程知识框架。
```

## 默认输出文件

Codex 默认生成：

```text
outputs/课程知识总框架.md
outputs/章节知识树.md
outputs/概念关系与易混点.md
outputs/资料来源索引.md
```

只有明确要求练题、冲刺计划、错题追踪时，才额外生成：

```text
outputs/可能考题.md
outputs/三天冲刺计划.md
outputs/错题与薄弱点追踪表.md
```

## 适用课程

适合概念多、分类多、过程多、图表多的课程，例如：

- 普通生物学
- 生物化学
- 细胞生物学
- 微生物学
- 有机化学
- 医学基础课
- 思政 / 历史 / 管理学等记忆型课程
- 其他期末闭卷复习课程

## 注意

这个 Skill 不是“自动押题神器”。它的目标是把资料转成可复习的知识框架：

- 知识树
- 概念关系
- 易混概念对比
- 重点过程机制
- 资料来源索引
- 转换质量提醒

如果课件中有大量图片、扫描页、手写字、结构图，MarkItDown 可能无法完整提取，需要人工检查或用更强的 OCR / Docling 方案补充。

## MarkItDown、Docling 与 OCR 的使用建议

本模板默认优先使用 MarkItDown，因为它轻量、安装快，适合大多数 PDF / PPTX / DOCX 课件。

但如果课程资料具有以下特点，建议启用 Docling 兜底：

- PDF 是 PPT 导出的图片型页面；
- 页面里有大量结构图、流程图、组织切片图；
- 图中有重要标签、箭头、表格；
- MarkItDown 转换后 Markdown 内容明显太少；
- 复习时需要识图题、表格题、结构题。

### 默认方案

```bash
python scripts/convert_materials.py
```

### 启用 Docling 兜底

先安装可选依赖：

```bash
pip install -r requirements-optional.txt
```

然后运行：

```bash
python scripts/convert_materials.py --docling-fallback
```

### 强制优先使用 Docling

```bash
python scripts/convert_materials.py --prefer-docling
```

### 什么时候需要人工补图？

即使用 Docling，也不一定能完全理解所有组织切片图、手写字、复杂结构图。生成复习资料后，请重点检查：

- 是否漏掉图中的结构名称；
- 是否漏掉“可能出识图题”的图片；
- 是否把表格转换错行；
- 是否把箭头流程识别错误。

如果发现漏图，可以把对应页面截图单独给 AI，让它补充到知识框架里。

## Windows 中文显示

所有 Markdown 和脚本输出都按 UTF-8 保存。若 PowerShell 中中文显示异常，可先运行：

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = "1"
```
