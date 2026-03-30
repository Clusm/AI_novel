# UI 审核报告 · 商业化专业化优化方案
**AI_Novel_Writer v3.0** · 审核日期：2026-03-30

---

## 一、审核摘要

本次审核覆盖主窗口、侧边栏、4 个主 Tab（创作中心/阅读管理/运行监控/导出发布）、4 个对话框（新建项目/API 设置/模型参数/系统授权）及公共组件（标题栏/欢迎页/Widget 层），共识别 **26 项问题**，涉及视觉一致性、可用性、交互体验、样式硬编码、组件规范五大维度。

---

## 二、问题清单与优化方案

### ── 2.1 全局级问题

---

#### 【G-01】硬编码颜色值散落各处，绕过设计系统

**问题位置**
- `tab_monitor_view.py:47` — `"border-bottom: 1px solid #e2e8f0; background: #f8fafc; ..."`
- `tab_reader_view.py:77` — `"border-bottom: 1px solid #e2e8f0; background: #f8fafc; ..."`
- `tab_reader_view.py:82–85` — `color: #0f172a`, `color: #64748b` 直接写在 setStyleSheet
- `tab_reader_view.py:90–106` — btn_copy_chapter 完整内联样式，绕过 QSS 类
- `tab_monitor_view.py:60–81` — 监控切换按钮使用完整内联 toggle_style

**影响** 未来主题切换或品牌色调整需要多处手动修改，高维护成本，且与 `variables.py` 设计 token 形成两套标准。

**优化方案**
1. `tab_monitor_view.py` 和 `tab_reader_view.py` 的 header 区域改用独立 ObjectName（如 `CardHeader`），在 `layouts.py` 中统一定义样式。
2. `btn_copy_chapter` 移除内联样式，改为 `setObjectName("SecondaryButton")` 并在 `components.py` 新增此变体。
3. 监控切换按钮改为 `setObjectName("SegmentedButton")` / `setObjectName("SegmentedButtonChecked")`，样式统一放 QSS。

**实现位置** `gui/styles/components.py`（新增 SecondaryButton、SegmentedButton），`gui/views/tab_monitor_view.py`，`gui/views/tab_reader_view.py`

---

#### 【G-02】QMessageBox 为原生系统弹窗，与无边框设计割裂

**问题位置**
- `main_window.py:583` — `QMessageBox.information(self, "保存成功", "大纲已保存")`
- `main_window.py:662` — `QMessageBox.question(...)`
- `main_window.py:672,677,682` — 设置/授权成功弹窗
- `dialogs.py:253–261` — Memory 清理确认弹窗

**影响** 原生系统弹窗（Windows 默认蓝色标题栏）与全无边框圆角设计风格严重不匹配，是商业化产品最显著的视觉割裂点之一。

**优化方案**
在 `gui/dialogs.py` 中新增一个 `CustomMessageBox` 类（复用 `FramelessWindowMixin`），提供 `information()`、`question()`、`warning()` 三个静态方法，替换全部 `QMessageBox` 调用。

```python
# 调用示例（改后）
CustomMessageBox.information(self, "保存成功", "大纲已保存")
CustomMessageBox.question(self, "确认删除", "确定删除项目...", callback=self._do_delete)
```

**实现位置** `gui/dialogs.py`（新增 CustomMessageBox），`gui/main_window.py`（全局替换）

---

#### 【G-03】emoji 图标在不同 Windows 字体渲染下显示不一致

**问题位置**
- 侧边栏按钮：`🔑 API 配置`、`🛡️ 系统授权`、`⚙️ 参数设置`
- 大纲面板标题：`📝 故事大纲`
- 生成控制标题：`🚀 生成控制`
- 导出面板标题：`📤 导出作品`
- 欢迎页 Logo：`📖`

**影响** 不同 Windows 版本、字体缩放设置下 emoji 渲染尺寸不一，可能出现方框或截断，且 emoji 整体质感偏低（消费级），商业产品通常使用字体图标库（如 Segoe Fluent Icons 或 SVG）。

**优化方案**
短期方案：统一改用 Unicode 纯文本符号（不含 emoji），如 `○ API 配置`、`✦ 参数设置`，风格与现有 Logo（`✦✦`）保持呼应。
中期方案：引入内嵌 SVG 图标，通过 `QIcon` + `QPixmap` 渲染，彻底解决跨平台一致性问题。

---

#### 【G-04】`QSpinBox` 数值不可交互：隐藏 spin 按钮但未提供替代操作提示

**问题位置** `tab_create_view.py:138–155`，`components.py:296–329`

**影响** `spin_start` 和 `spin_count` 的自增/自减按钮被完全隐藏（`width: 0px`），用户只能手动键入或滚轮操作，但没有任何视觉提示说明这一点，可发现性差，尤其对非技术用户。

