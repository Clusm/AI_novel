from crewai import Agent, LLM
import os
from src.api import (
    MODEL_ROLES,
    load_api_keys,
    resolve_runtime_role_models,
    get_model_capability_limits,
)


def _safe_model_params(params, limits):
    """按模型能力边界裁剪参数，避免不同供应商参数越界导致请求失败。"""
    raw = params or {}
    try:
        temperature = float(raw.get("temperature", 0.7))
    except (TypeError, ValueError):
        temperature = 0.7
    temperature = max(float(limits["temperature"]["min"]), min(float(limits["temperature"]["max"]), temperature))

    try:
        top_p = float(raw.get("top_p", 0.9))
    except (TypeError, ValueError):
        top_p = 0.9
    top_p = max(float(limits["top_p"]["min"]), min(float(limits["top_p"]["max"]), top_p))

    max_tokens = raw.get("max_tokens", None)
    if max_tokens in ("", None):
        max_tokens = None
    else:
        try:
            max_tokens = int(max_tokens)
            min_tokens = int(limits["max_tokens"]["min"])
            max_allowed = int(limits["max_tokens"]["max"])
            if max_tokens < min_tokens:
                max_tokens = None
            else:
                max_tokens = min(max_tokens, max_allowed)
        except (TypeError, ValueError):
            max_tokens = None

    return {
        "temperature": round(temperature, 2),
        "top_p": round(top_p, 2),
        "max_tokens": max_tokens,
    }


def _build_role_llm_kwargs(role, model_name, preset, custom_params, default_params):
    """根据模式与角色取值生成 LLM kwargs。"""
    limits = get_model_capability_limits(model_name)
    source = default_params if preset == "default" else custom_params
    selected = _safe_model_params(source, limits)
    return {
        "temperature": selected["temperature"],
        "top_p": selected["top_p"],
        "max_tokens": selected["max_tokens"],
    }


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
    # 参数模式：default 读取每角色默认值；custom 读取每角色自定义值
    model_preset = keys.get("MODEL_PRESET", "default")
    if model_preset not in {"default", "custom"}:
        model_preset = "default"
    # 角色-模型映射会受路由策略、主写模型偏好、Kimi Key 可用性共同影响
    role_models = resolve_runtime_role_models(keys)
    role_custom_params = keys.get("MODEL_PARAMS_BY_ROLE", {})
    role_default_params = keys.get("MODEL_DEFAULTS_BY_ROLE", {})
    for role in MODEL_ROLES:
        role_custom_params.setdefault(role, {})
        role_default_params.setdefault(role, {})
    
    # 设置环境变量 - 确保CrewAI memory功能正常工作
    os.environ["OPENAI_API_KEY"] = keys.get("DEEPSEEK_API_KEY", "dummy")
    os.environ["DEEPSEEK_API_KEY"] = keys.get("DEEPSEEK_API_KEY", "")
    os.environ["DASHSCOPE_API_KEY"] = keys.get("DASHSCOPE_API_KEY", "")
    os.environ["MOONSHOT_API_KEY"] = keys.get("MOONSHOT_API_KEY", "")
    
    # 配置LLM（具体模型见下方，OpenAI 兼容接口）
    # 增加超时控制和重试机制
    
    deepseek_model = role_models["outline"]
    qwen_model = role_models["character"]
    kimi_model = "openai/kimi-k2.5"
    writer_runtime_model = role_models["writer"]
    finalizer_runtime_model = role_models["finalizer"]

    def _llm_kwargs_for(role, model_name):
        # 统一在这里做模式选择+边界裁剪，确保所有角色构造行为一致
        role_kwargs = _build_role_llm_kwargs(
            role,
            model_name,
            model_preset,
            role_custom_params.get(role, {}),
            role_default_params.get(role, {}),
        )
        payload = {
            "temperature": role_kwargs["temperature"],
            "top_p": role_kwargs["top_p"],
        }
        if role_kwargs["max_tokens"] is not None:
            payload["max_tokens"] = role_kwargs["max_tokens"]
        return payload

    deepseek_llm = LLM(
        model=deepseek_model,
        api_key=keys.get("DEEPSEEK_API_KEY", ""),
        base_url="https://api.deepseek.com/v1",
        timeout=600,  # R1思考时间较长，增加到10分钟
        max_retries=2,
        **_llm_kwargs_for("outline", deepseek_model),
    )
    
    qwen_llm = LLM(
        model=qwen_model,
        api_key=keys.get("DASHSCOPE_API_KEY", ""),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        timeout=300,  # 5分钟超时
        max_retries=2,
        **_llm_kwargs_for("character", qwen_model),
    )

    kimi_llm = LLM(
        model=kimi_model,
        api_key=keys.get("MOONSHOT_API_KEY", ""),
        base_url="https://api.moonshot.cn/v1",
        timeout=300,
        max_retries=2,
        **_llm_kwargs_for("finalizer", kimi_model),
    )
    writer_model = keys.get("WRITER_MODEL", "auto")
    has_kimi_key = bool((keys.get("MOONSHOT_API_KEY") or "").strip())

    writer_llm = qwen_llm
    if writer_runtime_model == kimi_model and has_kimi_key:
        writer_llm = LLM(
            model=kimi_model,
            api_key=keys.get("MOONSHOT_API_KEY", ""),
            base_url="https://api.moonshot.cn/v1",
            timeout=300,
            max_retries=2,
            **_llm_kwargs_for("writer", kimi_model),
        )
    else:
        writer_llm = LLM(
            model=qwen_model,
            api_key=keys.get("DASHSCOPE_API_KEY", ""),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            timeout=300,
            max_retries=2,
            **_llm_kwargs_for("writer", qwen_model),
        )

    editor_llm = qwen_llm
    if finalizer_runtime_model == kimi_model and has_kimi_key:
        editor_llm = LLM(
            model=kimi_model,
            api_key=keys.get("MOONSHOT_API_KEY", ""),
            base_url="https://api.moonshot.cn/v1",
            timeout=300,
            max_retries=2,
            **_llm_kwargs_for("finalizer", kimi_model),
        )
    elif finalizer_runtime_model == qwen_model:
        editor_llm = LLM(
            model=qwen_model,
            api_key=keys.get("DASHSCOPE_API_KEY", ""),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            timeout=300,
            max_retries=2,
            **_llm_kwargs_for("finalizer", qwen_model),
        )
    
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
        goal="根据最新大纲 + 人物卡写出符合字数要求的正文",
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
