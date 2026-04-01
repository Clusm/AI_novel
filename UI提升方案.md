# AI_Novel_Writer UI 提升方案

## 概述
本文档详细列出 AI_Novel_Writer v3.0 的 UI/UX 优化建议，基于提供的三张界面截图进行专业级分析。

---

## 一、整体布局架构优化

### 1.1 布局结构调整

#### 当前问题
- 左侧边栏宽度过窄，内容拥挤
- 主内容区与右侧控制面板比例不协调
- 顶部统计区域占用过多垂直空间

#### 优化建议
```
建议布局比例：
┌─────────────────────────────────────────────────────────┐
│  顶部导航栏 (固定高度 60px)                              │
├──────────┬──────────────────────────────┬───────────────┤
│          │                              │               │
│  侧边栏   │      主内容区域               │   右侧面板     │
│  240px   │      自适应剩余宽度            │   320px       │
│  固定    │                              │   固定         │
│          │                              │               │
└──────────┴──────────────────────────────┴───────────────┘
```

**具体实现：**
- 左侧边栏从当前约180px扩展至240px
- 增加内边距：padding: 16px 20px
- 右侧面板固定320px，避免过宽挤压内容区
- 主内容区最小宽度设置为600px，确保阅读体验

### 1.2 响应式断点设计

| 断点 | 宽度范围 | 布局调整 |
|------|----------|----------|
| Desktop XL | ≥1440px | 三栏布局，完整显示 |
| Desktop | 1200px-1439px | 三栏布局，右侧面板280px |
| Tablet | 768px-1199px | 双栏布局，右侧面板收起为抽屉 |
| Mobile | <768px | 单栏布局，侧边栏变为汉堡菜单 |

---

## 二、色彩系统重构

### 2.1 主色调定义

#### 品牌色
```css
:root {
  /* 主品牌色 - 科技蓝 */
  --brand-primary: #2563EB;
  --brand-primary-light: #3B82F6;
  --brand-primary-dark: #1D4ED8;
  --brand-primary-50: #EFF6FF;
  --brand-primary-100: #DBEAFE;
  
  /* 辅助色 */
  --accent-success: #10B981;    /* 成功/完成 */
  --accent-warning: #F59E0B;    /* 警告/注意 */
  --accent-error: #EF4444;      /* 错误/删除 */
  --accent-info: #06B6D4;       /* 信息/提示 */
  
  /* 中性色 */
  --neutral-900: #111827;       /* 主标题 */
  --neutral-700: #374151;       /* 正文 */
  --neutral-500: #6B7280;       /* 次要文字 */
  --neutral-300: #D1D5DB;       /* 边框 */
  --neutral-100: #F3F4F6;       /* 背景 */
  --neutral-50: #F9FAFB;        /* 卡片背景 */
  
  /* 背景色 */
  --bg-primary: #FFFFFF;
  --bg-secondary: #F8FAFC;
  --bg-tertiary: #F1F5F9;
}
```

### 2.2 统计卡片色彩方案

#### 当前问题
四个统计卡片使用相同的白色背景，缺乏视觉区分。

#### 优化方案
为每个统计指标配置专属色彩：

| 指标 | 背景色 | 数字颜色 | 图标 | 含义 |
|------|--------|----------|------|------|
| 已生成章节 | #EFF6FF | #2563EB | 📚 | 蓝色-知识/内容 |
| 总字数 | #ECFDF5 | #059669 | ✍️ | 绿色-创作/成果 |
| 平均字数/章 | #FFFBEB | #D97706 | 📊 | 黄色-数据/统计 |
| 预计总章数 | #F5F3FF | #7C3AED | 🎯 | 紫色-目标/计划 |

**卡片样式细节：**
```css
.stat-card {
  background: linear-gradient(135deg, var(--card-bg) 0%, #FFFFFF 100%);
  border: 1px solid rgba(0,0,0,0.04);
  border-radius: 12px;
  padding: 20px 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: var(--neutral-500);
  font-weight: 500;
}
```