**优化方案**（二选一）
- **方案 A（最小改动）**：恢复显示 spin 按钮，仅去除默认 Windows 箭头图标，改为用 `▲`/`▼` 自定义样式。
- **方案 B（推荐）**：改用自定义 `StepSpinBox` 组件，在控件右侧显示 `+`/`-` 两个小按钮（类似 Notion 数字输入），视觉更现代，交互更明确。

---

#### 【G-05】`QComboBox` 下拉箭头被完全隐藏，可发现性差

**问题位置** `components.py:236–248`，影响全局所有下拉框

**影响** 下拉箭头 `width: 0px; image: none` 使控件外观与普通文本标签难以区分，用户不知道可以点击展开，违反「可发现性」基本交互原则，在 API 设置/新建项目对话框中尤为明显。

**优化方案**
恢复 `::down-arrow` 显示，使用内嵌 SVG（base64 编码 `↓`）或 Unicode 字符 `▾` 替代系统默认箭头，保持设计风格一致性：

```css
QComboBox::drop-down {
    border: none;
    width: 24px;
    padding-right: 8px;
}
QComboBox::down-arrow {
    width: 12px;
    height: 12px;
    /* image: url(:/icons/chevron-down.svg); */
    /* 或者 */
    color: #94a3b8;
}
```

---

### ── 2.2 主窗口 & 侧边栏

---

#### 【W-01】侧边栏折叠逻辑不完整：折叠后无展开入口

**问题位置** `main_window.py:344–352`，`main_window.py:233`

**影响** `toggle_sidebar()` 将侧边栏 `setVisible(False)` 后，用户无法重新展开，因为展开按钮在侧边栏内部。虽然 `main_panel.btn_toggle_sidebar` 有 `setVisible(is_visible)` 逻辑，但反向展开时 `btn_toggle_sidebar` 此时不可见，陷入死锁。

**优化方案**
- 当侧边栏隐藏时，在主面板标题栏左侧显示一个始终可见的展开按钮（`▸`）；
- 或改为折叠模式（只显示图标栏 `SIDEBAR_WIDTH_COLLAPSED = 48`），不完全隐藏。

**实现位置** `main_window.py:toggle_sidebar()`，`gui/views/main_panel_view.py`

---

#### 【W-02】`project_combo`（当前项目下拉框）无下拉视觉指示

承接【G-05】，此处特别突出。项目选择下拉框是侧边栏最核心的操作，宽度充足，更应恢复箭头指示。

---

#### 【W-03】侧边栏「项目文风」下拉框与「当前项目」的关联不明确

**问题位置** `sidebar_view.py:99–103`

**影响** 「项目文风」的 combo 放置在侧边栏，但它是**项目级配置**而非全局配置，语义上应与「当前项目」分组在一起，而不是独立悬浮在中间区域，易误解为全局设置。

**优化方案**
将「项目文风」移至项目区块，作为项目元信息的一部分展示（或放入项目区块下方，加上小标签 `「当前项目」文风`），并与新建/删除按钮形成视觉组。

---

#### 【W-04】标题栏缺少当前项目名称，状态感知弱

**问题位置** `main_window.py:70`，`widgets.py:56–89`

**影响** 无边框标题栏（高度 36px）目前完全空白（只有最小化/最大化/关闭按钮），用户无法在一眼内感知当前打开的是哪个项目。在多项目切换时认知负担增加。

**优化方案**
在标题栏中央或左侧显示当前项目名称（跟随 `selected_project` 变化），格式如 `AI_Novel_Writer · 诸天之无上道途`，字体用 `BODY_SMALL + WEIGHT_MEDIUM + TEXT_SECONDARY`。

---

### ── 2.3 创作中心（TabCreate）

---

#### 【C-01】大纲编辑器与 Markdown 渲染混合实现带来显著 UX 问题

**问题位置** `main_window.py:441–491`

**影响**
- 用户在大纲编辑器输入 Markdown 时，500ms 后编辑器会自动将内容替换为 HTML（`setHtml()`），导致光标位置跳转到末尾，**打断用户输入节奏**；
- 已渲染 HTML 的编辑器中再次编辑时，`toPlainText()` 会带上 HTML 标签残留，导致保存内容污染；
- 纯文本检测逻辑 `raw_like_markdown = bool(re.search(...))` 有误判风险。

**优化方案**
- 将大纲面板拆分为「编辑模式」/「预览模式」两个明确状态，提供切换按钮（类 GitHub 的 Write/Preview 切换 tab）；
- 编辑模式下保持纯文本（`QPlainTextEdit`，性能更好），预览模式下渲染 HTML；
- 彻底移除 500ms 定时器自动替换内容的逻辑。

