import os
import re
from datetime import datetime
from html import escape
import sys

from PySide6.QtCore import QEvent, Qt, QThread, QTimer
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QMainWindow,
    QSizeGrip,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
import markdown

from gui.styles import APP_STYLESHEET
from gui.workers import ChapterGenerationWorker
from gui.widgets import (
    StreamRedirector,
    FramelessWindowMixin,
    detect_outline_chapters,
)
from gui.dialogs import (
    NewProjectDialog,
    ApiSettingsDialog,
    ModelParamsDialog,
    LicenseSettingsDialog,
    CustomMessageBox,
)
from gui.views import (
    SidebarView,
    MainPanelView,
    TabCreateView,
    TabReaderView,
    TabMonitorView,
    TabExportView,
)
from src.api import (
    MODEL_ROLE_LABELS,
    MODEL_ROLES,
    load_api_keys,
    save_api_keys,
    resolve_runtime_role_models,
    get_model_capability_limits,
)
from src.logger import add_run_log, clear_run_logs
from src.project import (
    create_new_project,
    delete_project,
    get_all_projects,
    get_project_info,
    list_generated_chapters,
    load_chapter,
    load_project_config,
    load_outline,
    save_project_config,
    save_outline,
)
from src.workspace import workspace_manager


class MainWindow(QMainWindow, FramelessWindowMixin):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("多Agent写作系统 Pro")
        self.init_frameless("", min_btn=True, max_btn=True, translucent=True)
        self.resize(1280, 800)
        self.setMinimumSize(1120, 720)
        self._center_window()
        self.setStyleSheet(APP_STYLESHEET)
        self._resize_margin = 8
        self._resize_edges = None
        self._resize_start_pos = None
        self._resize_start_geometry = None
        self._is_resizing = False
        
        self.selected_project = None
        self.run_logs = []
        self.is_generating = False
        self.current_chapter_idx = 0
        self.filtered_chapters = []
        self.all_chapters = []
        self.worker_thread = None
        self.worker = None
        self._outline_syncing = False
        self._outline_source = ""
        self._last_loaded_project = None
        
        self._build_ui()
        self._connect_signals()
        self.refresh_projects()

        self.stdout_redirector = StreamRedirector(sys.stdout)
        self.stderr_redirector = StreamRedirector(sys.stderr)
        sys.stdout = self.stdout_redirector
        sys.stderr = self.stderr_redirector
        self.stdout_redirector.text_written.connect(self.append_raw_log)
        self.stderr_redirector.text_written.connect(self.append_raw_log)

    def _parse_ansi_to_html(self, text):
        text = text.replace("\r", "")
        text = escape(text)
        text = text.replace(" ", "&nbsp;")
        text = text.replace("\n", "<br>")
        
        color_map = {
            '30': '#000000', '31': '#cd3131', '32': '#0dbc79', '33': '#e5e510',
            '34': '#2472c8', '35': '#bc3fbc', '36': '#11a8cd', '37': '#e5e5e5',
            '90': '#666666', '91': '#f14c4c', '92': '#23d18b', '93': '#f5f543',
            '94': '#3b8eea', '95': '#d670d6', '96': '#29b8db', '97': '#e5e5e5',
        }
        
        parts = re.split(r'\x1b\[([\d;]*)m', text)
        if len(parts) == 1:
            return text
            
        result = [parts[0]]
        span_open = False
        
        for i in range(1, len(parts), 2):
            codes = parts[i].split(';')
            text_part = parts[i+1]
            
            if '0' in codes or '' in codes:
                if span_open:
                    result.append("</span>")
                    span_open = False
            
            styles = []
            for c in codes:
                if c in color_map:
                    styles.append(f"color: {color_map[c]}")
                elif c == '1':
                    styles.append("font-weight: bold")
                    
            if styles:
                if span_open:
                    result.append("</span>")
                result.append(f"<span style='{'; '.join(styles)}'>")
                span_open = True
                
            result.append(text_part)
            
        if span_open:
            result.append("</span>")
            
        return "".join(result)

    def append_raw_log(self, text):
        if hasattr(self, 'tab_monitor') and self.tab_monitor.raw_logs_view:
            bar = self.tab_monitor.raw_logs_view.verticalScrollBar()
            keep_bottom = bar.value() >= (bar.maximum() - 2)
            
            cursor = self.tab_monitor.raw_logs_view.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.tab_monitor.raw_logs_view.setTextCursor(cursor)
            
            html_text = self._parse_ansi_to_html(text)
            cursor.insertHtml(f"<span style=\"font-family: Consolas, 'Microsoft YaHei Mono', monospace; font-size: 13px; color: #d4d4d4;\">{html_text}</span>")
            
            if keep_bottom:
                bar.setValue(bar.maximum())

    def _center_window(self):
        screen = self.screen().availableGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

    def _build_ui(self):
        root = QFrame()
        root.setObjectName("CentralWidget")
        root.setMouseTracking(True)
        root.installEventFilter(self)
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(6, 6, 6, 6)
        root_layout.setSpacing(0)
        
        self.sidebar = SidebarView()
        self.main_panel = MainPanelView()
        
        self._build_tabs()
        
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        right_layout.addWidget(self.title_bar)
        right_layout.addWidget(self.main_panel)
        
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setObjectName("MainSplitter")
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(right_container)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setSizes([260, 1200])
        self.splitter.setHandleWidth(1)
        
        root_layout.addWidget(self.splitter)
        self._corner_grips = [QSizeGrip(root) for _ in range(4)]

    def _build_tabs(self):
        self.tab_create = TabCreateView()
        self.tab_reader = TabReaderView()
        self.tab_monitor = TabMonitorView()
        self.tab_export = TabExportView()
        
        self.main_panel.add_tab(self.tab_create, "✨ 创作中心")
        self.main_panel.add_tab(self.tab_reader, "📖 阅读管理")
        self.main_panel.add_tab(self.tab_monitor, "🖥️ 运行监控")
        self.main_panel.add_tab(self.tab_export, "📤 导出发布")

        self.tab_create.progress.setVisible(False)

    def _connect_signals(self):
        self.sidebar.btn_toggle_sidebar_left.clicked.connect(self.toggle_sidebar)
        self.sidebar.project_combo.currentIndexChanged.connect(self.on_project_changed)
        self.sidebar.btn_new_project.clicked.connect(self.create_project)
        self.sidebar.btn_delete_project.clicked.connect(self.remove_project)
        self.sidebar.combo_project_style.currentIndexChanged.connect(self.update_project_style_config)
        self.sidebar.btn_api_settings.clicked.connect(self.open_api_settings)
        self.sidebar.btn_license_settings.clicked.connect(self.open_license_settings)
        self.sidebar.btn_model_params.clicked.connect(self.open_model_params_settings)

        self.main_panel.btn_toggle_sidebar.clicked.connect(self.toggle_sidebar)
        self.main_panel.welcome_widget.btn_start.clicked.connect(self.create_project)

        self.tab_create.btn_save_outline.clicked.connect(self.save_outline_clicked)
        self.tab_create.btn_generate.clicked.connect(self.start_generation)
        self.tab_create.btn_stop.clicked.connect(self.stop_generation)
        self.tab_create.combo_mode.currentIndexChanged.connect(self.on_mode_changed)

        self.tab_reader.chapter_search.textChanged.connect(self.refresh_chapter_filter)
        self.tab_reader.chapter_combo.currentIndexChanged.connect(self.on_chapter_selected)
        self.tab_reader.btn_prev.clicked.connect(lambda: self.move_chapter(-1))
        self.tab_reader.btn_next.clicked.connect(lambda: self.move_chapter(1))
        self.tab_reader.btn_copy_chapter.clicked.connect(self.copy_chapter_content)

        self.tab_monitor.monitor_mode_group.buttonClicked.connect(self._on_monitor_mode_changed)
        self.tab_monitor.btn_refresh_logs.clicked.connect(self.refresh_log_view)
        self.tab_monitor.btn_clear_logs.clicked.connect(self.clear_current_logs)

        self.tab_export.btn_export_word.clicked.connect(self.export_word_clicked)
        self.tab_export.btn_export_epub.clicked.connect(self.export_epub_clicked)
        self.tab_export.btn_export_txt.clicked.connect(self.export_txt_clicked)
        self.tab_export.btn_export_all.clicked.connect(self.export_all_clicked)

    def _edge_flags(self, global_pos):
        rect = self.frameGeometry()
        x = global_pos.x() - rect.left()
        y = global_pos.y() - rect.top()
        w = rect.width()
        h = rect.height()
        margin = self._resize_margin
        left = x <= margin
        right = x >= w - margin
        top = y <= margin
        bottom = y >= h - margin
        return left, right, top, bottom

    def _cursor_for_edges(self, edges):
        left, right, top, bottom = edges
        if (left and top) or (right and bottom):
            return Qt.SizeFDiagCursor
        if (right and top) or (left and bottom):
            return Qt.SizeBDiagCursor
        if left or right:
            return Qt.SizeHorCursor
        if top or bottom:
            return Qt.SizeVerCursor
        return Qt.ArrowCursor

    def _apply_resize(self, global_pos):
        if not self._is_resizing or not self._resize_edges:
            return
        left, right, top, bottom = self._resize_edges
        start = self._resize_start_geometry
        dx = global_pos.x() - self._resize_start_pos.x()
        dy = global_pos.y() - self._resize_start_pos.y()
        min_w = self.minimumWidth()
        min_h = self.minimumHeight()

        new_left = start.left()
        new_right = start.right()
        new_top = start.top()
        new_bottom = start.bottom()

        if left:
            new_left = min(start.left() + dx, start.right() - min_w + 1)
        if right:
            new_right = max(start.right() + dx, start.left() + min_w - 1)
        if top:
            new_top = min(start.top() + dy, start.bottom() - min_h + 1)
        if bottom:
            new_bottom = max(start.bottom() + dy, start.top() + min_h - 1)

        self.setGeometry(new_left, new_top, new_right - new_left + 1, new_bottom - new_top + 1)

    def eventFilter(self, watched, event):
        if watched is self.centralWidget():
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                global_pos = event.globalPosition().toPoint()
                edges = self._edge_flags(global_pos)
                if any(edges):
                    self._resize_edges = edges
                    self._resize_start_pos = global_pos
                    self._resize_start_geometry = self.frameGeometry()
                    self._is_resizing = True
                    return True
            if event.type() == QEvent.MouseMove:
                global_pos = event.globalPosition().toPoint()
                if self._is_resizing:
                    self._apply_resize(global_pos)
                    return True
                self.setCursor(self._cursor_for_edges(self._edge_flags(global_pos)))
            if event.type() == QEvent.MouseButtonRelease and self._is_resizing:
                self._is_resizing = False
                self._resize_edges = None
                self._resize_start_pos = None
                self._resize_start_geometry = None
                self.setCursor(Qt.ArrowCursor)
                return True
        return super().eventFilter(watched, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not hasattr(self, "_corner_grips"):
            return
        grip_size = 14
        rect = self.rect()
        self._corner_grips[0].setGeometry(0, 0, grip_size, grip_size)
        self._corner_grips[1].setGeometry(rect.width() - grip_size, 0, grip_size, grip_size)
        self._corner_grips[2].setGeometry(0, rect.height() - grip_size, grip_size, grip_size)
        self._corner_grips[3].setGeometry(rect.width() - grip_size, rect.height() - grip_size, grip_size, grip_size)

    def toggle_sidebar(self):
        is_visible = self.sidebar.isVisible()

        if is_visible:
            self.sidebar.setVisible(False)
            self.splitter.setSizes([0, 1200])
            self.main_panel.btn_toggle_sidebar.setVisible(True)
        else:
            self.sidebar.setVisible(True)
            self.splitter.setSizes([260, 1200])
            self.main_panel.btn_toggle_sidebar.setVisible(False)

    def refresh_projects(self):
        projects = get_all_projects()
        current = self.selected_project
        self.sidebar.project_combo.blockSignals(True)
        self.sidebar.project_combo.clear()
        self.sidebar.project_combo.addItems(projects)
        self.sidebar.project_combo.blockSignals(False)
        if projects:
            if current in projects:
                self.selected_project = current
            else:
                self.selected_project = projects[0]
            self.sidebar.project_combo.setCurrentText(self.selected_project)
        else:
            self.selected_project = None
        self.reload_project_data()

    def on_project_changed(self):
        name = self.sidebar.project_combo.currentText().strip()
        self.selected_project = name if name else None
        self.reload_project_data()

    def reload_project_data(self):
        enabled = bool(self.selected_project)
        
        if not enabled:
            self.main_panel.show_welcome()
            self.sidebar.btn_delete_project.setEnabled(False)
            self._last_loaded_project = None
            return
            
        self.main_panel.show_dashboard()
        self.main_panel.tabs.setEnabled(True)
        self.sidebar.btn_delete_project.setEnabled(True)
        project_changed = self.selected_project != self._last_loaded_project
        
        info = get_project_info(self.selected_project)
        style_val = info.get("writing_style", "standard")
        style_map = {"standard": "正常模式", "tomato": "番茄模式"}
        self.sidebar.combo_project_style.blockSignals(True)
        self.sidebar.combo_project_style.setCurrentText(style_map.get(style_val, "正常模式"))
        self.sidebar.combo_project_style.blockSignals(False)
        chapters = info["generated_chapters"]
        total_planned = info.get("total_planned_chapters", 0)
        
        if total_planned == 0:
             outline = load_outline(self.selected_project)
             detected, estimated = detect_outline_chapters(outline)
             total_planned = detected if detected > 0 else estimated

        total_words = 0
        for chapter in chapters:
            total_words += len(load_chapter(self.selected_project, chapter))
        avg_words = int(total_words / len(chapters)) if chapters else 0
        
        self.main_panel.project_title.setText(self.selected_project)
        self.main_panel.get_stat_card(0).setText(str(len(chapters)))
        self.main_panel.get_stat_card(1).setText(f"{total_words:,}")
        self.main_panel.get_stat_card(2).setText(f"{avg_words:,}")
        self.main_panel.get_stat_card(3).setText(str(total_planned))

        # 更新起始序号默认值为当前最大章节号 + 1
        next_chapter_num = self._get_next_chapter_number(chapters)
        self.tab_create.spin_start.setValue(next_chapter_num)

        if project_changed:
            outline = load_outline(self.selected_project)
            self.tab_create.outline_preview.setHtml(self._render_outline_html(outline))
            self._detect_outline_chapters_from_plaintext(outline)
            self.refresh_chapter_combo()

        self.refresh_chapter_filter()
        self.refresh_log_view()
        self._last_loaded_project = self.selected_project

    def _normalize_outline_markdown(self, text):
        lines = []
        for line in (text or "").splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                lines.append(stripped)
                continue
            if stripped in ("```", "````", "` `", "`  `"):
                continue
            if stripped.startswith("• "):
                lines.append(line.replace("• ", "- ", 1))
                continue
            lines.append(line)
        return "\n".join(lines)

    def _render_outline_html(self, text):
        normalized = self._normalize_outline_markdown(text)
        raw_html = markdown.markdown(
            normalized,
            extensions=["extra", "tables", "fenced_code", "nl2br", "sane_lists"],
            output_format="html5",
        )
        return f"""
        <div style="font-family:'Segoe UI','Microsoft YaHei UI',sans-serif;font-size:15px;color:#334155;line-height:1.6;padding:10px;">
            <style>
                h1 {{ color:#2563eb; font-size:24px; margin-top:20px; margin-bottom:12px; }}
                h2 {{ color:#0ea5e9; font-size:20px; margin-top:18px; margin-bottom:10px; }}
                h3 {{ color:#0284c7; font-size:18px; margin-top:16px; margin-bottom:8px; }}
                h4, h5, h6 {{ color:#334155; font-size:16px; margin-top:14px; margin-bottom:8px; }}
                p {{ margin-bottom:12px; }}
                ul, ol {{ margin-top:8px; margin-bottom:12px; padding-left:24px; }}
                li {{ margin-bottom:6px; }}
                blockquote {{ border-left:4px solid #cbd5e1; padding-left:12px; color:#64748b; margin:12px 0; font-style:italic; }}
                hr {{ border:0; border-top:1px solid #e2e8f0; margin:20px 0; }}
                strong {{ font-weight:700; color:#0f172a; }}
                table {{ width:100%; border-collapse:collapse; margin:14px 0; font-size:14px; }}
                th {{ background:#f8fafc; color:#0f172a; font-weight:700; }}
                th, td {{ border:1px solid #dbe3ef; padding:8px 10px; text-align:left; vertical-align:top; }}
                tr:nth-child(even) td {{ background:#fcfdff; }}
                code {{ background:#f1f5f9; padding:2px 4px; border-radius:4px; }}
                pre {{ background:#0f172a; color:#e2e8f0; padding:12px; border-radius:8px; overflow:auto; }}
            </style>
            {raw_html}
        </div>
        """

    def _detect_outline_chapters_from_plaintext(self, plain_text):
        start_index = 0
        match = re.search(r'#+\s*分卷细纲|#+\s*章节大纲', plain_text)
        if match:
            start_index = match.end()

        chapter_matches = re.findall(
            r'第\s*\d+\s*章',
            plain_text[start_index:],
        )
        detected = len(chapter_matches)

        if detected > 0:
            self.tab_create.chapter_detect_label.setText(f"✅ 已识别 {detected} 个章节标题")
            self.main_panel.get_stat_card(3).setText(str(detected))
        else:
            self.tab_create.chapter_detect_label.setText("⚠️ 未检测到标准章节标题（建议使用第N章）")

    def _get_next_chapter_number(self, chapters):
        """
        根据已生成章节列表计算下一章序号

        参数：
        - chapters: 章节文件名列表，如 ["第1章.md", "第2章.md"]

        返回：下一章序号（整数）
        """
        if not chapters:
            return 1

        max_num = 0
        for chapter_file in chapters:
            match = re.search(r"(\d+)", chapter_file)
            if match:
                num = int(match.group(1))
                max_num = max(max_num, num)

        return max_num + 1

    def _refresh_banner_style(self, label, tone):
        label.setProperty("tone", tone)
        label.style().unpolish(label)
        label.style().polish(label)

    def _show_export_result(self, message, tone, file_path=None):
        self.tab_export.show_result(message, tone, file_path)

    def _get_log_tone(self, text):
        if "[ERROR]" in text or "❌" in text:
            return "danger"
        if "[WARNING]" in text or "⚠️" in text:
            return "warning"
        if "[SUCCESS]" in text or "✅" in text:
            return "success"
        return "info"

    def _get_log_icon(self, tone):
        if tone == "danger":
            return "⛔"
        if tone == "warning":
            return "⚠️"
        if tone == "success":
            return "✅"
        return "ℹ️"

    def _format_log_html(self, text):
        tone = self._get_log_tone(text)
        bg_map = {
            "info": "transparent",
            "success": "rgba(22, 163, 74, 0.1)",
            "warning": "rgba(217, 119, 6, 0.1)",
            "danger": "rgba(220, 38, 38, 0.1)",
        }
        color_map = {
            "info": "#60a5fa",
            "success": "#4ade80",
            "warning": "#fbbf24",
            "danger": "#f87171",
        }
        
        escaped = escape(text)
        time_str = datetime.now().strftime("%H:%M:%S")
        
        if " | " in escaped:
            left, right = escaped.split(" | ", 1)
            escaped = f"<strong style='color:#e2e8f0;'>{left}</strong><br><span style='color:#cbd5e1;'>{right}</span>"
        else:
            escaped = f"<span style='color:#e2e8f0;'>{escaped}</span>"
            
        return (
            f"<div style='padding:8px 12px;margin:4px 0;background:{bg_map[tone]};"
            f"border-left:3px solid {color_map[tone]};border-radius:4px;'>"
            f"<span style='color:#64748b;font-size:12px;margin-right:10px;'>[{time_str}]</span>"
            f"{self._get_log_icon(tone)} {escaped}</div>"
        )

    def save_outline_clicked(self):
        if not self.selected_project:
            return
        CustomMessageBox.info(self, "提示", "大纲为只读预览，请直接编辑项目目录下的大纲.md文件")


    def create_project(self):
        dialog = NewProjectDialog(self)
        if dialog.exec() == QDialog.Accepted:
            name = dialog.get_name()
            style = dialog.get_style()
            if not name:
                CustomMessageBox.warning(self, "提示", "请输入项目名称")
                return
            try:
                created = create_new_project(name, style)
                self.selected_project = created
                self.refresh_projects()
            except Exception as exc:
                CustomMessageBox.critical(self, "创建失败", str(exc))

    def update_project_style_config(self):
        if not self.selected_project:
            return
        
        style_text = self.sidebar.combo_project_style.currentText()
        style_val = "tomato" if "番茄" in style_text else "standard"
        
        config = load_project_config(self.selected_project)
        if config.get("writing_style") != style_val:
            config["writing_style"] = style_val
            save_project_config(self.selected_project, config)

    def remove_project(self):
        if not self.selected_project:
            return
        answer = CustomMessageBox.question(self, "确认删除", f"确定删除项目 {self.selected_project} 吗？")
        if not answer:
            return
        delete_project(self.selected_project)
        self.selected_project = None
        self.refresh_projects()

    def open_api_settings(self):
        dialog = ApiSettingsDialog(self)
        if dialog.exec() == QDialog.Accepted:
            CustomMessageBox.success(self, "配置成功", "API配置已保存")

    def open_license_settings(self):
        dialog = LicenseSettingsDialog(self)
        if dialog.exec() == QDialog.Accepted:
            CustomMessageBox.success(self, "授权成功", "系统授权已验证并保存")

    def open_model_params_settings(self):
        dialog = ModelParamsDialog(self)
        if dialog.exec() == QDialog.Accepted:
            CustomMessageBox.success(self, "配置成功", "模型参数已保存")

    def start_generation(self):
        if self.is_generating:
            return
        if not self.selected_project:
            CustomMessageBox.warning(self, "提示", "请先创建或选择项目")
            return
        outline = load_outline(self.selected_project).strip()
        if len(outline) < 50:
            CustomMessageBox.warning(self, "提示", "请先完善大纲（至少 50 字）")
            return

        mode_index = self.tab_create.combo_mode.currentIndex()

        if mode_index == 0:  # 新建章节
            start = self.tab_create.spin_start.value()
            count = self.tab_create.spin_count.value()
            rewrite_suggestion = None
        else:  # 重写章节
            if self.tab_create.combo_chapter.count() == 0:
                CustomMessageBox.warning(self, "提示", "没有可重写的章节")
                return
            chapter_name = self.tab_create.combo_chapter.currentText()
            match = re.search(r"(\d+)", chapter_name)
            if not match:
                CustomMessageBox.warning(self, "提示", "无法识别章节序号")
                return
            start = int(match.group(1))
            count = 1
            rewrite_suggestion = self.tab_create.text_suggestion.toPlainText().strip()

        self.is_generating = True
        self.tab_create.btn_generate.setVisible(False)
        self.tab_create.btn_stop.setVisible(True)
        self.tab_create.progress.setVisible(True)
        self.tab_create.progress.setValue(0)
        self.tab_create.progress_label.setText("正在初始化生成引擎...")
        self.run_logs = []
        self.refresh_log_view()

        self.main_panel.tabs.setCurrentWidget(self.tab_monitor)

        self.worker_thread = QThread(self)
        self.worker = ChapterGenerationWorker(self.selected_project, outline, start, count, rewrite_suggestion)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.log.connect(self.on_worker_log)
        self.worker.progress.connect(self.on_worker_progress)
        self.worker.chapter_done.connect(self.on_worker_chapter_done)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()

    def on_worker_log(self, message, status):
        add_run_log(self.run_logs, "Agent流", message, status)
        self.refresh_log_view()

    def on_worker_progress(self, done, total, text):
        ratio = 0 if total <= 0 else int(done * 100 / total)
        self.tab_create.progress.setValue(ratio)
        self.tab_create.progress_label.setText(text)

    def on_worker_chapter_done(self, chapter_number):
        msg = f"第 {chapter_number} 章生成完成"
        add_run_log(self.run_logs, "系统", msg, "success")
        self.refresh_log_view()
        self.reload_project_data()

    def on_worker_finished(self, success, message):
        self.is_generating = False
        self.tab_create.btn_generate.setVisible(True)
        self.tab_create.btn_stop.setVisible(False)
        self.tab_create.btn_stop.setEnabled(True)
        self.tab_create.btn_stop.setText("停止生成")
        self.tab_create.btn_generate.setEnabled(True)
        self.tab_create.progress.setValue(0)
        self.tab_create.progress.setVisible(False)
        if success:
            add_run_log(self.run_logs, "系统", message, "success")
            self.refresh_log_view()
        else:
            CustomMessageBox.warning(self, "任务结束", message)
        self.reload_project_data()
        self.worker = None
        self.worker_thread = None

    def stop_generation(self):
        if self.worker and self.is_generating:
            self.worker.stop()
            self.tab_create.btn_stop.setEnabled(False)
            self.tab_create.btn_stop.setText("正在停止...")
            add_run_log(self.run_logs, "系统", "用户请求停止生成", "warning")
            self.refresh_log_view()

    def on_mode_changed(self, index):
        self.tab_create.settings_stack.setCurrentIndex(index)
        if index == 1:  # 重写模式
            self.refresh_chapter_combo()

    def refresh_chapter_combo(self):
        self.tab_create.combo_chapter.clear()
        if not self.selected_project:
            return
        chapters = list_generated_chapters(self.selected_project)
        if chapters:
            self.tab_create.combo_chapter.addItems(chapters)

    def refresh_chapter_filter(self):
        if not self.selected_project:
            self.all_chapters = []
            self.filtered_chapters = []
            self.tab_reader.chapter_combo.clear()
            return
        all_chapters = list_generated_chapters(self.selected_project)
        self.all_chapters = all_chapters
        keyword = self.tab_reader.chapter_search.text().strip()
        self.filtered_chapters = [c for c in all_chapters if keyword in c] if keyword else all_chapters
        self.tab_reader.chapter_combo.blockSignals(True)
        self.tab_reader.chapter_combo.clear()
        self.tab_reader.chapter_combo.addItems(self.filtered_chapters)
        self.tab_reader.chapter_combo.blockSignals(False)
        if not self.filtered_chapters:
            self.current_chapter_idx = 0
            self.tab_reader.chapter_title.setText("暂无章节")
            self.tab_reader.chapter_words.setText("0 字")
            self.tab_reader.chapter_content.setMarkdown("")
            self.tab_reader.btn_prev.setEnabled(False)
            self.tab_reader.btn_next.setEnabled(False)
            return
        self.current_chapter_idx = min(self.current_chapter_idx, len(self.filtered_chapters) - 1)
        self.tab_reader.chapter_combo.setCurrentIndex(self.current_chapter_idx)
        self.show_current_chapter()

    def on_chapter_selected(self):
        idx = self.tab_reader.chapter_combo.currentIndex()
        if idx < 0:
            return
        self.current_chapter_idx = idx
        self.show_current_chapter()

    def move_chapter(self, offset):
        if not self.filtered_chapters:
            return
        current_file = self.filtered_chapters[self.current_chapter_idx]
        if not self.all_chapters or current_file not in self.all_chapters:
            return
        full_idx = self.all_chapters.index(current_file)
        target_full_idx = max(0, min(full_idx + offset, len(self.all_chapters) - 1))
        target_file = self.all_chapters[target_full_idx]
        if self.tab_reader.chapter_search.text().strip():
            self.tab_reader.chapter_search.clear()
        if target_file not in self.filtered_chapters:
            return
        self.current_chapter_idx = self.filtered_chapters.index(target_file)
        self.tab_reader.chapter_combo.setCurrentIndex(self.current_chapter_idx)
        self.show_current_chapter()

    def show_current_chapter(self):
        if not self.filtered_chapters:
            self.tab_reader.btn_copy_chapter.setEnabled(False)
            return
        chapter_file = self.filtered_chapters[self.current_chapter_idx]
        content = load_chapter(self.selected_project, chapter_file)
        self.tab_reader.chapter_title.setText(chapter_file.replace(".md", ""))
        self.tab_reader.chapter_words.setText(f"{len(content)} 字")
        self.tab_reader.chapter_content.setMarkdown(content)
        self.tab_reader.btn_copy_chapter.setEnabled(True)
        if self.all_chapters and chapter_file in self.all_chapters:
            full_idx = self.all_chapters.index(chapter_file)
            self.tab_reader.btn_prev.setEnabled(full_idx > 0)
            self.tab_reader.btn_next.setEnabled(full_idx < len(self.all_chapters) - 1)
            return
        self.tab_reader.btn_prev.setEnabled(self.current_chapter_idx > 0)
        self.tab_reader.btn_next.setEnabled(self.current_chapter_idx < len(self.filtered_chapters) - 1)

    def copy_chapter_content(self):
        content = self.tab_reader.chapter_content.toPlainText()
        if not content:
            return
        
        clipboard = QApplication.clipboard()
        clipboard.setText(content)
        
        original_text = self.tab_reader.btn_copy_chapter.text()
        self.tab_reader.btn_copy_chapter.setText("✅ 已复制")
        self.tab_reader.btn_copy_chapter.setEnabled(False)
        
        def restore():
            try:
                self.tab_reader.btn_copy_chapter.setText(original_text)
                self.tab_reader.btn_copy_chapter.setEnabled(True)
            except RuntimeError:
                pass
                
        QTimer.singleShot(1500, restore)

    def _on_monitor_mode_changed(self, button):
        idx = self.tab_monitor.monitor_mode_group.id(button)
        if idx == 0:
            self.tab_monitor.show_thought_view()
        else:
            self.tab_monitor.show_raw_view()
        self.tab_monitor.btn_refresh_logs.setVisible(idx == 0)

    def clear_current_logs(self):
        if self.tab_monitor.monitor_stack.currentIndex() == 0:
            self.clear_logs_clicked()
        else:
            self.tab_monitor.raw_logs_view.clear()

    def clear_logs_clicked(self):
        clear_run_logs(self.run_logs)
        self.refresh_log_view()

    def refresh_log_view(self):
        if not self.run_logs:
            self.tab_monitor.logs_view.setHtml("<p style='color:#64748b; font-family:sans-serif;'>等待任务启动...</p>")
            return
        blocks = [self._format_log_html(log) for log in self.run_logs]
        self.tab_monitor.logs_view.setHtml("".join(blocks))
        self.tab_monitor.logs_view.verticalScrollBar().setValue(self.tab_monitor.logs_view.verticalScrollBar().maximum())

    def _export_guard(self):
        if not self.selected_project:
            CustomMessageBox.warning(self, "提示", "请先选择项目")
            return False
        return True

    def export_word_clicked(self):
        if not self._export_guard():
            return
        try:
            from src.export import export_to_word
            path = export_to_word(self.selected_project)
            self._show_export_result(f"已导出至: {path}", "success", path)
        except Exception as exc:
            self._show_export_result(f"导出失败: {exc}", "danger")

    def export_epub_clicked(self):
        if not self._export_guard():
            return
        try:
            from src.export import export_to_epub
            path = export_to_epub(self.selected_project)
            self._show_export_result(f"已导出至: {path}", "success", path)
        except Exception as exc:
            self._show_export_result(f"导出失败: {exc}", "danger")

    def export_txt_clicked(self):
        if not self._export_guard():
            return
        try:
            from src.export import export_to_txt
            path = export_to_txt(self.selected_project)
            self._show_export_result(f"已导出至: {path}", "success", path)
        except Exception as exc:
            self._show_export_result(f"导出失败: {exc}", "danger")

    def export_all_clicked(self):
        if not self._export_guard():
            return
        try:
            from src.export import export_all_formats
            paths = export_all_formats(self.selected_project)
            self._show_export_result(f"全部导出成功: {os.path.dirname(paths['txt'])}", "success", paths['txt'])
        except Exception as exc:
            self._show_export_result(f"导出失败: {exc}", "danger")
