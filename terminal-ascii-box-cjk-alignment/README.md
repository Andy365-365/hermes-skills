# terminal-ascii-box-cjk-alignment

CJK-safe ASCII art for terminals. Draw boxes, tables, and flowcharts with properly aligned right borders — even when content mixes Chinese/Japanese/Korean characters.

## Problem

Terminal CJK characters take **2 columns**, ASCII takes **1 column**. Naive space-padding misaligns right edges.

## Quick Start

```bash
hermes skills install https://raw.githubusercontent.com/Andy365-365/hermes-skills/main/terminal-ascii-box-cjk-alignment/SKILL.md
```

Or copy `scripts/terminal_ascii_box.py` into your project.

## Functions

| Function | Description |
|---|---|
| `visual_width(s)` | Terminal visual width (CJK=2, ASCII=1) |
| `pad_to(s, target_w)` | Pad string to target visual width |
| `make_box(lines, content_w)` | Single box with aligned borders |
| `make_table(headers, rows, col_widths)` | Multi-column ASCII table |
| `connect_boxes_vertical(boxes, labels)` | Vertical flowchart with connectors |
| `make_flowchart(steps, connector_label)` | Quick vertical flowchart from step names |
| `make_side_by_side(boxes, gap)` | Horizontal side-by-side layout |
| `connect_boxes_horizontal(boxes, labels)` | Horizontal flowchart with arrows |
| `box_width(box)` | Visual width of a box |

## Examples

### Box

```python
from terminal_ascii_box import make_box
box = make_box([
    "GitHub Actions 工作流",
    "",
    "触发：push 到 main 分支",
    "触发：PR 合并请求",
], 28)
print('\n'.join(box))
```

Output:

```
┌────────────────────────────┐
│ GitHub Actions 工作流      │
│                            │
│ 触发：push 到 main 分支    │
│ 触发：PR 合并请求          │
└────────────────────────────┘
```

### Table

```python
from terminal_ascii_box import make_table
table = make_table(
    ["平台", "配置方式", "适用场景"],
    [
        ["GitHub Actions", "YAML", "最主流"],
        ["GitLab CI", ".gitlab-ci.yml", "企业内网"],
    ]
)
print('\n'.join(table))
```

Output:

```
┌────────────────┬────────────────┬──────────┐
│ 平台           │ 配置方式       │ 适用场景 │
├────────────────┼────────────────┼──────────┤
│ GitHub Actions │ YAML           │ 最主流   │
│ GitLab CI      │ .gitlab-ci.yml │ 企业内网 │
└────────────────┴────────────────┴──────────┘
```

### Vertical Flowchart

```python
from terminal_ascii_box import make_box, connect_boxes_vertical
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

Output:

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

### Horizontal Flowchart

```python
from terminal_ascii_box import make_box, connect_boxes_horizontal
ha = make_box(["代码检查", "ruff, mypy"], 18)
hb = make_box(["运行测试", "pytest"], 18)
hc = make_box(["构建部署", "Docker"], 18)
chart = connect_boxes_horizontal([ha, hb, hc], ["检查通过", "测试通过"])
print('\n'.join(chart))
```

Output:

```
┌──────────────────┐           ┌──────────────────┐           ┌──────────────────┐
│ 代码检查         │─检查通过─►│ 运行测试         │─测试通过─►│ 构建部署         │
│ ruff, mypy       │           │ pytest           │           │ Docker           │
└──────────────────┘           └──────────────────┘           └──────────────────┘
```

### Side by Side

```python
from terminal_ascii_box import make_box, make_side_by_side
b1 = make_box(["开发环境", "dev.example.com"], 20)
b2 = make_box(["预发布环境", "stg.example.com"], 20)
b3 = make_box(["生产环境", "prod.example.com"], 20)
layout = make_side_by_side([b1, b2, b3])
print('\n'.join(layout))
```

Output:

```
┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐
│ 开发环境           │  │ 预发布环境         │  │ 生产环境           │
│ dev.example.com    │  │ stg.example.com    │  │ prod.example.com   │
└────────────────────┘  └────────────────────┘  └────────────────────┘
```
