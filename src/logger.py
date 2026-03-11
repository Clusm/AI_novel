from datetime import datetime


def add_run_log(logs_list, title, content, status="info"):
    """添加运行日志"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    icon = "✅" if status == "success" else "⚠️" if status == "warning" else "❌" if status in ("error", "danger") else "🔄"
    log_entry = f"{icon} **[{timestamp}] {title}**：{content}"
    logs_list.append(log_entry)
    return logs_list


def clear_run_logs(logs_list):
    """清空日志"""
    logs_list.clear()
    return logs_list


def get_logs_html(logs_list):
    """获取日志HTML格式"""
    if not logs_list:
        return "<p style='color: #666;'>暂无运行日志，开始生成后会显示在这里</p>"
    
    html = ""
    for log in reversed(logs_list):
        if "❌" in log:
            html += f"<div style='padding: 8px; margin: 4px 0; background-color: #ffebee; border-radius: 4px;'>{log}</div>"
        elif "✅" in log:
            html += f"<div style='padding: 8px; margin: 4px 0; background-color: #e8f5e8; border-radius: 4px;'>{log}</div>"
        else:
            html += f"<div style='padding: 8px; margin: 4px 0; background-color: #f5f5f5; border-radius: 4px;'>{log}</div>"
    return html