---

## 三、组件级详细优化

### 3.1 顶部导航栏

#### 当前问题
- 标题与版本号挤在一起
- 缺少品牌识别元素
- 右侧窗口控制按钮过于突兀

#### 优化方案

**布局结构：**
```
┌────────────────────────────────────────────────────────────┐
│ [Logo] AI_Novel_Writer                              _ □ X │
│        v3.0                                                │
└────────────────────────────────────────────────────────────┘
```

**样式规范：**
```css
.top-nav {
  height: 60px;
  background: #FFFFFF;
  border-bottom: 1px solid var(--neutral-200);
  display: flex;
  align-items: center;
  padding: 0 24px;
  -webkit-app-region: drag; /* 允许拖拽移动窗口 */
}

.brand-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-logo {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.brand-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--neutral-900);
}

.brand-version {
  font-size: 11px;
  color: var(--neutral-400);
  font-weight: 500;
}

.window-controls {
  -webkit-app-region: no-drag;
  display: flex;
  gap: 8px;
}

.window-btn {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--neutral-500);
  transition: all 0.2s;
}

.window-btn:hover {
  background: var(--neutral-100);
  color: var(--neutral-700);
}

.window-btn.close:hover {
  background: #FEE2E2;
  color: #DC2626;
}
```

### 3.2 标签页导航（Tab Navigation）

#### 当前问题
- 标签页样式普通，选中状态不明显
- 缺少图标辅助识别
- 切换无动画效果

#### 优化方案

**设计规范：**
```css
.tab-nav {
  display: flex;
  gap: 4px;
  padding: 4px;
  background: var(--neutral-100);
  border-radius: 10px;
  margin-bottom: 24px;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--neutral-600);
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.tab-item:hover {
  color: var(--neutral-900);
  background: rgba(255,255,255,0.5);
}

.tab-item.active {
  color: var(--brand-primary);
  background: #FFFFFF;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 3px;
  background: var(--brand-primary);
  border-radius: 2px;
}

.tab-icon {
  font-size: 16px;
}
```

**标签页配置：**
| 标签 | 图标 | 颜色标识 |
|------|------|----------|
| 创作中心 | ✨ | 蓝色 |
| 阅读管理 | 📖 | 绿色 |
| 运行监控 | 🖥️ | 紫色 |
| 导出发布 | 📤 | 橙色 |

### 3.3 左侧边栏

#### 当前问题
- 项目选择器样式简陋
- "删除"按钮红色过于刺眼
- 系统设置区域视觉权重低

#### 优化方案

**3.3.1 项目选择器**
```css
.project-selector {
  background: #FFFFFF;
  border: 1px solid var(--neutral-200);
  border-radius: 10px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  transition: all 0.2s;
}

.project-selector:hover {
  border-color: var(--brand-primary-light);
  box-shadow: 0 0 0 3px var(--brand-primary-50);
}

.project-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.project-label {
  font-size: 11px;
  color: var(--neutral-400);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.project-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--neutral-800);
}

.project-arrow {
  color: var(--neutral-400);
  transition: transform 0.2s;
}

.project-selector.open .project-arrow {
  transform: rotate(180deg);
}
```

**3.3.2 操作按钮组**
```css
.action-buttons {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.btn {
  flex: 1;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--brand-primary);
  color: white;
  border: none;
}

.btn-primary:hover {
  background: var(--brand-primary-dark);
}

.btn-danger {
  background: transparent;
  color: var(--accent-error);
  border: 1px solid #FECACA;
}

.btn-danger:hover {
  background: #FEF2F2;
  border-color: var(--accent-error);
}
```

**3.3.3 系统设置分组**
```css
.settings-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--neutral-200);
}

.settings-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--neutral-400);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
  padding-left: 4px;
}

.settings-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.settings-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 13px;
  color: var(--neutral-600);
  cursor: pointer;
  transition: all 0.2s;
}

.settings-item:hover {
  background: var(--neutral-100);
  color: var(--neutral-900);
}

.settings-item-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}
```

