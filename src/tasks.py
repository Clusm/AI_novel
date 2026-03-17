from crewai import Task
import os
import re

# CrewAI 记忆检索时会把「任务 description + context」整段作为 query 发给 Embedding API。
# 因此需要控制 description 的长度，避免 embedding 查询超限。
STORY_BIBLE_MAX_CHARS = 2600
OUTLINE_EXCERPT_MAX_CHARS = 1200


def _clamp_with_suffix(text: str, max_chars: int, suffix: str) -> str:
    if max_chars <= 0:
        return ""
    if len(text) <= max_chars:
        return text
    if len(suffix) >= max_chars:
        return suffix[:max_chars]
    return text[: max_chars - len(suffix)] + suffix


def _extract_outline_excerpt(user_outline: str, current_chapter: int, max_chars: int) -> tuple[str, bool]:
    """提取大纲片段，并返回是否为详细细纲"""
    text = (user_outline or "").strip()
    if not text:
        return "", False

    # 尝试精准匹配 "#### 第N章" 或 "**第N章" 这种大纲标题
    chapter_pattern = rf"(?m)^#{2,4}\s*(\*{0,2}第\s*{current_chapter}\s*章[^\n]*)"
    match = re.search(chapter_pattern, text)
    
    chapter_content = ""
    is_detailed = False
    
    if match:
        start_idx = match.start()
        # 找下一章的标题作为结束
        next_chapter_pattern = rf"(?m)^#{2,4}\s*(\*{0,2}第\s*{current_chapter + 1}\s*章)"
        next_match = re.search(next_chapter_pattern, text[start_idx:])
        
        if next_match:
            end_idx = start_idx + next_match.start()
            chapter_content = text[start_idx:end_idx].strip()
        else:
            # 如果找不到下一章，可能是最后一章，或者是分卷标题阻隔
            # 尝试找下一个分卷标题或大标题
            next_section = re.search(r"(?m)^#{1,3}\s+", text[start_idx + len(match.group(0)):])
            if next_section:
                 end_idx = start_idx + len(match.group(0)) + next_section.start()
                 chapter_content = text[start_idx:end_idx].strip()
            else:
                 chapter_content = text[start_idx:].strip()
    
    # 如果没找到精准章节，回退到模糊搜索（但不认为是详细细纲）
    if not chapter_content:
        return _extract_outline_excerpt_legacy(text, current_chapter, max_chars), False

    # 判断提取内容是否足够详细（例如 > 50字）
    if len(chapter_content) > 50:
        is_detailed = True
        # 如果太长，适当截断，但保留核心
        if len(chapter_content) > max_chars:
             chapter_content = _clamp_with_suffix(chapter_content, max_chars, "…")
    
    return chapter_content, is_detailed

