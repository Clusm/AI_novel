import os
import json
import shutil
import re
from datetime import datetime
from src.workspace import workspace_manager

STORY_BIBLE_FILE = "剧情圣经.md"
SUMMARY_MAX_CHARS = 900
CANON_DIR = "canon"


def get_projects_root():
    return workspace_manager.get_projects_dir()


def init_projects_dir():
    """初始化项目目录"""
    projects_dir = get_projects_root()
    if not os.path.exists(projects_dir):
        os.makedirs(projects_dir)


def get_all_projects():
    """获取所有项目列表"""
    init_projects_dir()
    projects_dir = get_projects_root()
    return sorted([d for d in os.listdir(projects_dir) if os.path.isdir(os.path.join(projects_dir, d))])


def create_new_project(book_name):
    """创建新项目"""
    safe_name = "".join(c for c in book_name if c.isalnum() or c in " _-").strip() or "新书"
    projects_dir = get_projects_root()
    project_dir = os.path.join(projects_dir, safe_name)
    os.makedirs(project_dir, exist_ok=True)
    
    # 创建子目录
    os.makedirs(os.path.join(project_dir, "chapters"), exist_ok=True)
    os.makedirs(os.path.join(project_dir, "characters"), exist_ok=True)
    os.makedirs(os.path.join(project_dir, "logs"), exist_ok=True)
    os.makedirs(os.path.join(project_dir, "reports"), exist_ok=True)
    os.makedirs(os.path.join(project_dir, "summaries"), exist_ok=True)
    os.makedirs(os.path.join(project_dir, CANON_DIR), exist_ok=True)
    
    # 创建大纲文件
    outline_path = os.path.join(project_dir, "大纲.md")
    if not os.path.exists(outline_path):
        with open(outline_path, "w", encoding="utf-8") as f:
            f.write("# 请在这里粘贴你的大纲\n")

    # 创建剧情圣经（用于减少每章重复传入完整大纲）
    bible_path = os.path.join(project_dir, STORY_BIBLE_FILE)
    if not os.path.exists(bible_path):
        with open(bible_path, "w", encoding="utf-8") as f:
            f.write("# 剧情圣经（自动生成）\n\n> 由系统根据大纲自动提炼，用于人物/世界观/主线/伏笔等全局一致性。\n")
    
    # 创建配置文件
    config_path = os.path.join(project_dir, "config.json")
    config = {
        "name": safe_name,
        "created_at": datetime.now().isoformat(),
        "last_modified": datetime.now().isoformat(),
        "chapters": [],
        "characters": {},
        "worldview": {},
        "total_chapters": 0,
        "outline_hash": "",
        "story_bible_updated_at": None
    }
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    return safe_name


def load_project_config(project_name):
    """加载项目配置"""
    project_dir = os.path.join(get_projects_root(), project_name)
    config_path = os.path.join(project_dir, "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_project_config(project_name, config):
    """保存项目配置"""
    project_dir = os.path.join(get_projects_root(), project_name)
    config_path = os.path.join(project_dir, "config.json")
    config["last_modified"] = datetime.now().isoformat()
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def delete_project(project_name):
    """删除项目"""
    project_dir = os.path.join(get_projects_root(), project_name)
    if os.path.exists(project_dir):
        shutil.rmtree(project_dir)


def list_generated_chapters(project_name):
    """列出已生成的章节（按章节号自然排序）"""
    project_dir = os.path.join(get_projects_root(), project_name, "chapters")
    if os.path.exists(project_dir):
        files = [f for f in os.listdir(project_dir) if f.endswith(".md")]
        # 自然排序：第2章 < 第10章
        files.sort(key=lambda s: [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)])
        return files
    return []


def save_chapter(project_name, chapter_number, content):
    """保存生成的章节"""
    # 强制转换章节号为整数，避免出现中文数字或浮点数
    try:
        chapter_num = int(chapter_number)
    except (ValueError, TypeError):
        # 如果转换失败（比如已经是"第3章"），尝试提取数字
        m = re.search(r"(\d+)", str(chapter_number))
        chapter_num = int(m.group(1)) if m else chapter_number

    project_dir = os.path.join(get_projects_root(), project_name, "chapters")
    os.makedirs(project_dir, exist_ok=True)
    chapter_path = os.path.join(project_dir, f"第{chapter_num}章.md")
    with open(chapter_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    # 更新配置文件
    config = load_project_config(project_name)
    chapter_file = f"第{chapter_num}章.md"
    if chapter_file not in config.get("chapters", []):
        config["chapters"].append(chapter_file)
        # 按自然顺序重新排序章节列表
        config["chapters"].sort(key=lambda s: [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)])
        config["total_chapters"] = len(config["chapters"])
        save_project_config(project_name, config)


