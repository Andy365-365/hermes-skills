---
name: terminal-ascii-box-cjk-alignment
description: >
  终端 ASCII 图形绘制工具：CJK 中文内容右对齐。
  提供方框、表格、流程图、并排布局等组件，按视觉列数（CJK=2列, ASCII=1列）
  计算填充空格，确保所有边框严格对齐。适用于终端输出、CLI 工具、
  Markdown 代码块中的 ASCII art。
---

# 终端 ASCII 图形：CJK 中文对齐

## 问题

终端中 CJK 字符占 **2 列**视觉宽度，ASCII 字符占 **1 列**。按字符数填充空格会导致右侧边框错位。

## 核心函数

### visual_width / pad_to

```python
def _is_cjk(ch):
    cp = ord(ch)
    return (0x4e00 <= cp <= 0x9fff or 0x3000 <= cp <= 0x303f or
            0xff00 <= cp <= 0xffef or 0x2000 <= cp <= 0x206f or
            0x3400 <= cp <= 0x4dbf or 0xf900 <= cp <= 0xfaff)

def visual_width(s):
    """终端视觉宽度：CJK=2列, ASCII=1列"""
    return sum(2 if _is_cjk(ch) else 1 for ch in s)

def pad_to(s, target_w):
    """填充到目标视觉宽度"""
    return s + ' ' * max(0, target_w - visual_width(s))
```

### make_box — 方框

```python
def make_box(lines, content_w=None):
    """
    CJK 安全的 ASCII 方框。

    lines: 内容行列表（纯文本，不含边框字符）
    content_w: 内容区视觉宽度（即 ─ 的数量）。None 则自动适配最长行 + 2。

    结构：│<空格><内容><填充空格><空格>│
    返回：行列表
    """
    if content_w is None:
        content_w = max(visual_width(l) for l in lines) + 2

    slot_w = content_w - 2
    padded = [pad_to(line, slot_w) for line in lines]

    top = '┌' + '─' * content_w + '┐'
    bottom = '└' + '─' * content_w + '┘'
    middle = ['│ ' + l + ' │' for l in padded]
    return [top] + middle + [bottom]
```

**示例：**

```python
box = make_box([
    "GitHub Actions 工作流",
    "",
    "触发：push 到 main 分支",
    "触发：PR 合并请求",
], 28)
print('\n'.join(box))
```

输出：
```
┌────────────────────────────┐
│ GitHub Actions 工作流      │
│                            │
│ 触发：push 到 main 分支    │
│ 触发：PR 合并请求          │
└────────────────────────────┘
```

### make_table — 表格

```python
def make_table(headers, rows, col_widths=None):
    """
    CJK 安全的 ASCII 表格。

    headers: 表头列表
    rows: 数据行列表（每行是列表）
    col_widths: 每列视觉宽度。None 则自动适配。

    返回：行列表
    """
    ncols = len(headers)
    if col_widths is None:
        col_widths = []
        for c in range(ncols):
            cells = [headers[c]] + [row[c] for row in rows if c < len(row)]
            col_widths.append(max(visual_width(cell) for cell in cells) + 2)

    # 表头
    cells = [pad_to(headers[c], col_widths[c] - 2) for c in range(ncols)]
    header_inner = '│ ' + ' │ '.join(cells) + ' │'

    # 分隔线
    sep_parts = ['─' * w for w in col_widths]
    sep = '├' + '┼'.join(sep_parts) + '┤'

    # 顶/底边框
    top = '┌' + '┬'.join('─' * w for w in col_widths) + '┐'
    bot = '└' + '┴'.join('─' * w for w in col_widths) + '┘'

    # 数据行
    data = []
    for row in rows:
        cells = [pad_to(row[c] if c < len(row) else '', col_widths[c] - 2)
                 for c in range(ncols)]
        data.append('│ ' + ' │ '.join(cells) + ' │')

    return [top, header_inner, sep] + data + [bot]
```

**示例：**

```python
table = make_table(
    ["平台", "配置方式", "免费额度", "适用场景"],
    [
        ["GitHub Actions", "YAML", "开源无限", "最主流"],
        ["GitLab CI", ".gitlab-ci.yml", "开源自建", "企业内网"],
        ["Jenkins", "Groovy DSL", "完全免费", "老牌插件多"],
    ]
)
print('\n'.join(table))
```

