# terminal-ascii-box-cjk-alignment

CJK-safe ASCII art for terminals. Draw boxes, tables, and flowcharts with properly aligned right borders — even when content mixes Chinese/Japanese/Korean characters with ASCII.

## Why

CJK characters occupy **2 terminal columns**, ASCII characters occupy **1**. Naive string padding breaks right-edge alignment. This library calculates visual width correctly so all borders stay aligned.

## Functions

| Function | Description |
|---|---|
| `make_box(lines, content_w)` | Single box with aligned right edge |
| `make_table(headers, rows, col_widths)` | Multi-column ASCII table |
| `connect_boxes_vertical(boxes, labels)` | Vertical flowchart with stems and arrows |
| `connect_boxes_horizontal(boxes, labels)` | Horizontal flowchart with arrows |
| `make_flowchart(steps, connector_label)` | Quick flowchart from step names |
| `make_side_by_side(boxes, gap)` | Horizontal layout, vertically centered |
| `visual_width(s)` | Terminal visual width (CJK=2, ASCII=1) |
| `pad_to(s, target_w)` | Pad string to target visual width |

## Examples

### Box

```python
from terminal_ascii_box import make_box

box = make_box([
    "GitHub Actions 工作流",
    "",
    "触发：push 到 main 分支",
], 28)
print('\n'.join(box))
```

```
┌────────────────────────────┐
│ GitHub Actions 工作流      │
│                            │
│ 触发：push 到 main 分支    │
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

```
┌────────────────┬────────────────┬──────────┐
│ 平台           │ 配置方式       │ 适用场景 │
├────────────────┼────────────────┼──────────┤
│ GitHub Actions │ YAML           │ 最主流   │
│ GitLab CI      │ .gitlab-ci.yml │ 企业内网 │
└────────────────┴────────────────┴──────────┘
```

### Flowchart

```python
from terminal_ascii_box import make_flowchart

chart = make_flowchart([
    "触发 CI Pipeline",
    "1. Lint 与静态检查",
    "2. 单元测试",
    ["3. 部署到环境", "staging → production"],
], '通过')
print('\n'.join(chart))
```

```
┌────────────────────────┐
│ 触发 CI Pipeline     │
└───────────┬────────────┘
           │ 通过       
           ▼            
┌────────────────────────┐
│ 1. Lint 与静态检查   │
└───────────┬────────────┘
           │ 通过       
           ▼            
┌────────────────────────┐
│ 2. 单元测试          │
└───────────┬────────────┘
           │ 通过       
           ▼            
┌──────────────────────┐
│ 3. 部署到环境        │
│ staging → production │
└──────────────────────┘
```

### Side by side

```python
from terminal_ascii_box import make_box, make_side_by_side

b1 = make_box(["开发环境", "dev.example.com"], 20)
b2 = make_box(["生产环境", "prod.example.com"], 20)
layout = make_side_by_side([b1, b2])
print('\n'.join(layout))
```

```
┌────────────────────┐  ┌────────────────────┐
│ 开发环境           │  │ 生产环境           │
│ dev.example.com    │  │ prod.example.com   │
└────────────────────┘  └────────────────────┘
```

### Horizontal flow

```python
from terminal_ascii_box import make_box, connect_boxes_horizontal

ha = make_box(["代码检查", "ruff, mypy"], 18)
hb = make_box(["运行测试", "pytest"], 18)
hc = make_box(["构建部署", "Docker"], 18)
layout = connect_boxes_horizontal([ha, hb, hc], ["检查通过", "测试通过"])
print('\n'.join(layout))
```

```
┌──────────────────┐    ─ 检查通过 ─►    ┌──────────────────┐    ─ 测试通过 ─►    ┌──────────────────┐
│ 代码检查         │    │ 运行测试         │    │ 构建部署         │
│ ruff, mypy       │    │ pytest           │    │ Docker           │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

## Install as Hermes Skill

```bash
hermes skills install https://raw.githubusercontent.com/Andy365-365/hermes-skills/main/terminal-ascii-box-cjk-alignment/SKILL.md
```

## Usage as Python Library

```bash
# Run demos
python scripts/terminal_ascii_box.py

# Import in your code
from terminal_ascii_box import make_box, make_table, make_flowchart
```

## License

MIT
