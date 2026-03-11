import os
import time
import re
from datetime import datetime
import streamlit as st

# -----------------------------------------------------------------------------
# 1. 环境配置 (Environment Configuration)
# -----------------------------------------------------------------------------
# 启用 Tracing
os.environ["CREWAI_TRACING_ENABLED"] = "false"
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["OTEL_TRACES_EXPORTER"] = "none"
os.environ["OTEL_METRICS_EXPORTER"] = "none"
os.environ["OTEL_LOGS_EXPORTER"] = "none"
# 设置CrewAI存储目录到项目目录
os.environ["CREWAI_STORAGE_DIR"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".crewai", "data")

from src.project import (
    get_all_projects, create_new_project, delete_project,
    list_generated_chapters, load_chapter, load_outline, save_outline
)
from src.api import save_api_keys, load_api_keys, test_all_apis
from src.logger import add_run_log, clear_run_logs, get_logs_html
from src.generator import generate_single_chapter
from src.export import export_to_txt, export_to_word, export_to_epub, export_all_formats

# -----------------------------------------------------------------------------
# 2. 页面配置 & CSS (Page Config & Styling)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="多Agent写作系统 Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 顶级产品 UI 设计系统
st.markdown("""
<style>
    /* 引入字体 (可选，这里使用系统字体栈优化) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* 全局变量 */
    :root {
        --primary-color: #2563eb;
        --primary-hover: #1d4ed8;
        --bg-color: #f8fafc;
        --card-bg: #ffffff;
        --text-main: #0f172a;
        --text-sub: #64748b;
        --border-color: #e2e8f0;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    /* 全局重置与字体 */
    .stApp {
        background-color: var(--bg-color);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: var(--text-main);
    }
    
    /* 标题优化 */
    h1, h2, h3, h4 {
        font-family: 'Inter', sans-serif;
        color: var(--text-main);
        font-weight: 700;
        letter-spacing: -0.025em;
    }
    
    /* 自定义卡片组件 */
    .pro-card {
        background-color: var(--card-bg);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
        transition: box-shadow 0.2s ease, transform 0.2s ease;
        margin-bottom: 24px;
    }
    .pro-card:hover {
        box-shadow: var(--shadow-md);
    }
    
    /* 统计数据样式 */
    .stat-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 16px;
        background: #f1f5f9;
        border-radius: 12px;
        border: 1px solid transparent;
        transition: all 0.2s;
    }
    .stat-container:hover {
        background: #e2e8f0;
        border-color: #cbd5e1;
    }
    .stat-value {
        font-size: 28px;
        font-weight: 800;
        color: var(--primary-color);
        line-height: 1.2;
    }
    .stat-label {
        font-size: 13px;
        font-weight: 600;
        color: var(--text-sub);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 4px;
    }

    /* 按钮美化 */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        border: 1px solid var(--border-color);
        padding: 0.5rem 1rem;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        border-color: var(--primary-color);
        color: var(--primary-color);
        transform: translateY(-1px);
    }
    .stButton > button[kind="primary"] {
        background-color: var(--primary-color);
        border-color: var(--primary-color);
        color: white;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
    }
    .stButton > button[kind="primary"]:hover {
        background-color: var(--primary-hover);
        box-shadow: 0 6px 8px -1px rgba(37, 99, 235, 0.3);
    }

    /* 输入框与文本域优化 */
    .stTextInput > div > div, .stTextArea > div > div, .stSelectbox > div > div {
        border-radius: 10px;
        border-color: var(--border-color);
        background-color: #ffffff;
    }
    .stTextInput > div > div:focus-within, .stTextArea > div > div:focus-within {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
    }

    /* Tabs 样式优化 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        padding-bottom: 8px;
        border-bottom: 2px solid var(--border-color);
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        border-radius: 8px;
        padding: 0 20px;
        background-color: transparent;
        border: none;
        color: var(--text-sub);
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: white;
        color: var(--primary-color);
        box-shadow: var(--shadow-sm);
    }
    
    /* 侧边栏优化 */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid var(--border-color);
    }
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        justify-content: flex-start;
        text-align: left;
        border: none;
        background: transparent;
        padding: 8px 12px;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #f1f5f9;
        color: var(--text-main);
    }

    /* 状态标签 */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
        line-height: 1;
    }
    .badge-blue { background: #eff6ff; color: #2563eb; }
    .badge-green { background: #f0fdf4; color: #16a34a; }
    .badge-gray { background: #f1f5f9; color: #64748b; }

    /* 滚动条美化 */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. 状态管理 (State Management)
# -----------------------------------------------------------------------------
if "run_logs" not in st.session_state:
    st.session_state.run_logs = []
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False
if "show_new_dialog" not in st.session_state:
    st.session_state.show_new_dialog = False
if "selected_project" not in st.session_state:
    st.session_state.selected_project = None

# -----------------------------------------------------------------------------
# 4. 辅助函数 (Helper Functions)
# -----------------------------------------------------------------------------
def log_callback(message, status="info"):
    """日志回调函数 - 实现实时日志显示"""
    add_run_log(st.session_state.run_logs, "生成过程", message, status)
    if "log_placeholder" in st.session_state:
        try:
            with st.session_state.log_placeholder.container():
                st.markdown(get_logs_html(st.session_state.run_logs), unsafe_allow_html=True)
        except Exception:
            pass
    # 同时在控制台打印，确保即使用户界面卡住也能看到后台进度
    try:
        print(f"[{status.upper()}] {message}")
    except:
        pass

def detect_outline_chapters(outline_text: str):
    """识别大纲中的章节"""
    text = outline_text or ""
    patterns = [r'第\s*\d+\s*章', r'Chapter\s*\d+', r'章节\s*\d+', r'\d+\s*\.', r'\d+\s*-', r'\[\d+\]']
    detected = 0
    for pattern in patterns:
        detected += len(re.findall(pattern, text))
    
    if detected == 0:
        outline_length = len(text)
        if outline_length < 100: estimated = 3
        elif outline_length < 500: estimated = 5
        elif outline_length < 1000: estimated = 8
        else: estimated = 12
        return detected, estimated
    return detected, detected

def calculate_project_stats(project_name, chapters):
    """计算项目统计信息"""
    total_words = 0
    for ch in chapters:
        content = load_chapter(project_name, ch)
        total_words += len(content)
    avg_words = int(total_words / len(chapters)) if chapters else 0
    return total_words, avg_words

def get_required_providers(config):
    providers = ["deepseek", "qwen"]
    route_profile = config.get("ROUTE_PROFILE", "speed")
    writer_model = config.get("WRITER_MODEL", "auto")
    has_kimi = bool((config.get("MOONSHOT_API_KEY", "") or "").strip())
    kimi_required = has_kimi and (
        route_profile in ("balanced", "quality")
        or writer_model == "kimi"
        or (writer_model == "auto" and route_profile == "quality")
    )
    if kimi_required:
        providers.append("kimi")
    return providers

# -----------------------------------------------------------------------------
# 5. 对话框组件 (Dialog Components)
# -----------------------------------------------------------------------------
@st.dialog("⚙️ 系统配置")
def api_settings_dialog():
    keys = load_api_keys()
    st.markdown("#### 🔑 核心配置")
    st.caption("配置 AI 模型密钥与系统授权。")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        deepseek = st.text_input("DeepSeek API Key", value=keys.get("DEEPSEEK_API_KEY", ""), type="password")
        qwen = st.text_input("通义千问 API Key", value=keys.get("DASHSCOPE_API_KEY", ""), type="password")
    with col2:
        kimi = st.text_input("Kimi API Key", value=keys.get("MOONSHOT_API_KEY", ""), type="password")
        auth_code = st.text_input("🛡️ 授权码 (Auth Code)", value=keys.get("AUTH_CODE", ""), type="password", help="请输入系统授权码以解锁高级功能")

    route_profile = st.selectbox(
        "模型链路策略",
        ["speed", "balanced", "quality"],
        index=["speed", "balanced", "quality"].index(keys.get("ROUTE_PROFILE", "speed")) if keys.get("ROUTE_PROFILE", "speed") in ["speed", "balanced", "quality"] else 0,
        help="speed: 全链路优先速度；balanced: 润色用Kimi(若可用)；quality: 主写+润色倾向Kimi(若可用)"
    )
    writer_model = st.selectbox(
        "主写模型",
        ["auto", "qwen", "kimi"],
        index=["auto", "qwen", "kimi"].index(keys.get("WRITER_MODEL", "auto")) if keys.get("WRITER_MODEL", "auto") in ["auto", "qwen", "kimi"] else 0,
        help="auto 按策略自动选择；qwen 稳定更快；kimi 文风潜力更高但通常更慢"
    )
        
    st.markdown("---")
    if st.button("💾 保存配置并验证", type="primary", use_container_width=True):
        save_api_keys(deepseek, qwen, kimi, auth_code, route_profile, writer_model)
        with st.status("正在验证连接...", expanded=True) as status:
            providers = get_required_providers({
                "MOONSHOT_API_KEY": kimi,
                "ROUTE_PROFILE": route_profile,
                "WRITER_MODEL": writer_model,
            })
            api_results = test_all_apis(providers)
            all_ok = True
            for provider, (success, msg) in api_results.items():
                if success:
                    st.write(f"✅ **{provider}**: 连接成功")
                else:
                    st.write(f"❌ **{provider}**: {msg}")
                    all_ok = False
            
            if all_ok:
                status.update(label="✅ 配置已保存且连接正常", state="complete")
                time.sleep(1)
                st.rerun()
            else:
                status.update(label="⚠️ 部分连接失败，配置已保存", state="error")

@st.dialog("✨ 新建项目")
def new_project_dialog():
    st.markdown("#### 创建你的下一部杰作")
    st.caption("输入小说名称，我们将为您初始化全套创作环境。")
    
    name = st.text_input("小说名称", placeholder="例如：诸天之无上道途")
    
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("取消", use_container_width=True):
            st.session_state.show_new_dialog = False
            st.rerun()
    with col2:
        if st.button("🚀 立即创建", type="primary", use_container_width=True):
            if name:
                try:
                    new_name = create_new_project(name)
                    st.session_state.selected_project = new_name
                    st.session_state.show_new_dialog = False
                    st.toast(f"✅ 项目 {new_name} 创建成功！", icon="🎉")
                    time.sleep(0.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"创建失败: {str(e)}")

# -----------------------------------------------------------------------------
# 6. 侧边栏：项目导航 (Sidebar)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 24px;">
        <div style="font-size: 2.5rem;">🤖</div>
        <div>
            <h2 style="margin:0; font-size: 1.2rem;">多Agent写作系统</h2>
            <span style="font-size: 0.8rem; color: #64748b; background: #f1f5f9; padding: 2px 8px; border-radius: 99px;">Pro v2.2</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 项目选择区
    projects = get_all_projects()
    
    st.markdown("### 📚 我的项目")
    if projects:
        # 确保选中项有效
        index = 0
        if st.session_state.selected_project in projects:
            index = projects.index(st.session_state.selected_project)
        elif projects:
            st.session_state.selected_project = projects[0]
            
        selected_project = st.selectbox(
            "切换项目", 
            projects, 
            index=index,
            label_visibility="collapsed"
        )
        
        # 切换逻辑
        if selected_project != st.session_state.selected_project:
            st.session_state.selected_project = selected_project
            st.rerun()
            
        # 快捷操作
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ 新建", use_container_width=True):
                st.session_state.show_new_dialog = True
        with col2:
            if st.button("🗑️ 删除", use_container_width=True):
                if selected_project:
                    delete_project(selected_project)
                    st.session_state.selected_project = None
                    st.rerun()
    else:
        st.info("还没有项目，开始创建一个吧！")
        if st.button("➕ 新建项目", type="primary", use_container_width=True):
            st.session_state.show_new_dialog = True
        selected_project = None

    st.markdown("---")
    with st.expander("⚙️ 系统设置", expanded=False):
        if st.button("🔑 API & 授权", use_container_width=True):
            api_settings_dialog()
        st.caption("版本: Pro v2.2")
    
    st.markdown("---")
    st.caption("Powered by CrewAI Multi-Agent System")

# 处理新建项目弹窗
if st.session_state.get("show_new_dialog", False):
    new_project_dialog()

# -----------------------------------------------------------------------------
# 7. 主界面逻辑 (Main Interface)
# -----------------------------------------------------------------------------
if selected_project:
    # 加载数据
    outline_content = load_outline(selected_project)
    chapters = list_generated_chapters(selected_project)
    detected_chapters, estimated_chapters = detect_outline_chapters(outline_content)
    total_chapters_target = detected_chapters if detected_chapters > 0 else estimated_chapters
    total_words, avg_words = calculate_project_stats(selected_project, chapters)
    
    # 顶部概览卡片
    st.markdown(f"## {selected_project}")
    
    st.markdown('<div class="pro-card">', unsafe_allow_html=True)
    cols = st.columns(4)
    with cols[0]:
        st.markdown(f"""
        <div class="stat-container">
            <div class="stat-value">{len(chapters)}</div>
            <div class="stat-label">已生成章节</div>
        </div>
        """, unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"""
        <div class="stat-container">
            <div class="stat-value">{total_words:,}</div>
            <div class="stat-label">总字数</div>
        </div>
        """, unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f"""
        <div class="stat-container">
            <div class="stat-value">{avg_words:,}</div>
            <div class="stat-label">平均字数/章</div>
        </div>
        """, unsafe_allow_html=True)
    with cols[3]:
        st.markdown(f"""
        <div class="stat-container">
            <div class="stat-value">{total_chapters_target}</div>
            <div class="stat-label">预计总章数</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 功能标签页
    tab1, tab2, tab3, tab4 = st.tabs([
        "✍️ 创作中心", "📖 阅读管理", "📊 运行监控", "📤 导出发布"
    ])

    # -------------------------------------------------------------------------
    # Tab 1: 创作中心 (Outline + Generation)
    # -------------------------------------------------------------------------
    with tab1:
        col_outline, col_control = st.columns([1.8, 1])
        
        with col_outline:
            st.markdown('<div class="pro-card">', unsafe_allow_html=True)
            st.markdown("#### 📝 故事大纲")
            st.caption("AI 将基于此大纲生成内容。建议前 800-1200 字包含核心设定、人物小传及世界观硬约束。")
            
            tab_edit, tab_preview = st.tabs(["✏️ 编辑", "👁️ 预览"])
            with tab_edit:
                new_outline = st.text_area(
                    "大纲内容",
                    value=outline_content,
                    height=600,
                    placeholder="建议格式：\n[核心设定]...\n[人物小传]...\n第1章 标题...\n第2章 标题...",
                    label_visibility="collapsed"
                )
            with tab_preview:
                st.markdown(new_outline if new_outline else "暂无内容")
            
            c1, c2 = st.columns([1, 4])
            with c1:
                if st.button("💾 保存大纲", type="primary", use_container_width=True):
                    save_outline(selected_project, new_outline)
                    st.toast("✅ 大纲已保存", icon="💾")
            with c2:
                if detected_chapters > 0:
                    st.markdown(f"<div style='margin-top: 8px; color: #16a34a;' class='badge badge-green'>✅ 已识别 {detected_chapters} 个章节标题</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='margin-top: 8px; color: #ca8a04;' class='badge badge-gray'>⚠️ 未检测到标准章节标题（建议使用'第N章'格式）</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_control:
            st.markdown('<div class="pro-card">', unsafe_allow_html=True)
            st.markdown("#### 🚀 智能生成")
            st.caption("配置生成参数，启动多 Agent 协作流水线。")
            
            st.markdown("---")
            mode = st.radio(
                "生成模式", 
                ["智能续写", "批量生成"],
                horizontal=True,
                help="智能续写：从最后一章继续；批量生成：指定具体范围"
            )
            
            # 智能计算起始章节
            max_chap = 0
            for f in chapters:
                m = re.search(r"(\d+)", f)
                if m:
                    current_val = int(m.group(1))
                    if current_val > max_chap:
                        max_chap = current_val
            
            start_chapter = max_chap + 1
            count = 1
            
            if mode == "批量生成":
                c1, c2 = st.columns(2)
                with c1:
                    start_chapter = st.number_input("起始章节", value=start_chapter, min_value=1)
                with c2:
                    count = st.number_input("生成数量", value=1, min_value=1, max_value=10)
            else:
                st.info(f"即将生成：第 {start_chapter} 章")
                count = st.number_input("续写数量", value=1, min_value=1, max_value=5)

            st.markdown("---")
            if st.button("🚀 启动生成引擎", type="primary", use_container_width=True, disabled=st.session_state.is_generating):
                if not outline_content or len(outline_content) < 50:
                    st.error("请先完善大纲（至少 50 字）")
                else:
                    st.session_state.is_generating = True
                    st.session_state.run_logs = []
                    st.toast("任务已启动，请关注右侧监控面板", icon="🚀")
                    
                    try:
                        # 1. API 检查
                        with st.spinner("正在初始化 AI 模型连接..."):
                            runtime_keys = load_api_keys()
                            api_results = test_all_apis(get_required_providers(runtime_keys))
                            if not all(r[0] for r in api_results.values()):
                                failed = [k for k, v in api_results.items() if not v[0]]
                                st.error(f"API 连接失败: {', '.join(failed)}")
                                st.session_state.is_generating = False
                                st.stop()

                        # 2. 生成循环
                        # 在Tab 1也显示一个实时日志区，方便用户观察
                        log_container = st.empty()
                        
                        progress_text = "准备开始..."
                        my_bar = st.progress(0, text=progress_text)
                        
                        for i in range(count):
                            current_chap = start_chapter + i
                            progress_text = f"正在生成第 {current_chap} 章 ({i+1}/{count})..."
                            my_bar.progress((i) / count, text=progress_text)
                            
                            # 更新Tab 1的临时日志显示
                            with log_container.container():
                                st.info(f"正在全速生成第 {current_chap} 章... (请稍候，Agent思考可能需要几分钟)")
                                st.caption("💡 提示：如果长时间无响应，请查看终端输出或切换到'运行监控'标签页")
                            
                            # 调用核心生成函数
                            generate_single_chapter(
                                selected_project, 
                                outline_content, 
                                current_chap, 
                                log_callback
                            )
                            st.toast(f"✅ 第 {current_chap} 章生成完成！", icon="🎉")
                            # 避免 API 速率限制，稍作停顿
                            if i < count - 1:
                                time.sleep(3)
                        
                        log_container.empty() # 清理临时日志区
                        my_bar.progress(1.0, text="✅ 所有任务已完成！")
                        st.balloons()
                        time.sleep(1.5)
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"生成过程中断: {str(e)}")
                    finally:
                        st.session_state.is_generating = False
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 快捷提示卡片
            st.markdown("""
            <div class="pro-card" style="background-color: #f8fafc; border-style: dashed;">
                <h4 style="font-size: 0.9rem; margin-bottom: 8px;">💡 专家提示</h4>
                <ul style="font-size: 0.85rem; color: #64748b; padding-left: 20px; margin: 0;">
                    <li>大纲越详细，生成的一致性越高</li>
                    <li>生成的章节支持手动修改</li>
                    <li>遇到逻辑问题，请检查大纲中的伏笔表</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Tab 2: 阅读管理 (Reader)
    # -------------------------------------------------------------------------
    with tab2:
        if not chapters:
            st.info("👋 暂无章节内容，请前往「创作中心」开始生成。")
        else:
            col_list, col_reader = st.columns([1, 3])
            
            with col_list:
                st.markdown('<div class="pro-card">', unsafe_allow_html=True)
                st.markdown("#### 📑 章节目录")
                search = st.text_input("🔍 搜索", placeholder="输入章节名...", label_visibility="collapsed")
                
                filtered_chapters = [c for c in chapters if search in c] if search else chapters
                
                # 优化为下拉框 + 翻页按钮，适应大量章节
                if filtered_chapters:
                    # 初始化或校准当前索引
                    if "current_chapter_idx" not in st.session_state:
                        st.session_state.current_chapter_idx = len(filtered_chapters) - 1
                    
                    # 确保索引不越界
                    if st.session_state.current_chapter_idx >= len(filtered_chapters):
                        st.session_state.current_chapter_idx = len(filtered_chapters) - 1
                    if st.session_state.current_chapter_idx < 0:
                        st.session_state.current_chapter_idx = 0

                    # 导航栏布局
                    nav_c1, nav_c2, nav_c3 = st.columns([1, 3, 1])
                    with nav_c1:
                        if st.button("⬅️ 上一章", use_container_width=True, disabled=st.session_state.current_chapter_idx <= 0):
                            st.session_state.current_chapter_idx -= 1
                            st.rerun()
                    with nav_c2:
                        selected_chapter_file = st.selectbox(
                            "选择章节",
                            filtered_chapters,
                            index=st.session_state.current_chapter_idx,
                            label_visibility="collapsed",
                            key="chapter_selector"
                        )
                        # 如果用户通过下拉框直接选择了不同的章节，更新索引
                        if selected_chapter_file != filtered_chapters[st.session_state.current_chapter_idx]:
                            st.session_state.current_chapter_idx = filtered_chapters.index(selected_chapter_file)
                            st.rerun()
                    with nav_c3:
                        if st.button("下一章 ➡️", use_container_width=True, disabled=st.session_state.current_chapter_idx >= len(filtered_chapters) - 1):
                            st.session_state.current_chapter_idx += 1
                            st.rerun()
                else:
                    selected_chapter_file = None
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col_reader:
                if selected_chapter_file:
                    st.markdown('<div class="pro-card">', unsafe_allow_html=True)
                    
                    # 章节头部
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"### {selected_chapter_file.replace('.md', '')}")
                    with c2:
                        content = load_chapter(selected_project, selected_chapter_file)
                        st.markdown(f"<div style='text-align:right; color:#64748b;'>{len(content)} 字</div>", unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # 章节内容 - 使用 text_area 实现只读但可复制的阅读器
                    st.text_area(
                        "章节内容",
                        value=content,
                        height=700,
                        label_visibility="collapsed"
                    )
                    st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Tab 3: 运行监控 (Monitor)
    # -------------------------------------------------------------------------
    with tab3:
        col_logs, col_actions = st.columns([3, 1])
        with col_actions:
            st.markdown('<div class="pro-card">', unsafe_allow_html=True)
            st.markdown("#### 操作")
            if st.button("🔄 刷新日志", use_container_width=True):
                st.rerun()
            if st.button("🗑️ 清空日志", use_container_width=True):
                clear_run_logs(st.session_state.run_logs)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_logs:
            st.markdown('<div class="pro-card">', unsafe_allow_html=True)
            st.markdown("#### 📺 Agent 实时思考流")
            
            # 实时日志容器
            st.session_state.log_placeholder = st.empty()
            with st.session_state.log_placeholder.container():
                st.markdown(get_logs_html(st.session_state.run_logs), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Tab 4: 导出发布 (Export)
    # -------------------------------------------------------------------------
    with tab4:
        st.markdown('<div class="pro-card">', unsafe_allow_html=True)
        st.markdown("#### 📤 导出作品")
        st.caption("将您的作品打包导出，支持多种格式。")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("📄 Word (.docx)", use_container_width=True):
                try:
                    path = export_to_word(selected_project)
                    st.success(f"已导出: {os.path.basename(path)}")
                except Exception as e:
                    st.error(f"失败: {e}")
        with c2:
            if st.button("📚 EPUB 电子书", use_container_width=True):
                try:
                    path = export_to_epub(selected_project)
                    st.success(f"已导出: {os.path.basename(path)}")
                except Exception as e:
                    st.error(f"失败: {e}")
        with c3:
            if st.button("📝 纯文本 (.txt)", use_container_width=True):
                try:
                    path = export_to_txt(selected_project)
                    st.success(f"已导出: {os.path.basename(path)}")
                except Exception as e:
                    st.error(f"失败: {e}")
        with c4:
            if st.button("📦 全部导出", type="primary", use_container_width=True):
                try:
                    paths = export_all_formats(selected_project)
                    st.balloons()
                    st.success("✅ 所有格式导出成功！")
                    st.code(f"保存路径: projects/{selected_project}/reports/")
                except Exception as e:
                    st.error(f"失败: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # 空状态欢迎页
    st.markdown("""
    <div style="text-align: center; padding: 100px 20px;">
        <div style="font-size: 4rem; margin-bottom: 20px;">🤖</div>
        <h1 style="font-size: 2.5rem; margin-bottom: 10px;">欢迎使用多Agent写作系统</h1>
        <p style="font-size: 1.1rem; color: #64748b; margin-bottom: 40px;">
            专业的 AI 辅助创作平台，让灵感即刻成书。
        </p>
        <div style="display: flex; justify-content: center; gap: 20px;">
            <div class="pro-card" style="width: 200px;">
                <h3>Step 1</h3>
                <p>新建项目</p>
            </div>
            <div class="pro-card" style="width: 200px;">
                <h3>Step 2</h3>
                <p>粘贴大纲</p>
            </div>
            <div class="pro-card" style="width: 200px;">
                <h3>Step 3</h3>
                <p>一键生成</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("✨ 立即开始创作", type="primary", use_container_width=True):
            st.session_state.show_new_dialog = True