输出：
```
┌────────────────┬────────────────┬──────────┬────────────┐
│ 平台           │ 配置方式       │ 免费额度 │ 适用场景   │
├────────────────┼────────────────┼──────────┼────────────┤
│ GitHub Actions │ YAML           │ 开源无限 │ 最主流     │
│ GitLab CI      │ .gitlab-ci.yml │ 开源自建 │ 企业内网   │
│ Jenkins        │ Groovy DSL     │ 完全免费 │ 老牌插件多 │
└────────────────┴────────────────┴──────────┴────────────┘
```

### connect_boxes_vertical — 垂直流程图

```python
def connect_boxes_vertical(boxes, labels=None):
    """
    垂直连接多个方框，带茎线和箭头。

    boxes: 方框列表（每个是 make_box 的返回值）
    labels: 连接线标签列表（长度 = len(boxes) - 1）。
            空字符串表示无标签。

    自动将所有方框对齐到最大宽度，连接线居中。
    返回：完整流程图的行列表
    """
    if not boxes:
        return []
    if labels is None:
        labels = [''] * (len(boxes) - 1)

    # 统一宽度
    max_w = max(box_width(b) for b in boxes)
    # box_width 含角字符(┌...┐)，dash 数量 = max_w - 2
    dash_w = max_w - 2
    normalized = []
    for b in boxes:
        bw = box_width(b)
        if bw < max_w:
            new_lines = []
            for j, line in enumerate(b):
                if j == 0:
                    new_lines.append('┌' + '─' * dash_w + '┐')
                elif j == len(b) - 1:
                    new_lines.append('└' + '─' * dash_w + '┘')
                else:
                    inner = line[2:-2] if line.startswith('│ ') and line.endswith(' │') else line[1:]
                    new_lines.append('│ ' + pad_to(inner, dash_w - 2) + ' │')
            normalized.append(new_lines)
        else:
            normalized.append(list(b))

    result = []
    for i, box in enumerate(normalized):
        result.extend(box)
        if i < len(boxes) - 1:
            stem_col = max_w // 2
            last_line = list(box[-1])
            char_idx = _visual_to_char_idx(''.join(last_line), stem_col)
            if char_idx < len(last_line) and last_line[char_idx] == '─':
                last_line[char_idx] = '┬'
            result[-1] = ''.join(last_line)

            label = labels[i] if i < len(labels) else ''
            conn = (' ' * stem_col + '│ ' + label) if label else \
                    ' ' * stem_col + '│'
            result.append(pad_to(conn, max_w))
            result.append(pad_to(' ' * stem_col + '▼', max_w))

    return result
```

**示例：**

```python
steps = [
    make_box(["触发 CI Pipeline"]),
    make_box(["1. Lint 与静态检查"]),
    make_box(["2. 单元测试"]),
    make_box(["3. 构建打包"]),
    make_box(["4. 部署到生产环境"]),
]
chart = connect_boxes_vertical(steps, ['通过', '通过', '通过', ''])
print('\n'.join(chart))
```

输出：
```
┌────────────────────┐
│ 触发 CI Pipeline   │
└──────────┬─────────┘
           │ 通过
           ▼
┌────────────────────┐
│ 1. Lint 与静态检查 │
└──────────┬─────────┘
           │ 通过
           ▼
┌────────────────────┐
│ 2. 单元测试        │
└──────────┬─────────┘
           │ 通过
           ▼
┌────────────────────┐
│ 3. 构建打包        │
└──────────┬─────────┘
           │
           ▼
┌────────────────────┐
│ 4. 部署到生产环境  │
└────────────────────┘
```

### make_flowchart — 快捷流程图

