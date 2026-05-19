"""
terminal_ascii_box - CJK-safe ASCII art for terminals.

Usage:
    python terminal_ascii_box.py              # run all demos
    from terminal_ascii_box import make_box   # import in your code

Functions:
    visual_width(s)                           - terminal visual width (CJK=2, ASCII=1)
    pad_to(s, target_w)                       - pad string to visual width w
    make_box(lines, content_w)                - single box with aligned right edge
    make_table(headers, rows, col_widths)     - CJK-safe ASCII table
    make_flowchart(steps, connector_label)    - full vertical flowchart
    make_side_by_side(boxes, gap)             - horizontal layout
    connect_boxes_vertical(boxes, labels)     - vertical connector with stems
    connect_boxes_horizontal(boxes, labels)   - horizontal connector with arrows
    box_width(box)                            - visual width of a box
"""


# ─── Core ───────────────────────────────────────────────

def _is_cjk(ch):
    cp = ord(ch)
    return (0x4e00 <= cp <= 0x9fff or 0x3000 <= cp <= 0x303f or
            0xff00 <= cp <= 0xffef or 0x2000 <= cp <= 0x206f or
            0x3400 <= cp <= 0x4dbf or 0xf900 <= cp <= 0xfaff)


def visual_width(s):
    """Terminal visual width: CJK=2 cols, ASCII=1 col."""
    return sum(2 if _is_cjk(ch) else 1 for ch in s)


def pad_to(s, target_w):
    """Pad string to target visual width with spaces."""
    return s + ' ' * max(0, target_w - visual_width(s))


def make_box(lines, content_w=None):
    """
    CJK-safe ASCII box.

    lines: list of content lines (plain text, no border chars)
    content_w: visual width of content area (= number of dashes).
               If None, auto-size to longest line + 2.

    Returns list of strings.
    """
    if content_w is None:
        content_w = max(visual_width(l) for l in lines) + 2

    slot_w = content_w - 2
    padded = [pad_to(line, slot_w) for line in lines]

    top = '┌' + '─' * content_w + '┐'
    bottom = '└' + '─' * content_w + '┘'
    middle = ['│ ' + l + ' │' for l in padded]
    return [top] + middle + [bottom]


def box_width(box):
    """Visual width of a box (number of dashes)."""
    return visual_width(box[0])


# ─── Table ──────────────────────────────────────────────

def make_table(headers, rows, col_widths=None):
    """
    CJK-safe ASCII table.

    headers: list of header strings
    rows: list of lists (each inner list = one row)
    col_widths: list of visual widths per column. If None, auto-size.

    Returns list of strings.
    """
    ncols = len(headers)

    if col_widths is None:
        col_widths = []
        for c in range(ncols):
            cells = [headers[c]] + [row[c] for row in rows if c < len(row)]
            col_widths.append(max(visual_width(cell) for cell in cells) + 2)

    cells = [pad_to(headers[c], col_widths[c] - 2) for c in range(ncols)]
    header_inner = '│ ' + ' │ '.join(cells) + ' │'

    sep = '├' + '┤'.join('─' * (w + 2) for w in col_widths)

    top = '┌' + '┬'.join('─' * (w + 2) for w in col_widths) + '┐'
    bot = '└' + '┴'.join('─' * (w + 2) for w in col_widths) + '┘'

    data = []
    for row in rows:
        cells = [pad_to(row[c] if c < len(row) else '', col_widths[c] - 2)
                 for c in range(ncols)]
        data.append('│ ' + ' │ '.join(cells) + ' │')

    return [top, header_inner, sep] + data + [bot]


# ─── Layout helpers ─────────────────────────────────────