### 3.4 大纲展示区域

#### 当前问题
- 大纲内容纯文本展示，缺乏结构层次
- 标题与内容间距不均匀
- 缺少视觉引导元素

#### 优化方案

**3.4.1 大纲头部**
```css
.outline-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.outline-title-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.outline-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.outline-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--neutral-800);
}

.outline-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #ECFDF5;
  border-radius: 20px;
  font-size: 12px;
  color: #059669;
  font-weight: 500;
}

.outline-badge-icon {
  width: 16px;
  height: 16px;
  background: #059669;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 10px;
}
```

**3.4.2 大纲内容卡片**
```css
.outline-content {
  background: #FFFFFF;
  border: 1px solid var(--neutral-200);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.outline-main-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--brand-primary);
  margin-bottom: 8px;
  line-height: 1.3;
}

.outline-subtitle {
  font-size: 14px;
  color: var(--neutral-500);
  margin-bottom: 24px;
}

.outline-section {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--neutral-100);
}

.outline-section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.section-number {
  width: 28px;
  height: 28px;
  background: var(--brand-primary);
  color: white;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--neutral-800);
}

.section-content {
  padding-left: 36px;
}

.content-item {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  font-size: 14px;
  line-height: 1.6;
}

.content-label {
  color: var(--neutral-500);
  font-weight: 500;
  min-width: 80px;
  flex-shrink: 0;
}

.content-value {
  color: var(--neutral-700);
  flex: 1;
}

.content-value em {
  color: var(--brand-primary);
  font-style: normal;
  font-weight: 500;
}
```

**3.4.3 保存按钮**
```css
.save-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 12px 24px;
  background: linear-gradient(135deg, var(--brand-primary) 0%, var(--brand-primary-dark) 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 20px;
}

.save-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.save-btn:active {
  transform: translateY(0);
}
```

### 3.5 生成控制面板

#### 当前问题
- 面板边界不清晰
- 表单控件样式不统一
- "停止生成"按钮样式不明确

#### 优化方案

**3.5.1 面板整体样式**
```css
.control-panel {
  background: #FFFFFF;
  border: 1px solid var(--neutral-200);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.control-panel-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--neutral-100);
}

.control-panel-icon {
  font-size: 18px;
}

.control-panel-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--neutral-800);
}
```

**3.5.2 表单控件**
```css
.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--neutral-600);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.form-select {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--neutral-300);
  border-radius: 8px;
  font-size: 14px;
  color: var(--neutral-800);
  background: #FFFFFF;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,..."); /* 自定义下拉箭头 */
  background-repeat: no-repeat;
  background-position: right 12px center;
  transition: all 0.2s;
}

.form-select:hover {
  border-color: var(--neutral-400);
}

.form-select:focus {
  outline: none;
  border-color: var(--brand-primary);
  box-shadow: 0 0 0 3px var(--brand-primary-50);
}

.form-textarea {
  width: 100%;
  min-height: 120px;
  padding: 12px;
  border: 1px solid var(--neutral-300);
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.5;
  color: var(--neutral-800);
  resize: vertical;
  transition: all 0.2s;
}

.form-textarea::placeholder {
  color: var(--neutral-400);
}

.form-textarea:focus {
  outline: none;
  border-color: var(--brand-primary);
  box-shadow: 0 0 0 3px var(--brand-primary-50);
}
```

**3.5.3 操作按钮组**
```css
.control-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 20px;
}

.btn-generate {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-generate:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-stop {
  width: 100%;
  padding: 12px;
  background: transparent;
  color: var(--accent-error);
  border: 1.5px solid #FECACA;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-stop:hover {
  background: #FEF2F2;
  border-color: var(--accent-error);
}
```