```python
def make_flowchart(steps, connector_label='通过'):
    """
    从步骤名称快速生成垂直流程图。

    steps: 列表，元素可以是：
           - 字符串（单行方框）
           - 字符串列表（多行方框）
    connector_label: 每个连接线的默认标签

    返回：流程图的行列表
    """
    boxes = []
    for step in steps:
        if isinstance(step, str):
            boxes.append(make_box([step]))
        elif isinstance(step, (list, tuple)):
            boxes.append(make_box([str(item) for item in step]))
        else:
            boxes.append(make_box([str(step)]))

    labels = [connector_label] * (len(boxes) - 1)
    return connect_boxes_vertical(boxes, labels)
```

**示例：**

```python
chart = make_flowchart([
    ["开发者提交代码", "commit / PR"],
    "触发 CI Pipeline",
    "1. Lint 与静态检查",
    "2. 单元测试",
    "3. 集成测试",
    "4. 安全扫描",
    ["5. 部署到环境", "staging → production"],
    "6. 健康检查与监控",
], '通过')
print('\n'.join(chart))
```

### make_side_by_side — 并排布局

```python
def make_side_by_side(boxes, gap=2):
    """
    将多个方框水平并排，垂直居中对齐。

    boxes: 方框列表
    gap: 方框之间的空格数

    返回：组合后的行列表
    """
    heights = [len(b) for b in boxes]
    max_h = max(heights)

    padded_boxes = []
    for b in boxes:
        h = len(b)
        top_pad = (max_h - h) // 2
        bot_pad = max_h - h - top_pad
        spaces = ' ' * box_width(b)
        padded_boxes.append([spaces] * top_pad + list(b) + [spaces] * bot_pad)

    total_w = sum(box_width(b) for b in boxes) + gap * (len(boxes) - 1)
    lines = []
    for i in range(max_h):
        row = ''
        for pb in padded_boxes:
            row += pb[i] + ' ' * gap
        row = row.rstrip()
        row = pad_to(row, total_w)
        lines.append(row)

    return lines
```

**示例：**

```python
b1 = make_box(["开发环境", "dev.example.com"], 20)
b2 = make_box(["预发布环境", "stg.example.com"], 20)
b3 = make_box(["生产环境", "prod.example.com"], 20)
layout = make_side_by_side([b1, b2, b3])
print('\n'.join(layout))
```

输出：
```
┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐
│ 开发环境           │  │ 预发布环境         │  │ 生产环境           │
│ dev.example.com    │  │ stg.example.com    │  │ prod.example.com   │
└────────────────────┘  └────────────────────┘  └────────────────────┘
```

### connect_boxes_horizontal — 水平连接

```python
def connect_boxes_horizontal(boxes, labels=None):
    """
    水平连接多个方框，带箭头和可选标签。

    boxes: 方框列表
    labels: 箭头标签列表（长度 = len(boxes) - 1）

    返回：组合后的行列表
    """
    if not boxes:
        return []
    if labels is None:
        labels = [''] * (len(boxes) - 1)

    max_h = max(len(b) for b in boxes)

    segments = []
    for i, box in enumerate(boxes):
        bw = box_width(box)
        padded = list(box) + [' ' * bw] * (max_h - len(box))
        segments.append(padded)

        if i < len(boxes) - 1:
            label = labels[i] if i < len(labels) else ''
            if label:
                arrow_mid = '─' + label + '─►'
            else:
                arrow_mid = '───►'

            arrow_w = visual_width(arrow_mid)
            arrow_h = 1
            top_pad = (max_h - arrow_h) // 2
            bot_pad = max_h - arrow_h - top_pad

            arrow_block = (
                [' ' * arrow_w] * top_pad +
                [arrow_mid] +
                [' ' * arrow_w] * bot_pad
            )
            segments.append(arrow_block)

    result = []
    for row_i in range(max_h):
        line = ''
        for seg in segments:
            if row_i < len(seg):
                line += seg[row_i]
        result.append(line.rstrip())

    return result
```

**示例：**

```python
ha = make_box(["代码检查", "ruff, mypy"], 18)
hb = make_box(["运行测试", "pytest"], 18)
hc = make_box(["构建部署", "Docker"], 18)
layout = connect_boxes_horizontal([ha, hb, hc], ["检查通过", "测试通过"])
print('\n'.join(layout))
```