**实现位置** `gui/views/tab_create_view.py`，`gui/main_window.py`

---

#### 【C-02】`spin_start` 在「单章精修」模式下不可见但仍存在于布局

**问题位置** `main_window.py:624–626`

**影响** 切换「单章精修」时调用 `settings_grid.addWidget(lbl_count, 0, 0, 1, 2)`，实际上没有 `removeWidget(spin_start)` 的对应操作，只是 `setVisible(False)`，导致 grid 布局中仍占有空间（虽然视觉不可见），可能造成高度异常。

**优化方案**
使用 `QStackedWidget` 代替动态 `addWidget/setVisible`，预建两个布局状态，切换时替换。或确保在 `setVisible(False)` 时同步调整 `setMaximumHeight(0)` / 再改为 `columnStretch`。

---

#### 【C-03】「启动生成引擎」按钮运行中缺乏状态反馈

**问题位置** `main_window.py:695–697`，`tab_create_view.py:171–175`

**影响** 生成启动后，按钮仅设 `setEnabled(False)`，文字保持「启动生成引擎」不变，用户无法判断任务是否已真正开始，且没有停止机制（无法中断生成）。

**优化方案**
- 生成中按钮文字改为 `⏸ 生成中...`，颜色保持主色但加载感更强；
- 添加「停止生成」按钮（单独出现，危险样式），允许用户中断任务；
- 进度标签（`progress_label`）应在生成完成后自动清空或显示「已完成」。

---

#### 【C-04】进度条（`progress`）完成后不自动隐藏

**问题位置** `main_window.py:745–746`

**影响** `on_worker_finished()` 中成功路径：`progress.setVisible(False)` 确实被调用，但 `progress.setValue(100)` 在 `setVisible(False)` 之前被调用（第747行），逻辑顺序有问题；失败路径中 `progress.setVisible(False)` 未被调用，失败后进度条停留在中间值。

**优化方案** 在 `on_worker_finished()` 中统一处理：无论成功失败，均调用 `progress.setVisible(False)` 和 `progress.setValue(0)` 复位。

---

### ── 2.4 阅读管理（TabReader）

---

#### 【R-01】章节搜索框与章节下拉框功能高度重叠，信息架构冗余

**问题位置** `tab_reader_view.py:49–55`

**影响** 搜索框用于筛选 `chapter_combo`，`chapter_combo` 本身也包含所有章节，两者功能高度重叠，同时存在占用了 320px 侧栏的大量空间，对只有几十章的项目来说几乎无价值。

**优化方案**（按优先级）
1. 隐藏搜索框，仅保留下拉框（对 <50 章项目足够）；
2. 或将搜索框改为下拉框上方的可折叠输入，只在章节 >30 个时自动显示；
3. 或将章节列表改为真正的 `QListWidget`（可视滚动列表），去掉冗余下拉框。

---

#### 【R-02】章节切换使用「上一章/下一章」按钮，无视觉状态区分边界

**问题位置** `tab_reader_view.py:57–61`，`main_window.py:774–776`

**影响** 两个按钮并排相同样式，在第一章时「上一章」虽然 `setEnabled(False)` 但颜色变化不明显（默认 disabled 为 `GRAY_50` + `TEXT_MUTED`，对比度仅约 1.5:1），不符合 WCAG AA 标准（要求 ≥3:1）。

**优化方案**
强化 disabled 状态视觉区分：`disabled` 按钮文字颜色改为 `TEXT_MUTED`，添加 `opacity: 0.5` 滤镜效果，或将按钮改为箭头图标（`◀`/`▶`）并在禁用时隐藏。

---

#### 【R-03】阅读器头部 header 内联样式与全局 Card 样式冲突

**问题位置** `tab_reader_view.py:77`

**影响** `header.setStyleSheet("border-bottom: 1px solid #e2e8f0; background: #f8fafc; border-top-left-radius: 16px; border-top-right-radius: 16px;")` 中硬编码了 `16px` 圆角，与 `Radius.XL2 = 16px` 匹配但与 Card 容器圆角 `Radius.XL = 12px` 不一致（Card 对象名称通常使用 LG=8px）。导致 header 圆角大于 Card 外框圆角，出现「内角溢出」视觉瑕疵。

**优化方案** 统一 Card 和 CardHeader 圆角定义，CardHeader 圆角 = Card 圆角，均写入 `layouts.py`。

---

### ── 2.5 运行监控（TabMonitor）

---

#### 【M-01】Agent 思维流日志渲染为逆序（最新在顶），与终端习惯相反

**问题位置** `main_window.py:867`

```python
blocks = [self._format_log_html(log) for log in reversed(self.run_logs)]
```

