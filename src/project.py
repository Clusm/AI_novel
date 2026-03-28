"""
项目管理模块 - 处理小说项目的创建、读取、更新、删除操作

核心功能：
1. 项目管理：创建、删除、获取项目列表
2. 章节管理：保存、加载、列出章节
3. 大纲管理：保存、加载大纲
4. 剧情圣经：保存、加载剧情圣经（全局设定文档）
5. 人物卡：保存、加载人物卡
6. 摘要与台账：保存章节摘要和事实台账
7. 运行日志：保存生成过程的日志

目录结构：
项目目录/
├── config.json          # 项目配置
├── 大纲.md              # 故事大纲
├── 剧情圣经.md          # 全局设定文档
├── chapters/            # 章节正文
├── characters/          # 人物卡
├── summaries/           # 章节摘要
├── canon/               # 事实台账
├── reports/             # 审查报告
└── logs/                # 运行日志
"""

import os
import json
import shutil
import re
from datetime import datetime
from src.workspace import workspace_manager

# 常量定义
STORY_BIBLE_FILE = "剧情圣经.md"      # 剧情圣经文件名
SUMMARY_MAX_CHARS = 900               # 摘要最大字符数
CANON_DIR = "canon"                   # 事实台账目录名


def get_projects_root():
    """获取项目根目录路径"""
    return workspace_manager.get_projects_dir()


def _project_dir(project_name):
    """获取指定项目的目录路径"""
    return os.path.join(get_projects_root(), project_name)


def _natural_sort_key(value):
    """
    文件名自然排序键

    用于正确排序章节文件，例如：
    第2章.md < 第10章.md（而不是字典序：第10章.md < 第2章.md）

    参数：
    - value: 文件名

    返回：排序键列表
    """
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", value)]


