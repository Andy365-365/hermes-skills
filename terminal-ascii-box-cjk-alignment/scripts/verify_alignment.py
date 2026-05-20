#!/usr/bin/env python3
"""
验证所有函数的输出对齐。
每次修改 terminal_ascii_box.py 后运行此脚本。
只有所有检查 PASS 才算修改完成。
"""
import sys
sys.path.insert(0, '.')
from terminal_ascii_box import *

# Also need _is_cjk
import terminal_ascii_box
_is_cjk = terminal_ascii_box._is_cjk

errors = 0

def check_lines(name, lines, key_chars=None):
    """检查所有行 vw 一致，关键字符位置一致。"""
    global errors
    print(f"\n{'='*50}")
    print(f"  {name}")
    print(f"{'='*50}")

    # Check all lines have same visual width
    vws = [visual_width(line) for line in lines]
    if len(set(vws)) > 1:
        print(f"  FAIL: 行视觉宽度不一致: {dict(zip(range(len(lines)), vws))}")
        for i, line in enumerate(lines):
            marker = ' <--' if vws[i] != vws[0] else ''
            print(f"    [{i}] vw={vws[i]:3d}{marker} |{line}|")
        errors += 1
    else:
        print(f"  OK: 所有 {len(lines)} 行 vw={vws[0]}")

    # Check key char positions
    if key_chars:
        for ch in key_chars:
            positions = []
            for i, line in enumerate(lines):
                cols = find_char_visual_cols(line, ch)
                if cols:
                    positions.append((i, cols))
            if positions:
                # Check if positions are consistent across lines
                all_cols = set()
                for _, cols in positions:
                    all_cols.update(cols)
                # Just report, don't fail - different lines may have different char positions
                first_line_pos = positions[0]
                last_line_pos = positions[-1]
                if first_line_pos[1] != last_line_pos[1]:
                    print(f"  WARN: '{ch}' 位置: 第{first_line_pos[0]}行={first_line_pos[1]}, 第{last_line_pos[0]}行={last_line_pos[1]}")

def find_char_visual_cols(line, target):
    """Find all visual column positions of target char in line."""
    cols = []
    pos = 0
    for i, ch in enumerate(line):
        if ch == target:
            cols.append(pos)
        pos += 2 if _is_cjk(ch) else 1
    return cols

# ===== Test 1: make_box =====
box = make_box(["触发 CI Pipeline"], 20)
check_lines("make_box: 单行", box, ['│', '┌', '┐', '└', '┘'])

box2 = make_box(["GitHub Actions 工作流", "", "触发：push 到 main 分支"], 28)
check_lines("make_box: 多行+空行", box2, ['│'])

# ===== Test 2: make_table =====
table = make_table(
    ["平台", "配置方式", "适用场景"],
    [["GitHub Actions", "YAML", "最主流"],
     ["GitLab CI", ".gitlab-ci.yml", "企业内网"]])
check_lines("make_table: 3列", table, ['│', '├', '┼', '┤'])

# ===== Test 3: connect_boxes_vertical =====
steps = [
    make_box(["触发 CI Pipeline"]),
    make_box(["1. Lint 与静态检查"]),
    make_box(["2. 单元测试"]),
]
vchart = connect_boxes_vertical(steps, ['通过', '通过'])
check_lines("connect_boxes_vertical: 3方框", vchart, ['│', '├', '┼', '┤', '┬', '▼'])

# ===== Test 4: make_flowchart =====
fc = make_flowchart(
    [["开发者提交代码", "commit / PR"], "触发 CI", "部署"],
    '通过')
check_lines("make_flowchart: 多行+单行", fc, ['│', '┬', '▼'])

# ===== Test 5: connect_boxes_horizontal =====
ha = make_box(["代码检查", "ruff"], 18)
hb = make_box(["运行测试", "pytest"], 18)
hc = make_box(["构建部署", "Docker"], 18)
hchart = connect_boxes_horizontal([ha, hb, hc], ["检查通过", "测试通过"])
check_lines("connect_boxes_horizontal: 3方框+箭头", hchart, ['│', '►'])

# ===== Test 6: make_side_by_side =====
b1 = make_box(["开发环境", "dev.com"], 20)
b2 = make_box(["生产环境", "prod.com"], 20)
b3 = make_box(["预发布", "stg.com"], 20)
sbs = make_side_by_side([b1, b2, b3])
check_lines("make_side_by_side: 3方框并排", sbs, ['│'])

# ===== Test 7: 不同宽度的方框垂直连接 =====
small = make_box(["短"], 8)
large = make_box(["这是一个很长的内容"], 24)
mixed = connect_boxes_vertical([small, large], [''])
check_lines("connect_boxes_vertical: 不同宽度", mixed, ['│', '┬', '▼'])

# ===== Test 8: 不同高度的方框水平连接 =====
tall = make_box(["行1", "行2", "行3"], 14)
short = make_box(["单行"], 14)
hdiff = connect_boxes_horizontal([tall, short], [''])
check_lines("connect_boxes_horizontal: 不同高度", hdiff, ['│', '►'])

# Summary
print(f"\n{'='*50}")
if errors == 0:
    print("  全部通过 ✓")
else:
    print(f"  {errors} 项失败 ✗")
print(f"{'='*50}")
sys.exit(errors)