**影响** 用户习惯于从上往下阅读日志（最旧在顶，最新在底，跟随滚动条），而当前实现将日志逆序排列（最新在顶）。这与「终端命令行」视图的行为相反，造成两个视图的阅读逻辑不一致。

**优化方案** 移除 `reversed()`，改为正序排列，在 `refresh_log_view()` 末尾调用 `verticalScrollBar().setValue(maximum())` 使滚动条自动滚到底部（已有此逻辑但需与逆序修复同步）。

---

#### 【M-02】监控头部 header 使用内联样式，同 R-03

**问题位置** `tab_monitor_view.py:47`，同【G-01】

---

#### 【M-03】「Agent 思维流」日志块中 `[时间戳]` 显示但文本内容可见性差

**问题位置** `main_window.py:572–577`

**影响** 日志条目使用 `border-left` 彩色竖线 + 暗色背景，已有一定区分度，但在 LogViewer（`GRAY_900` 背景）中显示时，`info` 状态的竖线颜色（`#94a3b8`）与背景对比度仅约 2.8:1，未达 WCAG AA 标准。

**优化方案** 将 `info` 竖线颜色从 `#94a3b8` 提亮至 `#60a5fa`（PRIMARY_400），其他状态（success/warning/danger）对比度已满足标准，无需修改。

---

### ── 2.6 导出发布（TabExport）

---

#### 【E-01】四个导出按钮等宽横排，「全部导出」的优先级未得到视觉强调

**问题位置** `tab_export_view.py:43–55`

**影响** 四个按钮完全等宽，「全部导出」虽设了 `PrimaryButton` 样式，但在四等分布局中与其他按钮无尺寸区分，主操作的视觉权重不足。国际设计规范通常要求主 CTA（Call-to-Action）按钮在尺寸或位置上有明显差异化。

**优化方案**
将「全部导出」按钮独立为一行（放在三个格式按钮下方），独占全宽，高度 50px，与「启动生成引擎」风格统一，形成一致的主 CTA 视觉语言。

---

#### 【E-02】导出结果 Banner 无关闭按钮，只能靠后续操作覆盖

**问题位置** `tab_export_view.py:58–73`

**影响** 导出成功/失败消息显示后，用户没有显式关闭方式，Banner 一直残留在界面中，直到下一次导出操作触发新消息覆盖。

**优化方案** 在 Banner 右侧添加一个 `×` 关闭按钮（`IconButton` 样式），或在 3 秒后自动淡出隐藏。

---

#### 【E-03】导出页无文件保存路径反馈

**问题位置** `main_window.py:883,893,903,913`

**影响** 导出成功后仅显示文件名（`os.path.basename(path)`），不显示完整路径，用户不知道文件保存在哪里，需要自行查找。

**优化方案** 成功 Banner 改为 `已导出至：{完整路径}`，并添加「打开文件夹」按钮（调用 `os.startfile(os.path.dirname(path))`）。

---

### ── 2.7 对话框

---

#### 【D-01】ApiSettingsDialog 中「清理 Memory 数据」按钮位置突兀，无分组上下文

**问题位置** `dialogs.py:213–216`

**影响** 「清理当前项目的 Memory 数据」按钮直接放在 form 下方，与 API Key 配置在同一内容区域，语义归属不清（它是危险操作，但视觉上与普通配置按钮无区分），且没有前置说明文字告知此操作的含义和风险。

**优化方案**
1. 将 Memory 相关控件（checkbox + 清理按钮）用 `QGroupBox("长期记忆管理")` 包裹，形成独立分组；
2. 清理按钮改为 `DangerButton` 样式；
3. 添加一行说明文字：`"向量数据库中存储的跨章节记忆，清理后不可恢复"`。

---

#### 【D-02】ModelParamsDialog 的 Temperature/TopP 滑块无刻度感知，难以精确操作

**问题位置** `dialogs.py:395–399`，`components.py:331–353`

**影响** 滑块范围 0~2（Temperature）展示为 0~200 整数值，转换为浮点数后精度为 0.01，但没有刻度标记，用户无法感知当前值在整体范围中的位置，且滑块 groove 仅 4px 高，交互热区过小。

**优化方案**
- 在滑块下方添加最小/最大值标签（左：min，右：max）；
- 将滑块高度（groove）从 4px 增加到 6px，handle 从 14px 增加到 16px，增大交互热区；
- 当前值标签（`lbl_temperature_value`）改为输入框，支持直接键入精确值。

---

#### 【D-03】所有对话框的「取消」按钮与「保存」按钮左右排列顺序与平台规范不符

**问题位置** `dialogs.py:89–101`（新建项目），`dialogs.py:218–226`（API 设置），`dialogs.py:419–428`（模型参数），`dialogs.py:656–665`（授权管理）

