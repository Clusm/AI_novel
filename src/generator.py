"""
章节生成模块 - 使用 CrewAI 多 Agent 流水线生成小说章节

核心功能：
1. 多 Agent 协作：大纲优化师、世界观守护者、主写手、审校专家
2. 记忆功能：使用通义千问 embedding 接口实现长期记忆
3. 剧情圣经：自动提炼全局设定，保持章节一致性
4. 番茄模式：专为番茄小说优化的紧凑生成模式
5. 开头去重：自动检测并改写重复的章节开头
"""

import os
import sys
import queue
from difflib import SequenceMatcher

# 修复 Windows 下 ChromaDB 需要 sqlite3 >= 3.35 的问题
if sys.platform == "win32":
    try:
        import pysqlite3
        sys.modules["sqlite3"] = pysqlite3
    except ImportError:
        pass

# 彻底禁用 CrewAI 的 Telemetry 和 Tracing，防止网络阻塞或提示干扰
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
os.environ["CREWAI_TRACING_ENABLED"] = "false"
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["OTEL_TRACES_EXPORTER"] = "none"
os.environ["OTEL_METRICS_EXPORTER"] = "none"
os.environ["OTEL_LOGS_EXPORTER"] = "none"

from crewai import Crew, Process, Agent, Task, LLM
from src.agents import create_agents
from src.tasks import create_tasks
from src.project import (
    save_chapter,
    save_chapter_summary,
    save_run_log,
    load_project_config,
    save_project_config,
    load_story_bible,
    save_story_bible,
    load_chapter,
    load_chapter_summary,
    save_canon_entry,
    load_recent_canon_entries,
)
from src.workspace import workspace_manager
from src.api import load_api_keys
from datetime import datetime
import hashlib
import re
import time
from concurrent.futures import ThreadPoolExecutor


def get_embedder_config():
    """
    获取 CrewAI 记忆用的 embedder 配置
    使用通义千问 DashScope 的 OpenAI 兼容 embedding 接口
    返回：embedder 配置字典，若无 API Key 则返回 None
    """
    keys = load_api_keys()
    api_key = keys.get("DASHSCOPE_API_KEY", "").strip()
    if not api_key:
        return None
    return {
        "provider": "openai",
        "config": {
            "api_key": api_key,
            "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "model": "text-embedding-v3",
        },
    }


def _tomato_compact_context(text: str, max_chars: int) -> str:
    """
    番茄模式专用：压缩上下文文本
    移除多余换行，超长文本截断加省略号
    """
    raw = (text or "").strip()
    if not raw:
        return ""
    raw = re.sub(r"\n{3,}", "\n\n", raw).strip()
    if len(raw) <= max_chars:
        return raw
    return raw[: max_chars - 1].rstrip() + "…"


def _md_last_section(text: str, header: str) -> str:
    """
    提取 Markdown 文本中最后一个指定标题下的内容
    用于从摘要中提取特定小节
    """
    raw = (text or "").strip()
    if not raw:
        return ""
    pattern = rf"(?m)^##\s*{re.escape(header)}\s*$"
    last = None
    for m in re.finditer(pattern, raw):
        last = m
    if not last:
        return ""
    start = last.end()
    next_header = re.search(r"(?m)^##\s+", raw[start:])
    end = start + next_header.start() if next_header else len(raw)
    return raw[start:end].strip()


def _tight_one_liner(text: str, max_chars: int) -> str:
    """将文本压缩为单行，超长截断"""
    s = re.sub(r"\s+", " ", (text or "").strip())
    if not s:
        return ""
    if len(s) <= max_chars:
        return s
    return s[: max_chars - 1].rstrip() + "…"


def _take_bullet_lines(text: str, max_items: int) -> list[str]:
    """提取文本中的项目符号行，最多返回 max_items 条"""
    out = []
    for line in (text or "").splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith(("-", "•", "·")):
            out.append(s)
        if len(out) >= max_items:
            break
    return out


def _build_tomato_recap(project_name: str, chapter_number: int) -> str:
    """
    番茄模式专用：构建上一章回顾内容
    提取上一章摘要、事实台账、末尾原文，用于承接
    """
    prev_num = int(chapter_number) - 1
    if prev_num <= 0:
        return ""
    summary = load_chapter_summary(project_name, prev_num).strip()
    tail = load_chapter(project_name, f"第{prev_num}章.md")
    tail = _chapter_tail_for_context(tail, max_chars=1200).strip() if tail else ""
    canon_entries = load_recent_canon_entries(project_name, limit=3)
    canon = "\n\n".join([c.strip() for c in canon_entries if c.strip()])
    blocks = []
    if summary:
        s_irrev = _md_last_section(summary, "不可逆事实")
        s_end = _md_last_section(summary, "章末状态")
        s_anchor = _md_last_section(summary, "下一章承接锚点")
        lines = []
        if s_irrev:
            lines.append(f"- 不可逆：{_tight_one_liner(s_irrev, 180)}")
        if s_end:
            lines.append(f"- 章末：{_tight_one_liner(s_end, 200)}")
        if s_anchor:
            lines.append(f"- 承接：{_tight_one_liner(s_anchor, 200)}")
        payload = "\n".join(lines).strip() or _tomato_compact_context(summary, 900)
        blocks.append(f"【上一章摘要（供承接）】\n{_tomato_compact_context(payload, 900)}")
    if canon:
        c_irrev = _md_last_section(canon, "不可逆事实")
        c_state = _md_last_section(canon, "角色状态变更")
        c_anchor = _md_last_section(canon, "下一章必须承接锚点")
        lines = []
        lines.extend(_take_bullet_lines(c_irrev, 4))
        lines.extend(_take_bullet_lines(c_state, 4))
        lines.extend(_take_bullet_lines(c_anchor, 4))
        payload = "\n".join(lines).strip() or _tomato_compact_context(canon, 900)
        blocks.append(f"【最近事实台账（供承接）】\n{_tomato_compact_context(payload, 900)}")
    if tail:
        blocks.append(f"【上一章末尾原文片段（必须从这里接续）】\n{_tomato_compact_context(tail, 1200)}")
    return "\n\n".join(blocks).strip()


