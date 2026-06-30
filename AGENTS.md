# 期末知识框架 Skill

这是一个面向 Codex / Agent 的中文期末复习知识框架工作流。重点是根据课件和资料整理课程知识地图，而不是优先押题或生成冲刺计划。

## 主目标

把 `materials/` 或 `markdown/` 中的课程资料整理成：

```text
outputs/课程知识总框架.md
outputs/章节知识树.md
outputs/概念关系与易混点.md
outputs/资料来源索引.md
```

只有用户明确要求时，才额外生成 `可能考题.md`、`三天冲刺计划.md`、`错题与薄弱点追踪表.md`。

## 工作流程

1. 查看 `materials/`、`markdown/`、`outputs/`。
2. 如果 `markdown/` 为空或明显过期，运行：

```bash
python scripts/convert_materials.py
```

3. 如果转换结果很短、缺标题、疑似图片型课件，运行：

```bash
python scripts/convert_materials.py --docling-fallback
```

4. 生成资料索引和课程上下文：

```bash
python scripts/build_course_context.py
```

5. 优先阅读：

```text
outputs/_materials_index.md
outputs/_chapter_index.md
outputs/_source_quality_report.md
outputs/_course_context.md
```

6. 按章节生成核心输出，不要只做普通摘要。

## 每章整理结构

每一章或每个课程单元都按这个结构整理：

```markdown
## 第 X 章：章节名

### 1. 本章核心问题
### 2. 知识模块
### 3. 关键概念
### 4. 概念之间的关系
### 5. 重点过程 / 机制 / 步骤
### 6. 易混点
### 7. 与前后章节的联系
### 8. 来源文件
```

## 整理原则

1. 先框架，后细节。
2. 先课程主线，再章节，再知识模块。
3. 概念类内容整理“定义、关键词、例子、关系、易混点”。
4. 过程类内容整理“条件、步骤、结果、意义、易错点”。
5. 图表、结构图、流程图、表格、红字、高亮、箭头标注必须单独提醒。
6. 每个重要知识点尽量标注来源文件。
7. 资料没有讲清楚时，写“资料中未充分说明，需要结合教材或课堂补充”。
8. 不要编造课件中没有的老师重点。
9. 可以说明“可能与考试有关”，但不要把推测写成确定押题。

## 输出风格

- 全部使用中文。
- 适合学生复习，不写成论文。
- 优先使用标题、表格、树状结构、箭头流程。
- 易混概念必须做对比。
- 资料来源要清楚，方便回看原课件。