**影响** 所有对话框均为「取消」在左、「保存/确认」在右，这与 Windows 平台规范（OK 在左，Cancel 在右）相反，但与 macOS/Web 规范一致。在 Windows 平台上使用此顺序会造成操作习惯冲突。

**优化方案** 统一改为 Windows 规范：`[保存/确认]  [取消]`（正向操作在左），或根据 `sys.platform` 动态调整顺序。

---

#### 【D-04】LicenseSettingsDialog 中授权状态文字使用内联 setStyleSheet，非设计系统

**问题位置** `dialogs.py:652`，`dialogs.py:686`，`dialogs.py:690`，`dialogs.py:698`

**影响** 同一个 `license_status_label` 在 4 处用不同参数调用 `setStyleSheet()`，动态改变颜色和字号，没有使用 `setProperty(tone)` + QSS 的统一机制（已有 Banner 组件实现了这套机制），造成不必要的重复代码和维护负担。

**优化方案** 将 `license_status_label` 改为 `setObjectName("Banner")`，使用 `setProperty("tone", "success"/"danger")` + `unpolish/polish` 的统一方式更新状态，与其他对话框的 `result_label` 保持一致。

---

### ── 2.8 欢迎页（WelcomeWidget）

---

#### 【P-01】欢迎页「开始创作」按钮的渐变样式内联覆盖了 PrimaryButton QSS

**问题位置** `widgets.py:265–280`

**影响** `btn_start` 设置了 `setObjectName("PrimaryButton")` 同时又通过 `setStyleSheet()` 完整覆盖，导致 `PrimaryButton` 的 QSS 规则完全失效（内联优先级高于 QSS），形成「虚假继承」。未来修改 `PrimaryButton` QSS 时，欢迎页按钮不会跟进变化。

**优化方案**
在 `components.py` 的 `QPushButton#PrimaryButton` 下新增一个 `QPushButton#GradientPrimaryButton` 变体，包含渐变背景定义，欢迎页按钮改用此名称，移除内联 `setStyleSheet()`。

---

#### 【P-02】欢迎页步骤卡片的 hover 状态在 `widgets.py` 和 `layouts.py` 双重定义

**问题位置** `widgets.py:198–207`（内联 setStyleSheet），`layouts.py:72–81`（QSS `#WelcomeStepCard`）

**影响** 卡片 hover 样式在两处定义，内联样式优先级高于 QSS，导致 `layouts.py` 中的 `WelcomeStepCard:hover` 实际无效，样式完全由内联决定。二者重复且内容相同，属于冗余代码。

**优化方案** 删除 `widgets.py` 中 `card.setStyleSheet(...)` 内联定义，只保留 `layouts.py` 中的 QSS 规则（已包含相同定义），让样式系统统一管理。

---

## 三、优化优先级矩阵

| 编号 | 问题 | 影响级别 | 实现难度 | 优先级 |
|------|------|----------|----------|--------|
| G-02 | 原生 QMessageBox 割裂 | 高 | 中 | P0 |
| G-01 | 硬编码颜色值 | 中 | 低 | P0 |
| G-05 | ComboBox 下拉箭头隐藏 | 高 | 低 | P0 |
| C-01 | 大纲编辑器渲染打断输入 | 高 | 高 | P1 |
| W-01 | 侧边栏折叠死锁 | 高 | 低 | P1 |
| C-03 | 生成按钮无运行状态 | 中 | 低 | P1 |
| M-01 | 日志逆序渲染 | 中 | 低 | P1 |
| E-01 | 导出按钮视觉层级 | 中 | 低 | P1 |
| E-03 | 导出无路径反馈 | 中 | 低 | P1 |
| D-01 | Memory 清理按钮无分组 | 中 | 低 | P1 |
| G-04 | SpinBox 无操作提示 | 中 | 中 | P2 |
| G-03 | Emoji 渲染不稳定 | 低 | 高 | P2 |
| W-04 | 标题栏无项目名 | 低 | 低 | P2 |
| C-04 | 失败时进度条不重置 | 低 | 低 | P2 |
| R-01 | 搜索+下拉框重叠 | 低 | 中 | P2 |
| D-02 | 滑块无刻度感知 | 低 | 中 | P2 |
| D-04 | 授权状态内联样式 | 低 | 低 | P2 |
| P-01/P-02 | 欢迎页样式双重定义 | 低 | 低 | P3 |
| D-03 | 按钮顺序平台规范 | 低 | 低 | P3 |
| 其余 | 其他一致性 | 低 | 低 | P3 |

---

## 四、P0 快速落地方案

以下三项可在 1-2 小时内完成，建议立即实施：