def _extract_outline_excerpt_legacy(text: str, current_chapter: int, max_chars: int) -> str:
    """旧的提取逻辑，用于模糊匹配"""
    header_budget = min(600, max_chars // 2)
    sep = "\n\n【章节相关片段】\n"
    suffix = "…（大纲摘录已截断）"
    
    # ... (原有逻辑简化或直接复用)
    # 为节省篇幅，这里简化处理，实际可以直接保留原有逻辑
    loose_patterns = [
            rf"第\s*{int(current_chapter)}\s*章",
            rf"章节\s*{int(current_chapter)}\b",
            rf"Chapter\s*{int(current_chapter)}\b",
    ]
    chapter_slice = ""
    for pat in loose_patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if not m:
            continue
        start = max(0, m.start() - 240)
        end = min(len(text), m.end() + 1400)
        chapter_slice = text[start:end].strip()
        break
        
    if not chapter_slice:
        return _clamp_with_suffix(text, max_chars, suffix)
        
    return _clamp_with_suffix(chapter_slice, max_chars, suffix)


def create_tasks(
    agents,
    story_bible: str,
    user_outline: str,
    current_chapter=1,
    previous_chapter_content="",
    canon_context="",
    compact_mode=False,
    writing_style="standard",
):
    """
    为6个Agent创建任务
    writing_style: 'standard' (默认/传统) 或 'tomato' (番茄/新媒体/快节奏)
    """
    tasks = []

    bible_for_desc = (story_bible or "").strip()
    if len(bible_for_desc) > STORY_BIBLE_MAX_CHARS:
        bible_for_desc = bible_for_desc[:STORY_BIBLE_MAX_CHARS] + "…（剧情圣经已截断）"

    outline_excerpt, is_detailed_outline = _extract_outline_excerpt(user_outline, current_chapter, OUTLINE_EXCERPT_MAX_CHARS)

    # 上一章承接信息（用于保持连贯性）
    prev_info = ""
    if previous_chapter_content:
        prev_info = f"\n\n【上一章承接信息（只用于无缝接续，禁止复述前情）】\n{previous_chapter_content.strip()}"
    
    base_context = ""
    if bible_for_desc:
        base_context += f"\n\n【剧情圣经（摘要）】\n{bible_for_desc}"
    if canon_context:
        base_context += f"\n\n【最近章节事实台账（强连续性输入）】\n{canon_context[:1800]}"
    
    # 风格化指令注入
    style_instruction = ""
    outline_style_instruction = ""
    guardian_style_instruction = ""
    writer_style_instruction = ""
    finalizer_style_instruction = ""
    if writing_style == "tomato":
        min_chars = int(os.getenv("CHAPTER_MIN_CHARS_TOMATO", "2100"))
        max_chars = int(os.getenv("CHAPTER_MAX_CHARS_TOMATO", "2600"))
    else:
        min_chars = int(os.getenv("CHAPTER_MIN_CHARS", "3500"))
        max_chars = int(os.getenv("CHAPTER_MAX_CHARS", "5500"))
    if max_chars < min_chars:
        max_chars = min_chars + 200
    if writing_style == "tomato":
        style_instruction = (
            "\n\n【文风要求：番茄/新媒体/快节奏模式】\n"
            "1. 节奏极快：开章100字内必须出现冲突/刺激点；拒绝慢热铺垫。\n"
            "2. 爽点密度：每500字至少一个情绪点（震惊/打脸/危机/反转/奖励）。\n"
            "3. 语言克制：以动作与对白推动；少形容词、少抒情长段；拒绝谜语人、拒绝堆设定解释。\n"
            "4. 结构适配：短句短段，单句成段；每段尽量不超过80字，利于手机阅读。\n"
            "5. 断章钩子：章末必须留明确悬念或下一步行动目标。\n"
        )
        outline_style_instruction = (
            "\n\n【提纲输出要求（番茄模式加严）】\n"
            "1) 给出“开头钩子”（1-3句，直接冲突/对白起笔）；\n"
            "2) 给出“爽点节奏表”，按每500字一个节点列出：触发点/情绪点/推进结果；\n"
            "3) 给出“章末断章点”（一句话）；\n"
        )
        guardian_style_instruction = (
            "\n\n【守护者输出要求（番茄模式加严）】\n"
            "1) 输出极简清单：每条不超过20字；\n"
            "2) 标出本章关键冲突点与情绪锚点；\n"
            "3) 不要展开长篇设定解释。\n"
        )
        writer_style_instruction = (
            "\n\n【写作执行要求（番茄模式加严）】\n"
            "1) 章首用动作/对白/冲突起笔；\n"
            "2) 每300-600字推进一次冲突或信息增量；\n"
            "3) 多对白少独白，段落短；\n"
            "4) 章末留钩子（危机/奖励/转折/任务）。\n"
        )
        finalizer_style_instruction = (
            "\n\n【终审调整重点（番茄模式加严）】\n"
            "1) 删除拖节奏的环境/抒情长段；\n"
            "2) 合并冗余解释，把信息塞进对白与动作；\n"
            "3) 强化章首钩子与章末悬念；\n"
            "4) 保持短段阅读体验。\n"
        )
    else:
        style_instruction = (
            "\n\n【文风要求：传统/正剧模式】\n"
            "1. 节奏稳健：注重逻辑铺垫与草蛇灰线，情节推进要有合理性。\n"
            "2. 沉浸体验：适当的环境渲染与心理刻画，增强代入感。\n"
            "3. 逻辑严密：世界观与战力体系要自洽，拒绝无脑爽文套路。\n"
        )
        outline_style_instruction = ""
        guardian_style_instruction = ""
        writer_style_instruction = ""
        finalizer_style_instruction = ""

    # 1. 大纲动态优化师任务 (根据是否已有详细大纲决定是否跳过)
    outline_source = "大纲优化师生成的提纲"
    
    if is_detailed_outline:
        # 已有详细大纲，跳过Agent 1
        base_context += f"\n\n【本章详细细纲（已锁定）】\n{outline_excerpt}"
        outline_source = "上述【本章详细细纲】"
        # 不添加 task1
    else:
        # 没有详细大纲，需要AI生成
        if outline_excerpt:
            base_context += f"\n\n【用户大纲（摘录）】\n{outline_excerpt}"
            
        task1 = Task(
            description=(
                f"请基于以下信息，为第{current_chapter}章生成详细提纲。\n"
                f"要求：\n"
                f"1. 包含章节目标、主要情节、伏笔安排。\n"
                f"2. 【重要】在每个关键情节段落后，直接标注本段的【爽点类型】与【期待感来源】（例如：#爽点：扮猪吃虎；#期待：反派震惊）。\n"
                f"{style_instruction}"
                f"{outline_style_instruction}"
                f"{base_context}{prev_info}"
            ),
            agent=agents[0],
            expected_output="详细的章节提纲，包含爽点标注与伏笔安排"
        )
        tasks.append(task1)

    # 2. 人物与世界观守护者任务
    task2 = Task(
        description=(
            f"基于{outline_source}，提取本章出场的主要人物与关键设定，生成一份简明的人物卡与设定检查表。\n"
            f"重点关注：人物动机、性格特征、能力限制以及本章涉及的核心世界观规则。\n"
            f"请直接输出 Markdown 内容，无需解释思考过程。\n{prev_info}"
            f"{style_instruction}{guardian_style_instruction}"
        ),
        agent=agents[1],
        expected_output="本章相关的人物卡快照与世界观设定检查表（Markdown格式）"
    )
    tasks.append(task2)
    
    # 3. 章节主写手任务 (原Task 4)
    writer_instruction = (
        f"根据所有准备工作撰写{min_chars}-{max_chars}字正文。\n"
        "强制要求：\n"
        "0. 开头必须直接进入场景（动作/对白/冲突），禁止用“回顾/复盘/前情提要”式叙述；禁止出现‘上一章/上回/回想/不久前/转眼/与此同时’等总结承接句；禁止使用通用开场白（如天色/夜色/时间飞逝/几日后/一夜之间）。\n"
        "1. 必须承接上一章末状态，并在本章前20%篇幅落地。\n"
        "2. 不得让角色状态回滚、瞬移、突然知道未出现信息。\n"
        "3. 不得引入未交代的新核心设定替代既有设定。\n"
        f"4. 【硬性字数】正文（不含摘要块）必须≥{min_chars}字。\n"
        "4. 正文结束后追加摘要块，格式必须严格如下：\n"
        "[SUMMARY_BEGIN]\n"
        "本章目标达成：...\n"
        "不可逆事实：...\n"
        "角色状态变更：...\n"
        "资源变更：...\n"
        "新增/回收伏笔：...\n"
        "下一章承接锚点：...\n"
        "[SUMMARY_END]\n"
        f"{style_instruction}"
        f"{writer_style_instruction}"
        f"{base_context}{prev_info}"
    )
    if compact_mode:
        writer_instruction = (
            "根据提纲与人物设定直接写出完整正文并保证节奏紧凑。\n"
            "开头必须直接进入场景（动作/对白/冲突），禁止复述前情与通用开场白。\n"
            "强制要求：承接上一章末状态；保持人设与世界观一致；不得新增未铺垫核心设定。\n"
            f"【硬性字数】正文（不含摘要块）必须≥{min_chars}字。\n"
            "正文结束后追加摘要块，格式必须严格如下：\n"
            "[SUMMARY_BEGIN]\n"
            "本章目标达成：...\n"
            "不可逆事实：...\n"
            "角色状态变更：...\n"
            "资源变更：...\n"
            "新增/回收伏笔：...\n"
            "下一章承接锚点：...\n"
            "[SUMMARY_END]\n"
            f"{style_instruction}"
            f"{writer_style_instruction}"
            f"{base_context}{prev_info}"
        )
    task3 = Task(
        description=writer_instruction,
        agent=agents[2],
        expected_output=f"完整的章节正文（{min_chars}-{max_chars}字）"
    )
    tasks.append(task3)
    
    # 4. 终极审校专家任务 (原Task 5)
    finalizer_instruction = (
        "作为主编，请先执行【一致性Gate】，再执行润色：\n"
        "1. 必须项：承接上一章末状态；覆盖本章细纲关键事件；人设/战力/世界规则不跳变；\n"
        "2. 禁止项：角色突然知道未出现信息、设定回滚、无铺垫新增核心设定；\n"
        "3. 如发现硬伤，先直接改正文，再润色，不要只做提示；\n"
        "4. 完成后输出最终定稿。\n\n"
        "【重要要求】\n"
        "A. 输出必须包含章节标题，格式为 Markdown 一级标题，例如：# 第N章 章节名；\n"
        "B. 正文中禁止出现任何情节分段标题（如 ##/###/####，或行首'一、二、三、...'小标题）；\n"
        "C. 必须移除写手附加的摘要块（[SUMMARY_BEGIN]... [SUMMARY_END]），最终输出不包含该区块；\n"
        f"D. 【硬性字数】最终正文必须≥{min_chars}字；不足则在不改剧情的前提下扩写补足。\n"
        "E. 只输出最终正文，不要输出检查过程。\n"
        "F. 如果开头出现复述前情/模板化开场白，请直接改写为动作或对白起笔的承接开头。\n"
        f"{style_instruction}"
        f"{finalizer_style_instruction}"
        f"{base_context}{prev_info}"
    )
    task4 = Task(
        description=finalizer_instruction,
        agent=agents[3],
        expected_output="经审查与润色后的完整章节定稿，必须以 '# 第N章 章节名' 开头"
    )
    tasks.append(task4)
    
    return tasks