输出：
```
┌──────────────────┐           ┌──────────────────┐           ┌──────────────────┐
│ 代码检查         │─检查通过─►│ 运行测试         │─测试通过─►│ 构建部署         │
│ ruff, mypy       │           │ pytest           │           │ Docker           │
└──────────────────┘           └──────────────────┘           └──────────────────┘
```

## 辅助函数

```python
def box_width(box):
    """方框视觉宽度（即 ─ 的数量）"""
    return visual_width(box[0])

def _visual_to_char_idx(s, target_visual):
    """视觉列位置 → 字符索引"""
    pos = 0
    for i, ch in enumerate(s):
        cw = 2 if _is_cjk(ch) else 1
        if pos + cw > target_visual:
            return i
        pos += cw
    return len(s) - 1
```

## 资源

- `references/alignment-math.md` — 对齐计算公式与常见错误
- `scripts/verify_alignment.py` — 修改代码后运行此脚本验证所有函数输出对齐

## 开发注意事项（方法学）

### 修改后必须量化验证，不能靠人眼判断

对齐问题本质是视觉渲染问题。代码逻辑通顺 ≠ 输出正确。每次修改后：

1. 打印每行的 `visual_width`，确认所有行相等
2. 打印 `│`、`├`、`┼`、`┤` 的视觉列位置，确认同一列的字符位置一致
3. 只有数值验证通过才算修好

### 先跑最小用例，再跑复杂场景

修改一个函数后，先用最简单的输入验证（1 个方框、2 列表格），确认基础逻辑正确后再用复杂输入。完整脚本输出信息量大，人眼很难发现 1-2 列的偏移。

### 确认函数契约，不靠猜测

对每个关键函数，明确它的输入输出定义：
- `box_width()` 返回的是含角字符的总宽度（`┌` + dashes + `┐`），不是 dash 数量
- `col_width` 是两 `│` 之间的视觉宽度
- `stem_col` 是视觉列位置，`_visual_to_char_idx` 返回字符索引

推导下游使用时需要做怎样的转换，不要假设。

### 表格横线 dash 数量必须等于 col_width（不是 col_width + 2）

内容行格式：`│ ` + cell + ` │ ` + cell + ` │`，两 `│` 之间的视觉宽度正好等于 `col_width`。
横线格式：`├` + dashes + `┼` + dashes + `┤`。为了让 `├┼┤` 与 `│` 在同一视觉列对齐，
dashes 数量必须等于 `col_width`（不是 `col_width + 2`）。

验证方法：打印 `│` 和 `├┼┤` 的视觉列位置，应该完全一致。

### 方框统一宽度时必须重建内容区域，不能直接 pad_to 整行

`connect_boxes_vertical` 统一方框宽度时，错误做法是对整行 `pad_to(line, max_w)` ——这会在右侧 `│` 后面加空格，导致 `│` 位置偏移。

正确做法：提取 `│` 之间的内容（`line[2:-2]`），用 `pad_to(inner, dash_w - 2)` 扩展内容区域（其中 `dash_w = max_w - 2`），然后重新拼接 `'│ ' + inner + ' │'`。这样 `│` 始终在固定位置。

### box_width 返回含角字符的完整宽度

`box_width()` 返回 `visual_width(box[0])`，即 `┌` + dashes + `┐` 的总宽度。在 `connect_boxes_vertical` 中统一宽度时，`─` 的数量应该是 `max_w - 2`（减去两个角字符）。

### 表格分隔线必须用 `┼`（T 型交叉），不能用 `┤`

`├` + `┼` + `┼` + `┤` 形成正确的 T 型交叉结构。用 `┤` 拼接会导致列之间的分隔符形状错误。

## 组合使用示例：CI/CD 全景图

```python
# 表格 + 流程图组合
table = make_table(
    ["阶段", "工具", "输出"],
    [["代码检查", "ruff", "lint 报告"],
     ["测试", "pytest", "覆盖率"],
     ["构建", "Docker", "镜像"]]
)
print('\n'.join(table))
print()
chart = make_flowchart([
    "推送代码",
    "运行代码检查",
    "运行测试",
    ["构建 & 部署", "Docker Compose"],
    "健康检查",
], '通过')
print('\n'.join(chart))
```