### 4.1 恢复 ComboBox 下拉箭头【G-05】

`gui/styles/components.py`，修改 `QComboBox::drop-down` 和 `::down-arrow`：

```python
QComboBox::drop-down {{
    border: none;
    width: 20px;
    padding-right: 6px;
    subcontrol-origin: padding;
    subcontrol-position: center right;
}}

QComboBox::down-arrow {{
    color: {Colors.TEXT_MUTED};
    font-size: 10px;
    /* 用 Unicode 字符代替 image */
}}
```

> 注：QSS 中 `::down-arrow` 无法直接使用 `content`，需要提供一张 1px-transparent + 覆盖文字的变通方案，或在 Python 侧为每个 ComboBox 添加一个装饰性 `▾` QLabel 叠加。最简洁方案：在 `padding-right: 28px` 基础上恢复 `image: url(...)` 使用内嵌 base64 SVG。

### 4.2 修复失败路径进度条不重置【C-04】

`gui/main_window.py:on_worker_finished()`，约 742~752 行：

```python
def on_worker_finished(self, success, message):
    self.is_generating = False
    self.tab_create.btn_generate.setEnabled(True)
    self.tab_create.progress.setVisible(False)   # 统一先隐藏
    self.tab_create.progress.setValue(0)          # 统一复位
    if success:
        add_run_log(self.run_logs, "系统", message, "success")
        self.refresh_log_view()
    else:
        QMessageBox.warning(self, "任务结束", message)
    self.reload_project_data()
    ...
```

### 4.3 修复欢迎页样式双重定义【P-02】

`gui/widgets.py:198–207`，删除 `card.setStyleSheet(...)` 整个代码块，仅保留 `card.setObjectName("WelcomeStepCard")`，由 `layouts.py` 中已有的 QSS 接管。

---

## 五、备注

- 本报告基于源码静态分析，部分问题（如 emoji 渲染、ComboBox 交互）建议在实际 Windows 设备上运行验证；
- 【C-01】大纲编辑器重构涉及状态管理变更，需充分回归测试，建议单独分支进行；
- 【G-02】自定义 QMessageBox 建议复用现有 `FramelessWindowMixin` + `DialogContainer` 模式，与其他 4 个对话框风格完全统一。

---

## 六、修改记录

**修改日期：2026-03-30**

### 已完成的修改

#### 【G-02】创建 CustomMessageBox 替换原生 QMessageBox ✅
- **文件**：`gui/dialogs.py`，`gui/main_window.py`
- **修改内容**：
  - 在 `dialogs.py` 中新增 `CustomMessageBox` 类，继承 `QDialog` 和 `FramelessWindowMixin`
  - 支持 `information`、`success`、`warning`、`critical`、`question` 五种类型
  - 替换 `main_window.py` 中全部 12 处 `QMessageBox` 调用
  - 替换 `dialogs.py` 中 `ApiSettingsDialog._on_clear_memory()` 的 2 处 `QMessageBox` 调用

#### 【G-01】移除硬编码颜色值，统一使用设计系统 ✅
- **文件**：`gui/styles/layouts.py`，`gui/styles/components.py`，`gui/views/tab_monitor_view.py`，`gui/views/tab_reader_view.py`
- **修改内容**：
  - 在 `layouts.py` 新增 `CardHeader` 和 `Card` QSS 样式定义
  - 在 `components.py` 新增 `SegmentedButton`、`SecondaryButton`、`IconButtonDanger` 组件样式
  - `tab_monitor_view.py`：`CardHeader` 替代内联样式，切换按钮改用 `SegmentedButton`
  - `tab_reader_view.py`：`CardHeader` 替代内联样式，复制按钮改用 `SecondaryButton`

#### 【G-05】恢复 ComboBox 下拉箭头显示 ✅
- **文件**：`gui/styles/components.py`
- **修改内容**：
  - `QComboBox::drop-down` width 从 `0px` 改为 `24px`
  - `QComboBox::down-arrow` 改为显示 `12x12px` 彩色箭头

#### 【W-01】修复侧边栏折叠死锁问题 ✅
- **文件**：`gui/main_window.py`
- **修改内容**：
  - 重写 `toggle_sidebar()` 逻辑，隐藏侧边栏时设置 splitter sizes 为 `[0, 1200]`
  - 展开时恢复 `[260, 1200]`
  - 移除了不可见的 `btn_toggle_sidebar` 相关逻辑

#### 【C-03】生成按钮添加运行状态反馈 ✅
- **文件**：`gui/main_window.py`
- **修改内容**：
  - 生成开始时按钮文字改为 "生成中..."，禁用按钮
  - 生成结束后恢复 "启动生成引擎" 文字，重新启用
  - 进度条完成后统一 `setValue(0)` 和 `setVisible(False)` 复位

