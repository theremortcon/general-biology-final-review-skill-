# 通用期末复习 Skill 模板

这是一个面向 Codex / Agent 的通用期末复习 Skill 模板。

核心用途：

1. 把课程资料 PDF / PPTX / DOCX 放进 `materials/`
2. 用 MarkItDown 转成 Markdown
3. 让 Codex 根据 `AGENTS.md` 和 `prompts/` 生成期末复习资料
4. 输出知识框架、名词解释、易混点、可能考题、冲刺计划等文件

## 目录结构

```text
final-review-skill-template/
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
outputs/_course_context.md
outputs/_materials_index.md
```

### 4. 让 Codex 生成复习资料

对 Codex 说：

```text
请根据 AGENTS.md、prompts/universal_final_review_prompt.md，以及 outputs/_course_context.md，生成 outputs/ 中要求的所有期末复习文件。
```

## 推荐输出文件

Codex 应生成：

```text
outputs/总复习知识框架.md
outputs/名词解释背诵表.md
outputs/易混概念对比表.md
outputs/重点过程机制整理.md
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

这个模板不是“自动押题神器”。它的目标是把资料转成可复习的结构化材料：

- 知识树
- 名词解释
- 易混点
- 过程机制
- 可能题型
- 冲刺复习计划

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

如果发现漏图，可以把对应页面截图单独给 AI，让它补充到复习资料里。
