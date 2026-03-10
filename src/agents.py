from crewai import Agent, LLM
import os
from src.api import load_api_keys


def create_agents():
    """
    创建6个专业AI Agent（面向中文网文），具体模型与分工：

    模型与 API 名称：
    - DeepSeek：deepseek-chat（DeepSeek-V3.2，128K）— 大纲动态优化（1个）
    - 通义千问：qwen-plus（128K；可改为 qwen-turbo 省成本 / qwen-max 最强）— 人物、爽点、主写、审查、润色（5个）
    """
    agents = []
    keys = load_api_keys()
    route_profile = keys.get("ROUTE_PROFILE", "speed")
    
    # 设置环境变量 - 确保CrewAI memory功能正常工作
    os.environ["OPENAI_API_KEY"] = keys.get("DEEPSEEK_API_KEY", "dummy")
    os.environ["DEEPSEEK_API_KEY"] = keys.get("DEEPSEEK_API_KEY", "")
    os.environ["DASHSCOPE_API_KEY"] = keys.get("DASHSCOPE_API_KEY", "")
    os.environ["MOONSHOT_API_KEY"] = keys.get("MOONSHOT_API_KEY", "")
    
    # 配置LLM（具体模型见下方，OpenAI 兼容接口）
    # 增加超时控制和重试机制
    
    deepseek_model = "openai/deepseek-reasoner" if route_profile == "quality" else "openai/deepseek-chat"
    qwen_model = "openai/qwen-max" if route_profile == "quality" else "openai/qwen-plus"
    kimi_model = "openai/kimi-k2.5"

    deepseek_llm = LLM(
        model=deepseek_model,
        api_key=keys.get("DEEPSEEK_API_KEY", ""),
        base_url="https://api.deepseek.com/v1",
        timeout=600,  # R1思考时间较长，增加到10分钟
        max_retries=2
    )
    
    qwen_llm = LLM(
        model=qwen_model,
        api_key=keys.get("DASHSCOPE_API_KEY", ""),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        timeout=300,  # 5分钟超时
        max_retries=2
    )

    kimi_llm = LLM(
        model=kimi_model,
        api_key=keys.get("MOONSHOT_API_KEY", ""),
        base_url="https://api.moonshot.cn/v1",
        timeout=300,
        max_retries=2
    )
    writer_model = keys.get("WRITER_MODEL", "auto")
    has_kimi_key = bool((keys.get("MOONSHOT_API_KEY") or "").strip())

    writer_llm = qwen_llm
    if writer_model == "kimi" and has_kimi_key:
        writer_llm = kimi_llm
    elif writer_model == "auto" and route_profile == "quality" and has_kimi_key:
        writer_llm = kimi_llm

    editor_llm = qwen_llm
    # 强制终极审校专家使用Kimi K2.5（如果Key存在），以确保文字质感
    if has_kimi_key:
        editor_llm = kimi_llm
    
    # 1. 大纲动态优化师 - 使用DeepSeek
    agent_outline = Agent(
        role="大纲动态优化师",
        goal="把用户提供的大纲细化成当前章节详细提纲、爽点清单、伏笔表",
        backstory="你是一位资深网文编辑，有着10年以上的网文大纲规划经验。你擅长把简单的创意扩展成完整的长篇小说大纲。",
        llm=deepseek_llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3, # 降低迭代次数，防止R1无限推理
        max_execution_time=600 # 强制10分钟超时
    )
    agents.append(agent_outline)
    
    # 2. 人物与世界观守护者 - 使用通义千问
    agent_character = Agent(
        role="人物与世界观守护者",
        goal="维护完整人物卡、世界观一致性检查，防止后期崩人设",
        backstory="你是一位严谨的小说世界观构建师，你会仔细记录每一个人物的性格、背景、能力，确保整个故事的一致性。",
        llm=qwen_llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3, # 降低最大迭代次数，防止卡顿
        max_execution_time=300 # 5分钟强制超时
    )
    agents.append(agent_character)
    
    # [已移除] 3. 爽点强化设计师 - 职能合并至大纲优化师
    
    # 3. 章节主写手 (原Agent 4)
    agent_writer = Agent(
        role="章节主写手",
        goal="根据最新大纲 + 人物卡写出3500-5500字正文",
        backstory="你是一位高产的网文作家，文笔流畅，代入感强，擅长写精彩的情节。",
        llm=writer_llm,
        verbose=True,
        allow_delegation=False,
        max_iter=5, # 限制思考轮数，重点在一次性输出长文
        max_execution_time=900 # 延长到15分钟，适应长文生成
    )
    agents.append(agent_writer)
    
    # 4. 终极审校专家 - 合并原“审查员”与“润色师”职责
    agent_finalizer = Agent(
        role="终极审校专家",
        goal="一步完成情节逻辑审查与文字润色，输出最终定稿",
        backstory="你是一位兼具毒辣眼光与顶级文笔的资深主编。你能在审查逻辑漏洞的同时直接修改文字，确保作品既严谨又精彩。",
        llm=editor_llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
        max_execution_time=900 # 延长到15分钟
    )
    agents.append(agent_finalizer)
    
    return agents