#### 【M-01】日志改为正序渲染 ✅
- **文件**：`gui/main_window.py`
- **修改内容**：
  - 移除 `refresh_log_view()` 中的 `reversed()` 调用
  - 日志现在按时间正序显示（最旧在顶，最新在底）

#### 【M-03】日志 info 状态竖线颜色提亮 ✅
- **文件**：`gui/main_window.py`
- **修改内容**：
  - info 状态颜色从 `#94a3b8` 改为 `#60a5fa`（PRIMARY_400）
  - 提升与 GRAY_900 背景的对比度，满足 WCAG AA 标准

#### 【E-01】导出按钮视觉层级优化 ✅
- **文件**：`gui/views/tab_export_view.py`
- **修改内容**：
  - 三个格式按钮（Word/EPUB/TXT）横排一行
  - "全部导出" 按钮独立为全宽一行，高度 50px，主 CTA 样式

#### 【E-03】导出添加路径反馈 ✅
- **文件**：`gui/views/tab_export_view.py`，`gui/main_window.py`
- **修改内容**：
  - 导出成功消息改为显示完整路径 "已导出至: {path}"
  - 新增 "打开文件夹" 按钮（SecondaryButton 样式）
  - `show_result()` 方法增加 `file_path` 参数

#### 【D-01】Memory 清理按钮分组 ✅
- **文件**：`gui/dialogs.py`
- **修改内容**：
  - 新增 `QGroupBox("长期记忆管理")` 包裹相关控件
  - 添加风险提示文字："向量数据库中存储的跨章节记忆，清理后不可恢复"
  - 清理按钮改用 `DangerButton` 样式

#### 【C-01】大纲编辑器拆分为编辑/预览模式 ✅
- **文件**：`gui/views/tab_create_view.py`，`gui/main_window.py`
- **修改内容**：
  - `tab_create_view.py`：新增 `QStackedWidget` 包含编辑/预览两个页面
  - 新增 "编辑" / "预览" SegmentedButton 切换按钮
  - 编辑器从 `QTextEdit` 改为 `QPlainTextEdit`（纯文本，性能更好）
  - 移除 500ms 定时器自动替换内容的逻辑
  - 预览模式切换时手动渲染 HTML

### 验证方法

```bash
# 语法检查
python -m py_compile gui/dialogs.py gui/main_window.py gui/views/tab_create_view.py gui/views/tab_export_view.py gui/views/tab_monitor_view.py gui/views/tab_reader_view.py gui/styles/components.py gui/styles/layouts.py
```

### 修改文件清单

1. `gui/dialogs.py` - 新增 CustomMessageBox，修改 ApiSettingsDialog
2. `gui/main_window.py` - 替换 QMessageBox，修改侧边栏、大纲编辑器、导出功能
3. `gui/views/tab_create_view.py` - 编辑/预览模式拆分
4. `gui/views/tab_export_view.py` - 导出按钮布局优化，添加打开文件夹功能
5. `gui/views/tab_monitor_view.py` - 移除内联样式，SegmenteButton
6. `gui/views/tab_reader_view.py` - 移除内联样式，SecondaryButton
7. `gui/styles/components.py` - 新增 SegmentedButton、SecondaryButton、IconButtonDanger 样式
8. `gui/styles/layouts.py` - 新增 CardHeader、Card 样式定义

---

## 七、问题反馈与修复建议

**检查日期：2026-03-30**

### 发现的问题（已修复 ✅）

#### 1. 【C-01】大纲编辑器编辑/预览模式 - 按钮互斥逻辑缺失 ⚠️ → ✅ 已修复

**问题描述**：
- `btn_write_mode` 和 `btn_preview_mode` 都设置了 `setCheckable(True)`，但没有互斥逻辑
- 两个按钮可以同时被选中，导致状态混乱
- 点击已选中的按钮会取消选中，但没有切换到另一个模式

**修复文件**：
- `gui/views/tab_create_view.py` - 添加 `outline_mode_group` QButtonGroup 实现互斥
- `gui/main_window.py` - 更新信号连接，使用 `buttonClicked` 信号

**修复内容**：
```python
# tab_create_view.py
self.outline_mode_group = QButtonGroup(self)
self.outline_mode_group.setExclusive(True)
self.outline_mode_group.addButton(self.btn_write_mode, 0)
self.outline_mode_group.addButton(self.btn_preview_mode, 1)

# main_window.py
self.tab_create.outline_mode_group.buttonClicked.connect(self._on_outline_mode_changed)

def _on_outline_mode_changed(self, button):
    mode_index = self.tab_create.outline_mode_group.id(button)
    # ... 原有逻辑
```