**3.5.4 状态提示**
```css
.status-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: var(--neutral-50);
  border-radius: 8px;
  margin-top: 16px;
}

.status-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--neutral-300);
  border-top-color: var(--brand-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.status-text {
  font-size: 13px;
  color: var(--neutral-500);
}
```

---

## 四、阅读管理页面优化

### 4.1 目录侧边栏

#### 当前问题
- 章节列表样式简陋
- 缺少当前章节指示
- 导航按钮过小

#### 优化方案

**4.1.1 搜索框**
```css
.chapter-search {
  position: relative;
  margin-bottom: 16px;
}

.chapter-search-input {
  width: 100%;
  padding: 10px 12px 10px 36px;
  border: 1px solid var(--neutral-300);
  border-radius: 8px;
  font-size: 13px;
  transition: all 0.2s;
}

.chapter-search-input:focus {
  outline: none;
  border-color: var(--brand-primary);
  box-shadow: 0 0 0 3px var(--brand-primary-50);
}

.chapter-search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--neutral-400);
}
```

**4.1.2 章节列表**
```css
.chapter-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.chapter-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 13px;
  color: var(--neutral-600);
  cursor: pointer;
  transition: all 0.2s;
}

.chapter-item:hover {
  background: var(--neutral-100);
  color: var(--neutral-800);
}

.chapter-item.active {
  background: var(--brand-primary-50);
  color: var(--brand-primary);
  font-weight: 500;
}

.chapter-item.active::before {
  content: '';
  width: 3px;
  height: 16px;
  background: var(--brand-primary);
  border-radius: 2px;
}

.chapter-status {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--neutral-300);
}

.chapter-status.completed {
  background: var(--accent-success);
}

.chapter-status.in-progress {
  background: var(--accent-warning);
}
```

**4.1.3 导航按钮**
```css
.chapter-nav {
  display: flex;
  gap: 8px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--neutral-200);
}

.nav-btn {
  flex: 1;
  padding: 10px;
  background: #FFFFFF;
  border: 1px solid var(--neutral-300);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  color: var(--neutral-600);
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.nav-btn:hover:not(:disabled) {
  border-color: var(--brand-primary);
  color: var(--brand-primary);
}

.nav-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

### 4.2 正文阅读区

#### 当前问题
- 标题与字数信息布局松散
- 缺少阅读辅助功能
- 复制按钮位置不显眼

#### 优化方案

**4.2.1 文章头部**
```css
.article-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--neutral-200);
  margin-bottom: 24px;
}

.article-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--neutral-900);
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.word-count {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--neutral-100);
  border-radius: 20px;
  font-size: 12px;
  color: var(--neutral-600);
}

.btn-copy {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: #FFFFFF;
  border: 1px solid var(--neutral-300);
  border-radius: 8px;
  font-size: 13px;
  color: var(--neutral-600);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-copy:hover {
  border-color: var(--brand-primary);
  color: var(--brand-primary);
}

.btn-copy.copied {
  background: #ECFDF5;
  border-color: #10B981;
  color: #059669;
}
```

**4.2.2 阅读工具栏**
```css
.reading-toolbar {
  position: fixed;
  right: 24px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: #FFFFFF;
  border: 1px solid var(--neutral-200);
  border-radius: 12px;
  padding: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.toolbar-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  border-radius: 8px;
  font-size: 16px;
  color: var(--neutral-500);
  cursor: pointer;
  transition: all 0.2s;
}

.toolbar-btn:hover {
  background: var(--neutral-100);
  color: var(--neutral-800);
}

.toolbar-btn.active {
  background: var(--brand-primary-50);
  color: var(--brand-primary);
}
```

**4.2.3 正文样式**
```css
.article-content {
  font-size: 16px;
  line-height: 1.8;
  color: var(--neutral-800);
}

.article-content h1 {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 24px;
  color: var(--neutral-900);
}

.article-content p {
  margin-bottom: 16px;
  text-indent: 2em;
}

.article-content p:first-of-type {
  text-indent: 0;
}

.article-content p:first-of-type::first-letter {
  font-size: 3em;
  float: left;
  line-height: 1;
  margin-right: 8px;
  color: var(--brand-primary);
  font-weight: 700;
}

/* 阅读进度条 */
.reading-progress {
  position: fixed;
  top: 60px;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--neutral-200);
  z-index: 100;
}