def make_side_by_side(boxes, gap=2):
    """
    Place boxes side by side, vertically centered.

    boxes: list of box (list of strings)
    gap: number of space columns between boxes

    Returns list of strings.
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


# ─── Flowchart ──────────────────────────────────────────

def connect_boxes_vertical(boxes, labels=None):
    """
    Connect boxes vertically with stem + arrow.

    boxes: list of box (list of strings)
    labels: list of labels for connectors (len = len(boxes) - 1).
            Pass '' or None for unlabeled connectors.

    All boxes are normalized to the same width (max of all).
    Returns list of strings (full flowchart).
    """
    if not boxes:
        return []

    if labels is None:
        labels = [''] * (len(boxes) - 1)

    max_w = max(box_width(b) for b in boxes)
    normalized = []
    for b in boxes:
        bw = box_width(b)
        if bw < max_w:
            padded = [pad_to(line, max_w) for line in b]
            padded[0] = '┌' + '─' * max_w + '┐'
            padded[-1] = '└' + '─' * max_w + '┘'
            normalized.append(padded)
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
            conn = (' ' * (stem_col - 1) + '│ ' + label) if label else \
                    ' ' * (stem_col - 1) + '│'
            result.append(pad_to(conn, max_w))
            result.append(pad_to(' ' * (stem_col - 1) + '▼', max_w))

    return result


def connect_boxes_horizontal(boxes, labels=None):
    """
    Connect boxes horizontally with arrow + optional label.

    boxes: list of box (list of strings)
    labels: list of labels for arrows (len = len(boxes) - 1)

    Returns list of strings.
    """
    if not boxes:
        return []
    if labels is None:
        labels = [''] * (len(boxes) - 1)

    max_h = max(len(b) for b in boxes)

    segments = [list(boxes[0])]
    for i in range(1, len(boxes)):
        label = labels[i - 1] if i - 1 < len(labels) else ''

        if label:
            arrow_line = '  ─' + ' ' + label + ' ' + '─►  '
        else:
            arrow_line = '  ────►  '

        arrow_h = 3
        top_pad = (max_h - arrow_h) // 2
        bot_pad = max_h - arrow_h - top_pad

        arrow_block = (
            [''] * top_pad +
            [arrow_line] +
            [''] * bot_pad
        )
        segments.append(arrow_block)
        segments.append(list(boxes[i]))

    result = []
    for row_i in range(max_h):
        line = ''
        for seg in segments:
            if row_i < len(seg):
                line += seg[row_i]
            line += '  '
        line = line.rstrip()
        result.append(line)

    return result


def make_flowchart(steps, connector_label='通过'):
    """
    Quick flowchart from step names.

    steps: list of elements. Each element can be:
           - str: single-line box
           - list/tuple of str: multi-line box
    connector_label: label on each vertical connector

    Returns list of strings.
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


# ─── Helpers ────────────────────────────────────────────

def _visual_to_char_idx(s, target_visual):
    """Find character index corresponding to a visual column position."""
    pos = 0
    for i, ch in enumerate(s):
        cw = 2 if _is_cjk(ch) else 1
        if pos + cw > target_visual:
            return i
        pos += cw
    return len(s) - 1


# ─── Demo ───────────────────────────────────────────────

if __name__ == '__main__':
    def show(title, lines):
        print(f"\n{'='*50}")
        print(f"  {title}")
        print(f"{'='*50}")
        for line in lines:
            print(line)

    show("1. 基础方框", make_box([
        "GitHub Actions 工作流",
        "",
        "触发：push 到 main 分支",
        "触发：PR 合并请求",
        "",
        "步骤：",
        "  1. 检出代码",
        "  2. 安装依赖",
        "  3. 运行测试",
    ], 28))

    show("2. ASCII 表格", make_table(
        ["平台", "配置方式", "免费额度", "适用场景"],
        [
            ["GitHub Actions", "YAML", "开源无限", "最主流"],
            ["GitLab CI", ".gitlab-ci.yml", "开源自建", "企业内网"],
            ["Jenkins", "Groovy DSL", "完全免费", "老牌插件多"],
            ["CircleCI", "YAML", "开源免费", "快速上手"],
        ]
    ))

    show("3. 垂直流程图", make_flowchart([
        ["开发者提交代码", "commit / PR"],
        "触发 CI Pipeline",
        "1. Lint 与静态检查",
        "2. 单元测试",
        "3. 集成测试",
        "4. 安全扫描",
        "5. 构建打包",
        ["6. 部署到环境", "staging → production"],
        "7. 健康检查与监控",
    ], '通过'))

    b1 = make_box(["开发环境", "dev.example.com", "宽松配置"], 20)
    b2 = make_box(["预发布环境", "stg.example.com", "镜像生产"], 20)
    b3 = make_box(["生产环境", "prod.example.com", "高可用"], 20)
    show("4. 并排布局", make_side_by_side([b1, b2, b3]))

    ha = make_box(["代码检查", "ruff, mypy"], 18)
    hb = make_box(["运行测试", "pytest"], 18)
    hc = make_box(["构建部署", "Docker"], 18)
    show("5. 水平连接", connect_boxes_horizontal(
        [ha, hb, hc], ["检查通过", "测试通过"]
    ))

    show("6. 不同大小方框垂直连接", connect_boxes_vertical([
        make_box(["短标题"]),
        make_box(["这个标题比较长一些", "还有第二行内容"]),
        make_box(["再一个"]),
    ], ["", "OK"]))
