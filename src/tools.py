"""
Agent Tools 模块 - 为 CrewAI Agent 提供文件读取能力

各工具职责：
- read_character_cards: 读取项目人物卡（供人物守护者使用）
- read_world_settings: 从剧情圣经中提取世界观设定（供人物守护者使用）
- read_chapter_outline_detail: 读取大纲中指定章节内容（供主写手使用）

设计原则：
- 文件不存在时返回说明文字，不抛异常，不阻断 Agent 流程
- 所有路径通过 project.py 中的标准函数解析，不暴露绝对路径给 LLM
- 工具参数使用 project_name 传递上下文，由 agents.py 通过闭包绑定
"""

import os
import json
import re
from crewai.tools import tool


def make_read_character_cards(project_name: str):
    """
    工厂函数：生成绑定了 project_name 的 read_character_cards 工具

    返回的工具读取 projects/<project_name>/characters/ 下所有 .json 和 .md 格式的人物卡，
    合并为单一文本供 Agent 使用。
    """
    @tool("read_character_cards")
    def read_character_cards(dummy: str = "") -> str:
        """
        读取当前项目的所有人物卡信息。
        返回格式化后的人物卡文本，包含人物姓名、性格、背景、能力等信息。
        当需要核查人物一致性时调用此工具。
        """
        from src.project import get_projects_root
        chars_dir = os.path.join(get_projects_root(), project_name, "characters")
        if not os.path.exists(chars_dir):
            return "（人物卡目录不存在，请根据剧情圣经中的人物信息处理）"

        parts = []
        for fname in sorted(os.listdir(chars_dir)):
            fpath = os.path.join(chars_dir, fname)
            if fname.endswith(".json"):
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    name = fname.replace(".json", "")
                    parts.append(f"### {name}\n" + json.dumps(data, ensure_ascii=False, indent=2))
                except Exception:
                    pass
            elif fname.endswith(".md"):
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        parts.append(f.read().strip())
                except Exception:
                    pass

        if not parts:
            return "（人物卡目录为空，请根据剧情圣经中的人物信息处理）"
        return "\n\n".join(parts)

    return read_character_cards


def make_read_world_settings(project_name: str):
    """
    工厂函数：生成绑定了 project_name 的 read_world_settings 工具

    从剧情圣经中提取世界观相关段落（## 世界观、## 规则、## 设定 等标题下的内容）。
    """
    @tool("read_world_settings")
    def read_world_settings(dummy: str = "") -> str:
        """
        读取当前项目的世界观设定信息。
        从剧情圣经中提取世界观规则、设定约束等内容。
        当需要核查世界观一致性时调用此工具。
        """
        from src.project import get_projects_root
        bible_path = os.path.join(get_projects_root(), project_name, "剧情圣经.md")
        if not os.path.exists(bible_path):
            return "（剧情圣经文件不存在，请根据大纲中的设定信息处理）"

        with open(bible_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 提取世界观相关章节
        world_keywords = ["世界观", "规则", "设定", "background", "world"]
        lines = content.split("\n")
        result_parts = []
        in_section = False
        section_depth = 0

        for line in lines:
            header_match = re.match(r"^(#{1,4})\s+(.+)", line)
            if header_match:
                depth = len(header_match.group(1))
                title = header_match.group(2).lower()
                is_world_section = any(kw in title for kw in world_keywords)
                if is_world_section:
                    in_section = True
                    section_depth = depth
                    result_parts.append(line)
                elif in_section and depth <= section_depth:
                    # 遇到同级或更高级标题，结束当前世界观段落
                    in_section = False
            elif in_section:
                result_parts.append(line)

        if result_parts:
            return "\n".join(result_parts).strip()

        # 若未找到专属世界观段落，返回圣经全文（截断至2000字）
        if len(content) > 2000:
            return content[:1999].rstrip() + "…"
        return content

    return read_world_settings


def make_read_chapter_outline_detail(project_name: str, chapter_number: int):
    """
    工厂函数：生成绑定了 project_name 和 chapter_number 的 read_chapter_outline_detail 工具

    从大纲.md 中提取当前章节的详细内容。
    """
    @tool("read_chapter_outline_detail")
    def read_chapter_outline_detail(dummy: str = "") -> str:
        """
        读取大纲中当前章节的详细内容。
        返回当前章节在大纲中的完整描述，供写作时参考。
        当需要确认本章应写的情节时调用此工具。
        """
        from src.project import get_projects_root
        outline_path = os.path.join(get_projects_root(), project_name, "大纲.md")
        if not os.path.exists(outline_path):
            return f"（大纲文件不存在）"

        with open(outline_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 尝试匹配 "#### 第N章" 或 "**第N章" 等格式
        n = int(chapter_number)
        patterns = [
            rf"(?m)^#{1,4}\s+第{n}章[^\n]*\n(.*?)(?=^#{1,4}\s+第\d+章|\Z)",
            rf"(?m)\*\*第{n}章[^\n]*\*\*(.*?)(?=\*\*第\d+章|\Z)",
        ]
        for pat in patterns:
            m = re.search(pat, content, re.DOTALL)
            if m:
                section = m.group(0).strip()
                if len(section) > 1500:
                    section = section[:1499].rstrip() + "…"
                return section

        return f"（大纲中未找到第{n}章的专属条目，请根据已有上下文推断本章情节）"

    return read_chapter_outline_detail