def _read_text_if_exists(path):
    """读取文本文件，若不存在返回空字符串"""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def _read_json_if_exists(path, default):
    """读取 JSON 文件，若不存在返回默认值"""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def _write_text(path, content):
    """写入文本文件"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def init_projects_dir():
    """初始化项目根目录（若不存在则创建）"""
    projects_dir = get_projects_root()
    if not os.path.exists(projects_dir):
        os.makedirs(projects_dir)


def get_all_projects():
    """获取所有项目列表（按名称排序）"""
    init_projects_dir()
    projects_dir = get_projects_root()
    return sorted([d for d in os.listdir(projects_dir) if os.path.isdir(os.path.join(projects_dir, d))])


def create_new_project(book_name, writing_style="standard"):
    """
    创建新项目

    参数：
    - book_name: 书名
    - writing_style: 文风模式（standard/tomato）

    返回：实际创建的项目名称（可能经过安全化处理）

    创建的目录结构：
    - chapters/: 章节正文
    - characters/: 人物卡
    - logs/: 运行日志
    - reports/: 审查报告
    - summaries/: 章节摘要
    - canon/: 事实台账
    """
    # 安全化项目名称：只保留字母、数字、空格、下划线、横线
    safe_name = "".join(c for c in book_name if c.isalnum() or c in " _-").strip() or "新书"
    project_dir = _project_dir(safe_name)
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
        _write_text(outline_path, "# 请在这里粘贴你的大纲\n")

    # 创建剧情圣经（用于减少每章重复传入完整大纲）
    bible_path = os.path.join(project_dir, STORY_BIBLE_FILE)
    if not os.path.exists(bible_path):
        _write_text(
            bible_path,
            "# 剧情圣经（自动生成）\n\n> 由系统根据大纲自动提炼，用于人物/世界观/主线/伏笔等全局一致性。\n",
        )

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
        "story_bible_updated_at": None,
        "writing_style": writing_style
    }
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    return safe_name


def load_project_config(project_name):
    """加载项目配置（返回字典，若不存在返回空字典）"""
    config_path = os.path.join(_project_dir(project_name), "config.json")
    return _read_json_if_exists(config_path, {})


def save_project_config(project_name, config):
    """保存项目配置（自动更新 last_modified 时间戳）"""
    config_path = os.path.join(_project_dir(project_name), "config.json")
    config["last_modified"] = datetime.now().isoformat()
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def delete_project(project_name):
    """删除项目（包括所有章节、配置、日志等）"""
    project_dir = _project_dir(project_name)
    if os.path.exists(project_dir):
        shutil.rmtree(project_dir)


def list_generated_chapters(project_name):
    """
    列出已生成的章节文件

    返回：章节文件名列表，按章节号自然排序
    例如：["第1章.md", "第2章.md", "第10章.md"]
    """
    project_dir = os.path.join(_project_dir(project_name), "chapters")
    if os.path.exists(project_dir):
        files = [f for f in os.listdir(project_dir) if f.endswith(".md")]
        files.sort(key=_natural_sort_key)
        return files
    return []


def save_chapter(project_name, chapter_number, content):
    """
    保存生成的章节

    参数：
    - project_name: 项目名称
    - chapter_number: 章节序号（整数或"第N章"格式）
    - content: 章节内容

    同时更新项目配置中的章节列表
    """
    # 强制转换章节号为整数，避免出现中文数字或浮点数
    try:
        chapter_num = int(chapter_number)
    except (ValueError, TypeError):
        # 如果转换失败（比如已经是"第3章"），尝试提取数字
        m = re.search(r"(\d+)", str(chapter_number))
        chapter_num = int(m.group(1)) if m else chapter_number

    project_dir = os.path.join(_project_dir(project_name), "chapters")
    os.makedirs(project_dir, exist_ok=True)
    chapter_path = os.path.join(project_dir, f"第{chapter_num}章.md")
    _write_text(chapter_path, content)

    # 更新配置文件
    config = load_project_config(project_name)
    chapter_file = f"第{chapter_num}章.md"
    if chapter_file not in config.get("chapters", []):
        config["chapters"].append(chapter_file)
        # 按自然顺序重新排序章节列表
        config["chapters"].sort(key=_natural_sort_key)
        config["total_chapters"] = len(config["chapters"])
        save_project_config(project_name, config)


def load_chapter(project_name, chapter_file):
    """加载章节内容"""
    chapter_path = os.path.join(_project_dir(project_name), "chapters", chapter_file)
    return _read_text_if_exists(chapter_path)


def load_outline(project_name):
    """加载大纲内容"""
    outline_path = os.path.join(_project_dir(project_name), "大纲.md")
    return _read_text_if_exists(outline_path)


def load_story_bible(project_name):
    """
    加载剧情圣经内容

    剧情圣经是一份全局设定文档，包含：
    - 题材基调、世界观规则
    - 主线目标与阶段推进
    - 核心人物卡、关系网
    - 爽点配方、伏笔表、写作约束

    用于减少每章重复传入完整大纲，降低 token 消耗
    """
    bible_path = os.path.join(_project_dir(project_name), STORY_BIBLE_FILE)
    return _read_text_if_exists(bible_path)


def save_story_bible(project_name, content):
    """保存剧情圣经内容（自动更新 story_bible_updated_at 时间戳）"""
    bible_path = os.path.join(_project_dir(project_name), STORY_BIBLE_FILE)
    _write_text(bible_path, content)

    config = load_project_config(project_name)
    config["story_bible_updated_at"] = datetime.now().isoformat()
    save_project_config(project_name, config)


def save_outline(project_name, outline_content):
    """保存大纲内容"""
    outline_path = os.path.join(_project_dir(project_name), "大纲.md")
    _write_text(outline_path, outline_content)

    # 更新配置文件
    config = load_project_config(project_name)
    save_project_config(project_name, config)


def save_character_card(project_name, character_name, character_data):
    """保存人物卡（JSON 格式）"""
    character_path = os.path.join(_project_dir(project_name), "characters", f"{character_name}.json")
    with open(character_path, "w", encoding="utf-8") as f:
        json.dump(character_data, f, ensure_ascii=False, indent=2)


def load_character_card(project_name, character_name):
    """加载人物卡"""
    character_path = os.path.join(_project_dir(project_name), "characters", f"{character_name}.json")
    return _read_json_if_exists(character_path, {})


def save_review_report(project_name, chapter_number, report_content):
    """保存审查报告"""
    report_path = os.path.join(_project_dir(project_name), "reports", f"第{chapter_number}章审查报告.md")
    _write_text(report_path, report_content)


def save_chapter_summary(project_name, chapter_number, summary_content, max_chars=SUMMARY_MAX_CHARS):
    """
    保存章节摘要

    参数：
    - project_name: 项目名称
    - chapter_number: 章节序号
    - summary_content: 摘要内容
    - max_chars: 最大字符数（超出则截断加省略号）
    """
    summary_dir = os.path.join(_project_dir(project_name), "summaries")
    os.makedirs(summary_dir, exist_ok=True)
    summary_path = os.path.join(summary_dir, f"第{chapter_number}章摘要.md")
    text = (summary_content or "").strip()
    if len(text) > max_chars:
        text = text[: max_chars - 1] + "…"
    _write_text(summary_path, text)


def load_chapter_summary(project_name, chapter_number):
    """加载章节摘要"""
    summary_path = os.path.join(_project_dir(project_name), "summaries", f"第{chapter_number}章摘要.md")
    return _read_text_if_exists(summary_path)


def save_canon_entry(project_name, chapter_number, canon_content):
    """
    保存事实台账

    事实台账记录每章的：
    - 不可逆事实
    - 角色状态变更
    - 资源与能力变更
    - 伏笔状态流转
    - 下一章承接锚点

    用于后续章节保持一致性
    """
    canon_dir = os.path.join(_project_dir(project_name), CANON_DIR)
    os.makedirs(canon_dir, exist_ok=True)
    canon_path = os.path.join(canon_dir, f"第{chapter_number}章台账.md")
    _write_text(canon_path, (canon_content or "").strip())


def load_recent_canon_entries(project_name, limit=3):
    """
    加载最近 N 章的事实台账

    参数：
    - project_name: 项目名称
    - limit: 加载的章节数量

    返回：事实台账内容列表（按章节顺序）
    """
    canon_dir = os.path.join(_project_dir(project_name), CANON_DIR)
    if not os.path.exists(canon_dir):
        return []
    files = [f for f in os.listdir(canon_dir) if f.endswith(".md")]
    files.sort(key=_natural_sort_key)
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
    """保存运行日志（文件名包含时间戳）"""
    log_dir = os.path.join(_project_dir(project_name), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_run.log")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(log_content)


def get_project_info(project_name):
    """
    获取项目信息

    返回：{
        name: 项目名称
        created_at: 创建时间
        last_modified: 最后修改时间
        total_chapters: 已生成章节数
        total_planned_chapters: 计划章节数（从大纲统计）
        generated_chapters: 已生成章节列表
        writing_style: 文风模式
    }
    """
    config = load_project_config(project_name)
    chapters = list_generated_chapters(project_name)

    # 尝试从大纲中统计计划章节数（仅统计分卷细纲后的章节）
    outline = load_outline(project_name)
    planned_chapters = 0
    if outline:
        # 查找"分卷细纲"或类似的标记，如果没有则从头统计
        start_index = 0
        match = re.search(r'#+\s*分卷细纲|#+\s*章节大纲', outline)
        if match:
            start_index = match.end()

        # 统计形如 "### 第X章" 或 "第X章" 的行
        # 使用更严格的正则避免误判
        chapter_matches = re.findall(r'(?:^|\n)#*\s*第\s*\d+\s*章', outline[start_index:])
        planned_chapters = len(chapter_matches)

    return {
        "name": config.get("name", project_name),
        "created_at": config.get("created_at"),
        "last_modified": config.get("last_modified"),
        "total_chapters": len(chapters),
        "total_planned_chapters": planned_chapters,
        "generated_chapters": chapters,
        "writing_style": config.get("writing_style", "standard")
    }