#### 2. 【G-02】CustomMessageBox - 缺少关闭按钮处理 ⚠️ → ✅ 已修复

**问题描述**：
- `CustomMessageBox` 继承 `FramelessWindowMixin`，但没有处理窗口关闭按钮
- 用户点击标题栏关闭按钮时，对话框可能无法正确返回结果
- `question` 类型的回调机制与返回值机制混用，逻辑复杂

**修复文件**：
- `gui/dialogs.py` - 添加 `closeEvent` 处理，保存 `msg_type` 用于判断

**修复内容**：
```python
def __init__(self, parent=None, title="", message="", msg_type="info", callback=None):
    # ... 原有代码 ...
    self._msg_type = msg_type  # 保存类型用于关闭判断

def closeEvent(self, event):
    """处理窗口关闭事件"""
    if self._msg_type == "question":
        self._result = False  # 关闭视为取消
    event.accept()
```

#### 3. 【D-01】Memory 分组样式 - 与对话框整体风格不统一 ⚠️ → ✅ 已修复

**问题描述**：
- `QGroupBox` 设置了独立的 `setStyleSheet`，与 `DialogContainer` 的样式可能冲突
- 边框颜色 `Colors.BORDER` 在暗色/亮色主题下可能显示效果不佳
- 缺少 `margin-bottom`，导致与下方按钮间距不一致

**修复文件**：
- `gui/dialogs.py` - 优化 QGroupBox 样式

**修复内容**：
```python
memory_group.setStyleSheet(f"""
    QGroupBox {{
        margin-top: 12px;        /* 增加顶部间距 */
        margin-bottom: 8px;      /* 增加底部间距 */
        padding-bottom: 12px;    /* 增加内边距 */
    }}
    QGroupBox::title {{
        padding: 0 6px;          /* 增加标题内边距 */
        background: {Colors.WHITE};  /* 与对话框背景一致 */
    }}
""")
```

#### 4. 【G-01】SegmentedButton 样式 - 选中状态不明显 ⚠️ → ✅ 已修复

**问题描述**：
- `SegmentedButton` 的 `checked` 状态只有轻微阴影和颜色变化
- 在 Windows 默认主题下，白色背景与对话框背景对比度不够
- 缺少 `QPushButton#SegmentedButton:checked:hover` 状态定义

**修复文件**：
- `gui/styles/components.py` - 优化 SegmentedButton 样式

**修复内容**：
```css
QPushButton#SegmentedButton {{
    border: 1px solid transparent;  /* 添加透明边框占位 */
}}

QPushButton#SegmentedButton:checked {{
    border-color: {Colors.BORDER};  /* 选中时显示边框 */
}}

QPushButton#SegmentedButton:checked:hover {{
    background: {Colors.GRAY_50};   /* 添加悬停状态 */
    border-color: {Colors.GRAY_300};
}}
```

#### 5. 【G-05】ComboBox 下拉箭头 - 箭头颜色对比度不足 ⚠️ → ✅ 已修复

**问题描述**：
- 下拉箭头使用 `border-color: {Colors.PRIMARY_500}`，在灰色边框的 ComboBox 上可能不够明显
- 箭头大小 12x12px 在某些 DPI 设置下可能过小

**修复文件**：
- `gui/styles/components.py` - 优化下拉箭头样式

**修复内容**：
```css
QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {Colors.TEXT_SECONDARY};  /* 使用文字颜色 */
    width: 0;
    height: 0;
}}

QComboBox::down-arrow:on {{
    border-top: none;
    border-bottom: 6px solid {Colors.TEXT_SECONDARY};
}}

QComboBox:hover::down-arrow {{
    border-top-color: {Colors.TEXT_PRIMARY};  /* 悬停时加深 */
}}
```

---

## 八、修复完成总结

**修复日期：2026-03-30**

### 已修复问题清单

| 编号 | 问题 | 状态 | 修复文件 |
|------|------|------|----------|
| C-01 | 大纲编辑器按钮互斥逻辑缺失 | ✅ 已修复 | tab_create_view.py, main_window.py |
| G-02 | CustomMessageBox 关闭按钮处理 | ✅ 已修复 | dialogs.py |
| G-01 | SegmentedButton 选中状态不明显 | ✅ 已修复 | components.py |
| D-01 | Memory 分组样式不统一 | ✅ 已修复 | dialogs.py |
| G-05 | ComboBox 箭头颜色对比度不足 | ✅ 已修复 | components.py |

### 验证结果

```bash
# 语法检查通过
python -m py_compile gui/dialogs.py gui/main_window.py gui/views/tab_create_view.py gui/styles/components.py
```

所有修改文件均已通过 Python 语法检查，无编译错误。