def _outline_hash(text: str) -> str:
    """计算大纲文本的 SHA256 哈希值，用于检测大纲变化"""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _clamp(text: str, max_chars: int) -> str:
    """截断文本到指定最大长度，末尾加省略号"""
    if max_chars <= 0:
        return ""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "…"


def _build_chapter_summary(chapter_number: int, content: str, max_chars: int = 900) -> str:
    """
    构建章节摘要（正则提取版）
    包含：本章目标、不可逆事实、章末状态、下一章承接锚点
    """
    raw = (content or "").strip()
    body = re.sub(r"^#.*\n?", "", raw).strip()
    body = re.sub(r"\n{2,}", "\n", body)
    chunks = [c.strip() for c in re.split(r"(?<=[。！？])", body) if c.strip()]
    core_goal = "".join(chunks[:2]) if chunks else body[:220]
    irreversible = "；".join(chunks[2:5]) if len(chunks) > 2 else "".join(chunks[:3])
    end_state = "".join(chunks[-2:]) if len(chunks) >= 2 else body[-180:]
    anchor = chunks[-1] if chunks else ""
    core_goal = _clamp(core_goal, 220)
    irreversible = _clamp(irreversible, 220)
    end_state = _clamp(end_state, 180)
    anchor = _clamp(anchor, 110)
    summary = (
        f"# 第{chapter_number}章摘要\n\n"
        f"## 本章目标达成\n{core_goal}\n\n"
        f"## 不可逆事实\n{irreversible or '本章未出现明显不可逆事实。'}\n\n"
        f"## 章末状态\n{end_state}\n\n"
        f"## 下一章承接锚点\n{anchor or '待下一章承接。'}"
    )
    return _clamp(summary, max_chars)


def _extract_sentences(text: str):
    """按句号、感叹号、问号分割文本为句子列表"""
    return [c.strip() for c in re.split(r"(?<=[。！？])", text) if c.strip()]


def _extract_resource_mentions(text: str):
    """提取文本中的资源/能力变更提及（如道源点、道纹、突破等）"""
    patterns = [
        r"道源点[+＋-]?\d+",
        r"道纹[^，。；\n]{0,20}",
        r"突破[^，。；\n]{0,20}",
        r"获得[^，。；\n]{0,30}",
        r"解锁[^，。；\n]{0,30}",
    ]
    hits = []
    for pat in patterns:
        for m in re.findall(pat, text):
            m = m.strip()
            if m and m not in hits:
                hits.append(m)
            if len(hits) >= 5:
                return hits
    return hits


def _extract_summary_block(text: str) -> tuple[str, str]:
    """
    从文本中提取 [SUMMARY_BEGIN]...[SUMMARY_END] 标记的摘要块
    返回：(正文, 摘要)
    """
    if not text:
        return "", ""
    pattern = r"\[SUMMARY_BEGIN\]([\s\S]*?)\[SUMMARY_END\]"
    match = re.search(pattern, text)
    if not match:
        return text, ""
    summary = match.group(1).strip()
    body = (text[: match.start()] + text[match.end():]).strip()
    return body, summary


def _normalize_summary(chapter_number: int, summary_text: str, max_chars: int = 900) -> str:
    """标准化摘要格式，确保以标题开头"""
    summary = (summary_text or "").strip()
    if not summary:
        return ""
    if not summary.startswith("#"):
        summary = f"# 第{chapter_number}章摘要\n\n{summary}"
    return _clamp(summary, max_chars)


def _generate_summary_via_llm(content: str, llm, max_chars: int = 900) -> str:
    """
    使用 LLM 生成高质量章节摘要
    包含：核心情节、关键信息、角色状态、不可逆事实、承接锚点
    """
    prompt = f"""
请为以下章节正文生成一份高质量的摘要，主要目的是**指导下一章的续写**。
请务必包含以下要素，并保持条理清晰：

1. **本章核心情节**：发生了什么主要事件？主角的目标是否达成？
2. **关键信息与伏笔**：揭示了哪些重要信息？埋下了什么伏笔？
3. **角色状态变更**：主角及关键配角的状态、位置、资源、人际关系有何变化？
4. **不可逆事实**：本章确立了哪些不可更改的设定或事实（如死亡、物品消耗、地点毁灭等）？
5. **下一章承接锚点**：故事在何处戛然而止？下一章应从哪里接续？

正文内容：
{content[:15000]} ... (内容过长已截断)

请输出 Markdown 格式的摘要，字数控制在 {max_chars} 字以内。
"""
    try:
        response = llm.call([{"role": "user", "content": prompt}])
        return _clamp(response, max_chars)
    except Exception as e:
        return ""