.reading-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--brand-primary) 0%, var(--brand-primary-light) 100%);
  transition: width 0.1s;
}
```

---

## 五、运行监控页面优化

### 5.1 终端界面

#### 当前问题
- 黑底绿字对比度低
- 缺少代码高亮
- 输出区域分隔不明确

#### 优化方案

**5.1.1 终端容器**
```css
.terminal-container {
  background: #1E1E1E;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

.terminal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #2D2D2D;
  border-bottom: 1px solid #3D3D3D;
}

.terminal-tabs {
  display: flex;
  gap: 4px;
}

.terminal-tab {
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 13px;
  color: #9CA3AF;
  cursor: pointer;
  transition: all 0.2s;
}

.terminal-tab:hover {
  color: #E5E7EB;
  background: rgba(255,255,255,0.05);
}

.terminal-tab.active {
  color: #FFFFFF;
  background: rgba(255,255,255,0.1);
}

.terminal-actions {
  display: flex;
  gap: 8px;
}

.terminal-action-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  border-radius: 6px;
  color: #9CA3AF;
  cursor: pointer;
  transition: all 0.2s;
}

.terminal-action-btn:hover {
  background: rgba(255,255,255,0.1);
  color: #E5E7EB;
}
```

**5.1.2 终端内容区**
```css
.terminal-body {
  padding: 16px;
  font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
  max-height: 500px;
  overflow-y: auto;
}

.terminal-line {
  margin-bottom: 4px;
  white-space: pre-wrap;
  word-break: break-all;
}

/* 语法高亮 */
.terminal-line.info {
  color: #60A5FA;
}

.terminal-line.success {
  color: #34D399;
}

.terminal-line.warning {
  color: #FBBF24;
}

.terminal-line.error {
  color: #F87171;
}

.terminal-line.command {
  color: #A78BFA;
}

.terminal-line.output {
  color: #E5E7EB;
}

/* 行号 */
.terminal-line-number {
  display: inline-block;
  width: 40px;
  color: #4B5563;
  text-align: right;
  margin-right: 16px;
  user-select: none;
}
```

**5.1.3 输出区域**
```css
.output-section {
  margin-top: 16px;
  border: 1px solid #3D3D3D;
  border-radius: 8px;
  overflow: hidden;
}

.output-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: #2D2D2D;
  border-bottom: 1px solid #3D3D3D;
  font-size: 12px;
  color: #9CA3AF;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.output-content {
  padding: 14px;
  background: #252525;
  color: #E5E7EB;
  font-size: 13px;
  line-height: 1.5;
}

.output-content.warning {
  background: rgba(251, 191, 36, 0.1);
  border-left: 3px solid #FBBF24;
}

