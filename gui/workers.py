from PySide6.QtCore import QObject, Signal

from src.api import load_api_keys, test_api_connection
from src.generator import generate_multiple_chapters

class ChapterGenerationWorker(QObject):
    finished = Signal(bool, str)
    progress = Signal(int, int, str)
    log = Signal(str, str)
    chapter_done = Signal(int)

    def __init__(self, project_name, outline, start_chapter, count):
        super().__init__()
        self.project_name = project_name
        self.outline = outline
        self.start_chapter = start_chapter
        self.count = count
        self.is_running = True

    def run(self):
        try:
            self.log.emit("🚀 任务启动，正在加载 AI 模型与配置...", "info")
            
            # 增加短暂延时确保 UI 渲染出第一条日志
            import time
            time.sleep(0.5)

            try:
                keys = load_api_keys()
            except Exception as e:
                self.log.emit(f"❌ 读取配置文件失败: {str(e)}", "error")
                self.finished.emit(False, "无法读取 API 配置")
                return

            route_profile = keys.get("ROUTE_PROFILE", "speed")
            writer_model = keys.get("WRITER_MODEL", "auto")

            self.log.emit("🔎 正在检测 API Key 配置与连通性...", "info")
            
            deepseek_key = (keys.get("DEEPSEEK_API_KEY") or "").strip()
            qwen_key = (keys.get("DASHSCOPE_API_KEY") or "").strip()
            kimi_key = (keys.get("MOONSHOT_API_KEY") or "").strip()

            missing_required = []
            if not deepseek_key:
                missing_required.append("DeepSeek")
            if not qwen_key:
                missing_required.append("通义千问")

            if missing_required:
                self.log.emit(f"❌ 缺少必要 API Key：{', '.join(missing_required)}", "error")
                self.log.emit("💡 请前往「系统设置 → API 配置」填入 Key 并保存。", "warning")
                self.finished.emit(False, "必要 API Key 缺失")
                return

            if writer_model == "kimi" and not kimi_key:
                self.log.emit("⚠️ 主写模型选了 Kimi 但未配置 Key，将自动降级为通义千问。", "warning")

            checks = [("deepseek", deepseek_key), ("qwen", qwen_key)]
            if kimi_key:
                checks.append(("kimi", kimi_key))

            required_failed = False
            for provider, api_key in checks:
                self.log.emit(f"📡 正在连接 {provider} API...", "info")
                # 再次强制 try-catch 确保测试函数不抛出异常中断流程
                try:
                    ok, msg = test_api_connection(provider, api_key, route_profile=route_profile)
                except Exception as e:
                    ok, msg = False, str(e)

                if ok:
                    self.log.emit(f"✅ {provider}：连接正常", "success")
                else:
                    self.log.emit(f"❌ {provider}：连接失败 - {msg}", "error")
                    if provider in ("deepseek", "qwen"):
                        required_failed = True
            
            if required_failed:
                self.log.emit("⛔ 核心 API 连接失败，无法继续生成。", "error")
                self.finished.emit(False, "核心 API 连接失败")
                return

            self.log.emit("✅ API 检测通过，正在初始化多 Agent 工作流...", "success")
            total_steps = self.count * 5
            current_step = 0

            def log_callback(message, status="info"):
                nonlocal current_step
                self.log.emit(message, status)
                if "✅" in message or "已加载" in message:
                    current_step += 1
                    # 避免进度条超过 100%
                    display_step = min(current_step, total_steps)
                    self.progress.emit(display_step, total_steps, message)

            generate_multiple_chapters(
                self.project_name,
                self.outline,
                self.start_chapter,
                self.start_chapter + self.count - 1,
                log_callback=log_callback
            )
            self.finished.emit(True, "所有章节生成完成！")
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.log.emit(f"❌ 生成过程中发生未捕获异常:\n{error_details}", "error")
            self.finished.emit(False, f"生成过程中断: {e}")

    def stop(self):
        self.is_running = False