def _count_body_chars(text: str) -> int:
    """统计正文有效字数（排除标题、空白、摘要块）"""
    raw = (text or "").strip()
    raw, _ = _extract_summary_block(raw)
    raw = re.sub(r"^#.*\n?", "", raw).strip()
    raw = re.sub(r"\s+", "", raw)
    return len(raw)


def _expand_chapter_to_min_length(agent, chapter_number: int, body_text: str, min_chars: int, max_chars: int) -> str:
    """
    扩写章节正文到最小字数要求
    约束：不改变剧情、不新增人物/设定、只补充细节
    """
    current_len = _count_body_chars(body_text)
    if current_len >= min_chars:
        return body_text

    expand_task = Task(
        description=(
            f"请将以下章节正文扩写到至少{min_chars}字（不含标题），但不超过{max_chars}字。\n"
            "硬性约束：\n"
            "1. 不改变既有剧情事件的先后顺序与结果；\n"
            "2. 不新增关键人物、不新增核心设定、不跳时间线；\n"
            "3. 只能通过补充动作细节、环境感官、对话、心理活动、过渡段来扩写；\n"
            "4. 保持原文文风与视角一致；\n"
            "5. 正文中不要包含任何情节分段标题（##/###/一、二、三等）；\n"
            "6. 输出必须以 Markdown 一级标题开头：# 第N章 章节名。\n\n"
            f"【当前正文（偏短，需扩写）】\n{body_text}"
        ),
        agent=agent,
        expected_output="扩写后的完整章节正文（含 # 第N章 标题）",
    )
    expand_crew = Crew(
        agents=[agent],
        tasks=[expand_task],
        process=Process.sequential,
        verbose=False,
        memory=False,
    )
    expanded = str(expand_crew.kickoff())
    return expanded