def load_chapter(project_name, chapter_file):
    """加载章节内容"""
    chapter_path = os.path.join(get_projects_root(), project_name, "chapters", chapter_file)
    if os.path.exists(chapter_path):
        with open(chapter_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def load_outline(project_name):
    """加载大纲内容"""
    outline_path = os.path.join(get_projects_root(), project_name, "大纲.md")
    if os.path.exists(outline_path):
        with open(outline_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def load_story_bible(project_name):
    """加载剧情圣经内容"""
    bible_path = os.path.join(get_projects_root(), project_name, STORY_BIBLE_FILE)
    if os.path.exists(bible_path):
        with open(bible_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def save_story_bible(project_name, content):
    """保存剧情圣经内容"""
    bible_path = os.path.join(get_projects_root(), project_name, STORY_BIBLE_FILE)
    with open(bible_path, "w", encoding="utf-8") as f:
        f.write(content)

    config = load_project_config(project_name)
    config["story_bible_updated_at"] = datetime.now().isoformat()
    save_project_config(project_name, config)


def save_outline(project_name, outline_content):
    """保存大纲内容"""
    outline_path = os.path.join(get_projects_root(), project_name, "大纲.md")
    with open(outline_path, "w", encoding="utf-8") as f:
        f.write(outline_content)
    
    # 更新配置文件
    config = load_project_config(project_name)
    save_project_config(project_name, config)


def save_character_card(project_name, character_name, character_data):
    """保存人物卡"""
    character_path = os.path.join(get_projects_root(), project_name, "characters", f"{character_name}.json")
    with open(character_path, "w", encoding="utf-8") as f:
        json.dump(character_data, f, ensure_ascii=False, indent=2)


def load_character_card(project_name, character_name):
    """加载人物卡"""
    character_path = os.path.join(get_projects_root(), project_name, "characters", f"{character_name}.json")
    if os.path.exists(character_path):
        with open(character_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_review_report(project_name, chapter_number, report_content):
    """保存审查报告"""
    report_path = os.path.join(get_projects_root(), project_name, "reports", f"第{chapter_number}章审查报告.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)


def save_chapter_summary(project_name, chapter_number, summary_content, max_chars=SUMMARY_MAX_CHARS):
    summary_dir = os.path.join(get_projects_root(), project_name, "summaries")
    os.makedirs(summary_dir, exist_ok=True)
    summary_path = os.path.join(summary_dir, f"第{chapter_number}章摘要.md")
    text = (summary_content or "").strip()
    if len(text) > max_chars:
        text = text[: max_chars - 1] + "…"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(text)


def load_chapter_summary(project_name, chapter_number):
    summary_path = os.path.join(get_projects_root(), project_name, "summaries", f"第{chapter_number}章摘要.md")
    if os.path.exists(summary_path):
        with open(summary_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def save_canon_entry(project_name, chapter_number, canon_content):
    canon_dir = os.path.join(get_projects_root(), project_name, CANON_DIR)
    os.makedirs(canon_dir, exist_ok=True)
    canon_path = os.path.join(canon_dir, f"第{chapter_number}章台账.md")
    with open(canon_path, "w", encoding="utf-8") as f:
        f.write((canon_content or "").strip())


def load_recent_canon_entries(project_name, limit=3):
    canon_dir = os.path.join(get_projects_root(), project_name, CANON_DIR)
    if not os.path.exists(canon_dir):
        return []
    files = [f for f in os.listdir(canon_dir) if f.endswith(".md")]
    files.sort(key=lambda s: [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)])
    picked = files[-max(1, int(limit)):] if files else []
    result = []
    for name in picked:
        path = os.path.join(canon_dir, name)
        try:
            with open(path, "r", encoding="utf-8") as f:
                result.append(f.read())
        except Exception:
            continue
    return result


def save_run_log(project_name, log_content):
    """保存运行日志"""
    log_dir = os.path.join(get_projects_root(), project_name, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_run.log")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(log_content)


def get_project_info(project_name):
    """获取项目信息"""
    config = load_project_config(project_name)
    chapters = list_generated_chapters(project_name)
    return {
        "name": config.get("name", project_name),
        "created_at": config.get("created_at"),
        "last_modified": config.get("last_modified"),
        "total_chapters": len(chapters),
        "generated_chapters": chapters
    }