.timestamp {
  color: #6B7280;
  font-size: 11px;
  margin-right: 8px;
}
```

---

## 六、动画与交互细节

### 6.1 微交互设计

| 元素 | 触发条件 | 动画效果 | 时长 |
|------|----------|----------|------|
| 按钮 | Hover | 上移1px + 阴影加深 | 200ms |
| 按钮 | Click | 缩放0.98 | 100ms |
| 卡片 | Hover | 上移2px + 阴影扩散 | 300ms |
| 标签页 | 切换 | 指示条滑动 | 250ms |
| 下拉菜单 | 展开 | 淡入 + 下移 | 200ms |
| 模态框 | 打开 | 缩放0.95→1 + 淡入 | 300ms |
| Toast | 出现 | 从右侧滑入 | 300ms |
| 加载 | 持续 | 旋转 + 脉冲 | 800ms |

### 6.2 过渡动画CSS

```css
/* 通用过渡 */
.transition-all {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 按钮点击效果 */
.btn:active {
  transform: scale(0.98);
}

/* 卡片悬浮 */
.card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

/* 标签页指示器 */
.tab-indicator {
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 页面切换 */
.page-enter {
  opacity: 0;
  transform: translateY(10px);
}

.page-enter-active {
  opacity: 1;
  transform: translateY(0);
  transition: all 0.3s ease;
}

/* 骨架屏 */
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.skeleton {
  background: linear-gradient(90deg, #F3F4F6 25%, #E5E7EB 50%, #F3F4F6 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
```

---

## 七、字体与排版规范

### 7.1 字体栈

```css
:root {
  /* 中文 */
  --font-chinese: -apple-system, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  
  /* 英文/数字 */
  --font-english: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
  
  /* 代码 */
  --font-mono: "JetBrains Mono", "Fira Code", "Consolas", monospace;
  
  /* 标题 */
  --font-heading: var(--font-chinese);
  
  /* 正文 */
  --font-body: var(--font-chinese);
}
```

### 7.2 字体层级

| 层级 | 用途 | 字号 | 字重 | 行高 |
|------|------|------|------|------|
| H1 | 页面主标题 | 28px | 700 | 1.3 |
| H2 | 区块标题 | 20px | 600 | 1.4 |
| H3 | 小标题 | 16px | 600 | 1.4 |
| Body | 正文 | 14px | 400 | 1.6 |
| Small | 辅助文字 | 12px | 400 | 1.5 |
| Caption | 标签/说明 | 11px | 500 | 1.4 |

---

## 八、图标系统

### 8.1 图标规范

- **图标库**: Lucide 或 Phosphor Icons
- **基础尺寸**: 16px, 20px, 24px
- **描边宽度**: 1.5px - 2px
- **圆角**: 2px

### 8.2 图标映射表

| 功能 | 图标 | 尺寸 |
|------|------|------|
| 新建 | Plus | 16px |
| 删除 | Trash2 | 16px |
| 编辑 | Pencil | 16px |
| 保存 | Save | 16px |
| 复制 | Copy | 16px |
| 设置 | Settings | 20px |
| 搜索 | Search | 16px |
| 章节 | FileText | 16px |
| 生成 | Sparkles | 20px |
| 停止 | Square | 16px |
| 上一章 | ChevronLeft | 16px |
| 下一章 | ChevronRight | 16px |
| 全屏 | Maximize2 | 16px |
| 主题 | Sun/Moon | 16px |
| 字体 | Type | 16px |

---

## 九、实施优先级

### P0 - 立即实施（1周内）
1. 色彩系统重构（统计卡片配色）
2. 按钮样式统一规范
3. 标签页导航优化
4. 表单控件样式统一

### P1 - 短期实施（2-4周）
1. 大纲内容卡片式布局
2. 阅读页面阅读模式设置
3. 终端界面代码高亮
4. 左侧边栏系统设置分组

### P2 - 中期实施（1-2月）
1. 响应式布局适配
2. 动画与微交互完善
3. 加载状态优化
4. 空状态设计

### P3 - 长期规划（3月+）
1. 深色模式支持
2. 自定义主题功能
3. 键盘快捷键支持
4. 无障碍访问优化

---

## 十、参考资源

### 设计系统参考
- [Ant Design](https://ant.design/)
- [Element Plus](https://element-plus.org/)
- [Tailwind UI](https://tailwindui.com/)

### 图标资源
- [Lucide Icons](https://lucide.dev/)
- [Phosphor Icons](https://phosphoricons.com/)

### 字体资源
- [Inter](https://rsms.me/inter/)
- [JetBrains Mono](https://www.jetbrains.com/lp/mono/)

---

*文档版本: v1.0*  
*创建日期: 2026-04-02*  
*适用版本: AI_Novel_Writer v3.0*