def _sanitize_final_content(content: str, chapter_number: int) -> str:
    """
    清理最终章节内容
    - 统一换行符
    - 移除摘要块
    - 移除多余的分段标题
    - 确保以一级标题开头
    """
    text = (content or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text:
        return f"# 第{chapter_number}章\n"

    text, _ = _extract_summary_block(text)
    lines = text.split("\n")
    title = ""
    body_lines = []

    for line in lines:
        stripped = line.strip()
        if not title and stripped.startswith("# "):
            title = stripped
            continue
        if re.match(r"^#{2,}\s+", stripped):
            continue
        if re.match(r"^[一二三四五六七八九十百千]+、\s*$", stripped):
            continue
        body_lines.append(line.rstrip())

    if not title:
        title = f"# 第{chapter_number}章"
    cleaned_body = "\n".join(body_lines).strip()
    cleaned_body = re.sub(r"\n{3,}", "\n\n", cleaned_body)
    if cleaned_body:
        return f"{title}\n\n{cleaned_body}\n"
    return f"{title}\n"


def _chapter_body_without_title(text: str) -> str:
    """移除章节标题，返回纯正文"""
    raw = (text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    raw, _ = _extract_summary_block(raw)
    raw = re.sub(r"^#.*\n?", "", raw).lstrip()
    return raw


def _chapter_opening_for_similarity(text: str, max_chars: int = 520) -> str:
    """提取章节开头片段，用于相似度检测"""
    body = _chapter_body_without_title(text)
    if not body:
        return ""
    parts = [p.strip() for p in body.split("\n\n") if p.strip()]
    if not parts:
        return ""
    snippet = ""
    for p in parts:
        if not snippet:
            snippet = p
        elif len(snippet) < max_chars:
            snippet = snippet + "\n\n" + p
        if len(snippet) >= max_chars:
            break
    return snippet[:max_chars]


def _chapter_tail_for_context(text: str, max_chars: int = 1200) -> str:
    """提取章节末尾片段，用于承接上下文"""
    body = _chapter_body_without_title(text)
    if not body:
        return ""
    body = body.strip()
    if len(body) <= max_chars:
        return body
    return body[-max_chars:]


def _normalize_similarity_text(text: str) -> str:
    """标准化文本用于相似度比较（移除空白和引号）"""
    t = (text or "").strip()
    if not t:
        return ""
    t = re.sub(r"\s+", "", t)
    t = re.sub(r"[""]\"''']", "", t)
    return t


def _similarity_ratio(a: str, b: str) -> float:
    """计算两段文本的相似度（0.0-1.0）"""
    na = _normalize_similarity_text(a)
    nb = _normalize_similarity_text(b)
    if not na or not nb:
        return 0.0
    return SequenceMatcher(None, na, nb).ratio()


def _split_opening_and_rest(body: str) -> tuple[str, str]:
    """将正文分割为开头部分和剩余部分"""
    parts = [p.strip() for p in (body or "").split("\n\n") if p.strip()]
    if not parts:
        return "", ""
    opening_parts = []
    acc = 0
    for p in parts:
        opening_parts.append(p)
        acc += len(p)
        if len(opening_parts) >= 2 and acc >= 240:
            break
        if len(opening_parts) >= 3:
            break
    opening = "\n\n".join(opening_parts).strip()
    rest = "\n\n".join(parts[len(opening_parts):]).strip()
    return opening, rest


def _rewrite_opening_via_llm(
    llm,
    previous_opening: str,
    previous_tail: str,
    current_opening: str,
    next_context: str,
) -> str:
    """
    使用 LLM 改写章节开头
    目的：避免与上一章开头雷同，同时保持剧情连贯
    """
    prompt = f"""
你是中文网文主编。请将"当前章开头"改写为一个明显不同、但完全连贯的开场。

硬性要求：
1) 只输出改写后的开头正文，不要输出标题，不要输出解释。
2) 字数控制在 220–420 字。
3) 必须从上一章末尾状态直接接续，用动作/对白/冲突起笔，立刻推进剧情。
4) 禁止复述前情，禁止写"回顾/复盘/前情提要/上一章/上回/回想/不久前/转眼/与此同时"等承接句。
5) 禁止使用通用开场白（如天色/夜色/时间飞逝/几日后/一夜之间）。
6) 不改变当前章既定事件顺序与结果，只改开头表达方式，并保证能自然衔接后续正文。

【上一章开头（用于避重）】
{previous_opening}

【上一章末尾原文片段（必须承接）】
{previous_tail}

【当前章开头（需改写）】
{current_opening}

【当前章后续片段（用于衔接）】
{next_context}
"""
    try:
        rewritten = str(llm.call([{"role": "user", "content": prompt}]) or "").strip()
        rewritten = re.sub(r"^#.*\n?", "", rewritten).strip()
        rewritten = re.sub(r"\[SUMMARY_BEGIN\][\s\S]*?\[SUMMARY_END\]", "", rewritten).strip()
        return rewritten
    except Exception:
        return ""


def _dedupe_opening_if_needed(
    chapter_text: str,
    previous_chapter_text: str,
    llm,
    log_callback=None,
) -> str:
    """
    检测并处理章节开头重复问题
    若当前章开头与上一章相似度超过阈值，则调用 LLM 改写
    """
    if not chapter_text.strip() or not previous_chapter_text.strip():
        return chapter_text

    title_line = ""
    lines = chapter_text.replace("\r\n", "\n").replace("\r", "\n").strip().split("\n")
    if lines and lines[0].strip().startswith("# "):
        title_line = lines[0].strip()
        body = "\n".join(lines[1:]).lstrip("\n")
    else:
        body = chapter_text.strip()

    opening, rest = _split_opening_and_rest(body)
    prev_opening = _chapter_opening_for_similarity(previous_chapter_text, max_chars=520)
    ratio = _similarity_ratio(opening[:520], prev_opening[:520])
    if ratio < float(os.getenv("CHAPTER_OPENING_SIMILARITY_THRESHOLD", "0.74")):
        return chapter_text

    next_context = rest[:900].strip()
    prev_tail = _chapter_tail_for_context(previous_chapter_text, max_chars=1200)
    rewritten = _rewrite_opening_via_llm(
        llm=llm,
        previous_opening=prev_opening[:520],
        previous_tail=prev_tail,
        current_opening=opening[:520],
        next_context=next_context,
    )
    if not rewritten:
        return chapter_text

    new_body = (rewritten.strip() + ("\n\n" + rest if rest else "")).strip() + "\n"
    merged = (title_line + "\n\n" + new_body).strip() + "\n" if title_line else new_body
    if log_callback:
        try:
            log_callback("✍️ 已检测到开头重复，自动改写开场以避免与上一章雷同", status="info")
        except Exception:
            pass
    return merged


def _build_canon_ledger(chapter_number: int, content: str, max_chars: int = 1600) -> str:
    """
    构建章节事实台账
    包含：不可逆事实、角色状态变更、资源变更、伏笔状态、承接锚点
    用于后续章节保持一致性
    """
    body = re.sub(r"^#.*\n?", "", (content or "").strip()).strip()
    body = re.sub(r"\n{2,}", "\n", body)
    sentences = _extract_sentences(body)
    facts = "；".join(sentences[:3]) if sentences else ""
    state_delta = "；".join(sentences[3:6]) if len(sentences) > 3 else (sentences[-1] if sentences else "")
    resources = _extract_resource_mentions(body)
    hooks = [s for s in sentences[-5:] if "？" in s or "..." in s or "……" in s]
    anchors = sentences[-3:] if len(sentences) >= 3 else sentences
    canon_text = (
        f"# 第{chapter_number}章事实台账\n\n"
        f"## 不可逆事实\n- {facts or '待补充'}\n\n"
        f"## 角色状态变更\n- {state_delta or '待补充'}\n\n"
        f"## 资源与能力变更\n"
        + ("\n".join([f"- {x}" for x in resources]) if resources else "- 无显著资源变更")
        + "\n\n## 伏笔状态流转\n"
        + ("\n".join([f"- {x}" for x in hooks[:3]]) if hooks else "- 新增/回收信息待下一章确认")
        + "\n\n## 下一章必须承接锚点\n"
        + ("\n".join([f"- {x}" for x in anchors]) if anchors else "- 承接上一章末状态")
    )
    return _clamp(canon_text, max_chars)


def _task_output_text(task) -> str:
    """从 CrewAI Task 对象中提取输出文本"""
    output = getattr(task, "output", None)
    if not output:
        return ""
    if hasattr(output, "raw"):
        return str(output.raw or "")
    return str(output)


def ensure_story_bible(project_name: str, outline: str, chapter_number: int = 0, recent_canon_text: str = "", log_callback=None) -> str:
    """
    生成/更新项目的「剧情圣经」

    剧情圣经是一份全局设定文档，包含：
    - 题材基调、世界观规则
    - 主线目标与阶段推进
    - 核心人物卡、关系网
    - 爽点配方、伏笔表、写作约束

    目的：避免每章都传入完整大纲，减少 token 消耗和 embedding 压力
    触发条件：大纲变化、首次生成、或每隔 N 章增量更新
    """
    config = load_project_config(project_name)
    current_hash = _outline_hash(outline or "")
    existing_bible = load_story_bible(project_name).strip()

    refresh_every = int(os.getenv("STORY_BIBLE_REFRESH_EVERY_CHAPTERS", "5"))
    last_sync_chapter = int(config.get("story_bible_last_sync_chapter") or 0)
    need_incremental = (
        bool(existing_bible)
        and bool(recent_canon_text.strip())
        and chapter_number > 0
        and chapter_number % refresh_every == 0
        and chapter_number > last_sync_chapter
    )

    if existing_bible and config.get("outline_hash") == current_hash and not need_incremental:
        return existing_bible

    keys = load_api_keys()
    api_key = (keys.get("DASHSCOPE_API_KEY") or "").strip()
    if not api_key:
        return existing_bible

    if log_callback:
        log_callback("正在提炼剧情圣经（用于减少每章重复传入完整大纲）...")

    qwen_llm = LLM(
        model="openai/qwen-plus",
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    bible_agent = Agent(
        role="剧情圣经提炼师",
        goal="将大纲提炼成稳定、可复用的全局设定资产，便于后续章节保持一致性",
        backstory="你擅长从长大纲中抽取关键信息，形成精简且结构化的设定文档。",
        llm=qwen_llm,
        verbose=False,
        allow_delegation=False,
    )

    if need_incremental:
        bible_desc = (
            "请基于【现有剧情圣经】与【最近章节事实台账】做增量更新，"
            "只更新受影响的小节，不要重写无关内容。\n\n"
            "更新优先级：\n"
            "1) 核心人物卡（当前状态）\n"
            "2) 伏笔与回收表（状态流转）\n"
            "3) 世界观规则新增与变更\n\n"
            f"【现有剧情圣经】\n{existing_bible[:5000]}\n\n"
            f"【最近章节事实台账】\n{recent_canon_text[:3000]}\n\n"
            f"【用户大纲】\n{outline[:3000]}"
        )
    else:
        bible_desc = (
            "请将以下【用户大纲】提炼为一份中文网文可用的《剧情圣经》Markdown，"
            "要求结构清晰、可复用、尽量精简但信息完整。\n\n"
            "必须包含以下小节：\n"
            "1) 题材与基调（1-3句）\n"
            "2) 世界观规则（要点列表）\n"
            "3) 主线目标与阶段推进（要点列表）\n"
            "4) 核心人物卡（主角/关键配角，姓名、身份、动机、能力/资源、雷区）\n"
            "5) 关键关系网（简表）\n"
            "6) 爽点配方（本书通用爽点类型与节奏建议）\n"
            "7) 伏笔与回收表（表格：伏笔｜埋点章节｜回收章节/条件｜当前状态）\n"
            "8) 写作约束（第一人称/第三人称、文风、禁忌等）\n\n"
            f"【用户大纲】\n{outline}"
        )

    bible_task = Task(
        description=bible_desc,
        agent=bible_agent,
        expected_output="《剧情圣经》Markdown 文档",
    )

    bible_crew = Crew(
        agents=[bible_agent],
        tasks=[bible_task],
        process=Process.sequential,
        verbose=False,
        memory=False,
    )
    bible_result = str(bible_crew.kickoff())
    save_story_bible(project_name, bible_result)

    config["outline_hash"] = current_hash
    if chapter_number > 0:
        config["story_bible_last_sync_chapter"] = int(chapter_number)
    save_project_config(project_name, config)
    return bible_result


def _resolve_writing_style(project_name: str) -> str:
    """读取并标准化文风值（standard/tomato），避免脏配置"""
    project_config = load_project_config(project_name)
    writing_style = str(project_config.get("writing_style", "standard") or "standard").lower()
    if writing_style not in {"standard", "tomato"}:
        return "standard"
    return writing_style


def _build_previous_context(project_name: str, chapter_number: int) -> tuple[str, str]:
    """
    构建上一章承接输入
    返回：(previous_context 用于任务描述, previous_chapter_text 全文用于去重)
    """
    previous_summary = load_chapter_summary(project_name, max(1, chapter_number - 1)) if chapter_number > 1 else ""
    previous_chapter_text = ""
    previous_tail = ""
    if chapter_number > 1:
        previous_chapter_text = load_chapter(project_name, f"第{chapter_number - 1}章.md")
        previous_tail = _chapter_tail_for_context(previous_chapter_text, max_chars=1200)

    previous_context = ""
    if previous_summary:
        previous_context += f"【上一章摘要（仅供查阅，禁止复述前情）】\n{previous_summary.strip()}\n"
    if previous_tail:
        if previous_context:
            previous_context += "\n"
        previous_context += f"【上一章末尾原文片段（必须从这里接续）】\n{previous_tail.strip()}\n"
    return previous_context, previous_chapter_text


def generate_chapter(project_name, outline, chapter_number, log_callback=None):
    """
    核心函数：生成单个章节

    流程：
    1. 创建 Agent 团队（大纲优化师、世界观守护者、主写手、审校专家）
    2. 加载上下文（上一章摘要、事实台账、剧情圣经）
    3. 执行 CrewAI 流水线
    4. 后处理（扩写、去重、保存摘要和台账）

    参数：
    - project_name: 项目名称
    - outline: 故事大纲
    - chapter_number: 章节序号
    - log_callback: 日志回调函数

    返回：生成的章节内容
    """
    run_logs = []
    autosaved_from_finalizer = False
    shared_state = {
        "finalizer_output": "",
        "last_update": time.time()
    }

    project_storage_dir = os.path.join(workspace_manager.get_projects_dir(), project_name, ".crewai")
    os.makedirs(project_storage_dir, exist_ok=True)
    os.environ["CREWAI_STORAGE_DIR"] = os.path.abspath(project_storage_dir)

    log_queue = queue.Queue()

    def safe_log(message, status="info"):
        """线程安全的日志记录函数"""
        log_queue.put((message, status))

    def step_callback(step_output):
        """
        CrewAI 步骤回调 - 实时显示 Agent 思考过程
        同时实现终审稿的提前保存，防止最后一步挂起导致内容丢失
        """
        nonlocal autosaved_from_finalizer
        if log_callback:
            try:
                timestamp = datetime.now().strftime("%H:%M:%S")
                if isinstance(step_output, dict):
                    agent_text = str(step_output.get("agent", ""))
                    candidate = ""
                    for key in ("output", "final_output", "result", "tool_output"):
                        value = step_output.get(key)
                        if hasattr(value, "raw"):
                            value = value.raw
                        text_value = str(value or "")
                        if len(text_value) > len(candidate):
                            candidate = text_value

                    if "终极审校专家" in agent_text and len(candidate) > len(shared_state["finalizer_output"]):
                        shared_state["finalizer_output"] = candidate
                        shared_state["last_update"] = time.time()

                    if (
                        not autosaved_from_finalizer
                        and "终极审校专家" in agent_text
                        and len(candidate.strip()) > 800
                    ):
                        candidate_to_save = _sanitize_final_content(candidate, int(chapter_number))
                        save_chapter(project_name, chapter_number, candidate_to_save)
                        autosaved_from_finalizer = True
                        safe_log(f"[{timestamp}] 💾 已提前保存终审稿，避免意外丢失", status="success")

                if isinstance(step_output, dict):
                    agent = step_output.get("agent", "Agent")
                    thought = str(step_output.get("thought", ""))
                    tool_output = str(step_output.get("tool_output", ""))

                    if thought:
                        safe_log(f"[{timestamp}] 🤖 {agent} 思考中...", status="info")
                        try:
                            print(f"\n[{timestamp}] {agent}: {thought[:200]}...")
                        except:
                            pass
                    if tool_output:
                        safe_log(f"[{timestamp}] 🛠️ 调用工具...", status="info")
                elif hasattr(step_output, "agent"):
                     agent = getattr(step_output, "agent", "Agent")
                     safe_log(f"[{timestamp}] ⚡ {agent} 正在执行...", status="info")
                else:
                    safe_log(f"[{timestamp}] ⚡ 系统正在处理...", status="info")
            except Exception:
                pass

    try:
        if log_callback:
            message = "开始生成第{}章...".format(chapter_number)
            log_callback(message)
            run_logs.append(f"[{datetime.now().isoformat()}] {message}")

        agents = create_agents()
        previous_context, previous_chapter_text = _build_previous_context(project_name, int(chapter_number))
        recent_canon_entries = load_recent_canon_entries(project_name, limit=3)
        recent_canon_context = "\n\n".join(recent_canon_entries).strip()
        story_bible = ensure_story_bible(
            project_name,
            outline,
            chapter_number=int(chapter_number),
            recent_canon_text="\n\n".join(load_recent_canon_entries(project_name, limit=5)),
            log_callback=log_callback,
        )
        writing_style = _resolve_writing_style(project_name)

        embedder = None
        default_memory_enabled = False
        if log_callback:
            log_callback("ℹ️ CrewAI Memory 已禁用（使用剧情圣经+摘要+台账链路）", status="info")

        def _run_pipeline(compact_mode: bool, memory_enabled: bool):
            """
            执行章节生成流水线

            compact_mode: 精简模式（失败时的降级方案）
            memory_enabled: 是否启用 CrewAI 记忆功能
            """
            prev_payload = previous_context
            canon_payload = recent_canon_context
            bible_payload = story_bible
            if writing_style == "tomato":
                prev_payload = _build_tomato_recap(project_name, int(chapter_number)) or previous_context
                canon_payload = _tomato_compact_context(recent_canon_context, 1200)
                bible_payload = _tomato_compact_context(story_bible, 3200)
            tasks = create_tasks(
                agents,
                bible_payload,
                outline,
                chapter_number,
                previous_chapter_content=prev_payload,
                canon_context=canon_payload,
                compact_mode=compact_mode,
                writing_style=writing_style,
            )
            mode_label = "精简链路" if compact_mode else "完整链路"
            if log_callback:
                message = f"CrewAI 已初始化，开始执行{mode_label}（{len(tasks)}个任务）..."
                log_callback(message)
                run_logs.append(f"[{datetime.now().isoformat()}] {message}")

            crew = Crew(
                agents=agents,
                tasks=tasks,
                process=Process.sequential,
                verbose=False,
                memory=memory_enabled,
                embedder=embedder if memory_enabled else None,
                step_callback=step_callback,
            )
            if log_callback:
                log_callback("💡 Agent 开始思考与协作... (这可能需要几分钟)")
            kickoff_timeout = int(os.getenv("CREW_KICKOFF_TIMEOUT_SEC", "1500"))
            recovered_output = ""
            result = None
            future_done = False
            executor = ThreadPoolExecutor(max_workers=1)
            future = executor.submit(crew.kickoff)
            deadline = time.time() + kickoff_timeout
            try:
                while True:
                    while not log_queue.empty():
                        try:
                            msg, status = log_queue.get_nowait()
                            if log_callback:
                                log_callback(msg, status=status)
                        except queue.Empty:
                            break

                    if future.done():
                        result = future.result()
                        future_done = True
                        break

                    if len(shared_state["finalizer_output"]) > 800:
                        if time.time() - shared_state["last_update"] > 45:
                            recovered_output = shared_state["finalizer_output"]
                            if log_callback:
                                safe_log(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ 检测到终审专家似乎卡住，已从最后一次输出中恢复内容", status="warning")
                            break

                    if tasks:
                        candidate = _task_output_text(tasks[-1]).strip()
                        if len(candidate) > 1200:
                            recovered_output = candidate
                            break

                    if time.time() >= deadline:
                        if len(shared_state["finalizer_output"]) > 500:
                             recovered_output = shared_state["finalizer_output"]
                             break

                        if tasks:
                            candidate = _task_output_text(tasks[-1]).strip()
                            if candidate:
                                recovered_output = candidate
                                break
                        raise TimeoutError("Crew kickoff 超时，且未拿到可保存输出")
                    time.sleep(1)
            finally:
                executor.shutdown(wait=False, cancel_futures=True)

            while not log_queue.empty():
                try:
                    msg, status = log_queue.get_nowait()
                    if log_callback:
                        log_callback(msg, status=status)
                except queue.Empty:
                    break

            if future_done:
                for i, task in enumerate(tasks):
                    if compact_mode:
                        agent_name = getattr(task.agent, "role", f"Agent-{i+1}")
                    else:
                        all_roles = ["大纲动态优化师", "人物与世界观守护者", "章节主写手", "终极审校专家"]
                        agent_name = all_roles[i] if i < len(all_roles) else f"Agent-{i+1}"
                    if log_callback:
                        message = f"✅ {agent_name} 任务已在后台完成"
                        log_callback(message)
                        run_logs.append(f"[{datetime.now().isoformat()}] {message}")
            elif recovered_output and log_callback:
                message = "已检测到终审稿输出，跳过尾部阻塞并继续保存"
                log_callback(message, status="warning")
                run_logs.append(f"[{datetime.now().isoformat()}] WARNING: {message}")

            if recovered_output:
                return recovered_output
            if tasks:
                final_output = _task_output_text(tasks[-1]).strip()
                if final_output:
                    return final_output
            return str(result)

        try:
            result = _run_pipeline(compact_mode=False, memory_enabled=default_memory_enabled)
        except Exception as first_error:
            if log_callback:
                message = f"完整链路失败，切换精简链路重试: {str(first_error)}"
                log_callback(message, status="warning")
                run_logs.append(f"[{datetime.now().isoformat()}] WARNING: {message}")
            result = _run_pipeline(compact_mode=True, memory_enabled=False)
            if log_callback:
                message = "精简链路重试成功，已继续完成本章生成"
                log_callback(message, status="success")
                run_logs.append(f"[{datetime.now().isoformat()}] {message}")

        if log_callback:
            message = "章节生成完成，正在保存..."
            log_callback(message)
            run_logs.append(f"[{datetime.now().isoformat()}] {message}")

        raw_result = str(result)
        body_without_summary, summary_block = _extract_summary_block(raw_result)
        final_content = _sanitize_final_content(body_without_summary, int(chapter_number))

        if writing_style == "tomato":
            min_chars = int(os.getenv("CHAPTER_MIN_CHARS_TOMATO", "2100"))
            max_chars = int(os.getenv("CHAPTER_MAX_CHARS_TOMATO", "2600"))
        else:
            min_chars = int(os.getenv("CHAPTER_MIN_CHARS", "3500"))
            max_chars = int(os.getenv("CHAPTER_MAX_CHARS", "5500"))
        if max_chars < min_chars:
            max_chars = min_chars + 200
        current_len = _count_body_chars(final_content)
        if current_len < min_chars:
            if log_callback:
                log_callback(f"⚠️ 正文长度不足（{current_len}字 < {min_chars}字），正在自动扩写补足...", status='warning')
            expanded_once = _expand_chapter_to_min_length(agents[3], int(chapter_number), final_content, min_chars, max_chars)
            final_content = _sanitize_final_content(expanded_once, int(chapter_number))
            current_len = _count_body_chars(final_content)
            if current_len < min_chars:
                expanded_twice = _expand_chapter_to_min_length(agents[3], int(chapter_number), final_content, min_chars, max_chars)
                final_content = _sanitize_final_content(expanded_twice, int(chapter_number))
                current_len = _count_body_chars(final_content)
            if log_callback:
                log_callback(f"✅ 扩写完成，正文长度：{current_len}字", status='success')

        dedup_enabled = os.getenv("CHAPTER_OPENING_DEDUP", "true").lower() != "false"
        if dedup_enabled and int(chapter_number) > 1 and previous_chapter_text:
            target_llm = agents[3].llm if len(agents) > 3 else agents[0].llm
            final_content = _dedupe_opening_if_needed(final_content, previous_chapter_text, target_llm, log_callback=log_callback)
            current_len = _count_body_chars(final_content)
            if current_len < min_chars:
                expanded_once = _expand_chapter_to_min_length(agents[3], int(chapter_number), final_content, min_chars, max_chars)
                final_content = _sanitize_final_content(expanded_once, int(chapter_number))

        save_chapter(project_name, chapter_number, final_content)
        save_canon_entry(project_name, chapter_number, _build_canon_ledger(int(chapter_number), final_content))
        summary_max_chars = int(os.getenv("CHAPTER_SUMMARY_MAX_CHARS", "900"))
        summary_content = _normalize_summary(int(chapter_number), summary_block, max_chars=summary_max_chars)

        if not summary_content:
            if log_callback:
                log_callback("📝 正在使用 LLM 生成高质量章节摘要...", status="info")
            target_llm = agents[3].llm if len(agents) > 3 else agents[0].llm
            summary_content = _generate_summary_via_llm(final_content, target_llm, max_chars=summary_max_chars)

        if not summary_content:
            summary_content = _build_chapter_summary(chapter_number, final_content, max_chars=summary_max_chars)

        save_chapter_summary(project_name, chapter_number, summary_content, max_chars=summary_max_chars)

        if log_callback:
            message = "第{}章保存成功！".format(chapter_number)
            log_callback(message, status="success")
            run_logs.append(f"[{datetime.now().isoformat()}] {message}")

        save_run_log(project_name, "\n".join(run_logs))

        return result
    except Exception as e:
        error_message = "生成过程出错: {}".format(str(e))
        if log_callback:
            log_callback(error_message, status="error")
            run_logs.append(f"[{datetime.now().isoformat()}] ERROR: {error_message}")
        save_run_log(project_name, "\n".join(run_logs))
        raise


def generate_single_chapter(project_name, outline, chapter_number, log_callback=None):
    """生成单个章节（generate_chapter 的别名）"""
    return generate_chapter(project_name, outline, chapter_number, log_callback)


def generate_multiple_chapters(project_name, outline, start_chapter, end_chapter, log_callback=None):
    """
    批量生成多个章节
    循环调用 generate_chapter，保存完整运行日志
    """
    results = []
    run_logs = []

    for chapter_num in range(start_chapter, end_chapter + 1):
        try:
            chapter_logs = []
            if log_callback:
                message = "=" * 60
                log_callback(message)
                chapter_logs.append(f"[{datetime.now().isoformat()}] {message}")

                message = "开始生成第{}章".format(chapter_num)
                log_callback(message)
                chapter_logs.append(f"[{datetime.now().isoformat()}] {message}")

                message = "=" * 60
                log_callback(message)
                chapter_logs.append(f"[{datetime.now().isoformat()}] {message}")

            result = generate_chapter(project_name, outline, chapter_num, log_callback)
            results.append(result)

            run_logs.extend(chapter_logs)

        except Exception as e:
            error_message = "第{}章生成失败: {}".format(chapter_num, str(e))
            if log_callback:
                log_callback(error_message, status="error")
                run_logs.append(f"[{datetime.now().isoformat()}] ERROR: {error_message}")
            continue

    save_run_log(project_name, "\n".join(run_logs))

    return results
