"""
Agent 模块 - 创建多 Agent 协作的 AI 写作团队

核心功能：
1. 创建 4 个专业 Agent：大纲优化师、世界观守护者、主写手、审校专家
2. 支持多模型：DeepSeek、通义千问、Kimi
3. 参数裁剪：根据模型能力边界自动调整 temperature、top_p、max_tokens
4. 路由策略：极速/平衡/质量优先，影响模型选择
"""

from crewai import Agent, LLM
import os
from src.api import (
    MODEL_ROLES,
    load_api_keys,
    resolve_runtime_role_models,
    get_model_capability_limits,
)
from src.tools import (
    make_read_character_cards,
    make_read_world_settings,
    make_read_chapter_outline_detail,
)


def _safe_model_params(params, limits):
    """
    按模型能力边界裁剪参数
    避免不同供应商参数越界导致请求失败

    参数：
    - params: 用户配置的参数 {temperature, top_p, max_tokens}
    - limits: 模型能力边界 {temperature: {min, max}, top_p: {min, max}, max_tokens: {min, max}}

    返回：裁剪后的安全参数
    """
    raw = params or {}
    try:
        temperature = float(raw.get("temperature", 1.0))
    except (TypeError, ValueError):
        temperature = 1.0
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
    """
    根据模式与角色生成 LLM 参数

    参数：
    - role: Agent 角色（outline/character/writer/finalizer）
    - model_name: 模型名称
    - preset: 参数模式（default/custom）
    - custom_params: 自定义参数
    - default_params: 默认参数

    返回：LLM kwargs 字典
    """
    limits = get_model_capability_limits(model_name)
    source = default_params if preset == "default" else custom_params
    selected = _safe_model_params(source, limits)
    return {
        "temperature": selected["temperature"],
        "top_p": selected["top_p"],
        "max_tokens": selected["max_tokens"],
    }


def create_agents(project_name: str = None, chapter_number: int = None):
    """
    创建 4 个专业 AI Agent（面向中文网文）

    Agent 分工：
    1. 大纲动态优化师（DeepSeek）：细化大纲、生成爽点清单和伏笔表
    2. 人物与世界观守护者（通义千问）：维护人物卡、世界观一致性
    3. 章节主写手（通义千问/Kimi）：撰写正文
    4. 终极审校专家（Kimi/通义千问）：润色、检查一致性

    参数：
    - project_name: 当前项目名称（可选）。提供后为守护者和主写手配置文件读取 Tools
    - chapter_number: 当前章节号（可选）。提供后主写手可按需读取本章大纲详情

    模型选择受以下因素影响：
    - 路由策略（speed/balanced/quality）
    - 主写模型偏好（auto/qwen/kimi）
    - Kimi Key 可用性

    返回：Agent 列表
    """
    agents = []
    keys = load_api_keys()
    route_profile = keys.get("ROUTE_PROFILE", "speed")
    model_preset = keys.get("MODEL_PRESET", "default")
    if model_preset not in {"default", "custom"}:
        model_preset = "default"
    role_models = resolve_runtime_role_models(keys)
    role_custom_params = keys.get("MODEL_PARAMS_BY_ROLE", {})
    role_default_params = keys.get("MODEL_DEFAULTS_BY_ROLE", {})
    for role in MODEL_ROLES:
        role_custom_params.setdefault(role, {})
        role_default_params.setdefault(role, {})

    os.environ["OPENAI_API_KEY"] = keys.get("DEEPSEEK_API_KEY", "dummy")
    os.environ["DEEPSEEK_API_KEY"] = keys.get("DEEPSEEK_API_KEY", "")
    os.environ["DASHSCOPE_API_KEY"] = keys.get("DASHSCOPE_API_KEY", "")
    os.environ["MOONSHOT_API_KEY"] = keys.get("MOONSHOT_API_KEY", "")

    deepseek_model = role_models["outline"]
    qwen_model = role_models["character"]
    kimi_model = "openai/kimi-k2-5"
    writer_runtime_model = role_models["writer"]
    finalizer_runtime_model = role_models["finalizer"]

    def _llm_kwargs_for(role, model_name):
        """统一在这里做模式选择+边界裁剪，确保所有角色构造行为一致"""
        role_kwargs = _build_role_llm_kwargs(
            role,
            model_name,
            model_preset,
            role_custom_params.get(role, {}),
            role_default_params.get(role, {}),
        )
        model_lower = (model_name or "").lower()
        is_reasoner = any(p in model_lower for p in ["deepseek-reasoner", "openai/o1", "openai/o3"])
        if is_reasoner:
            payload = {}
            if role_kwargs.get("max_tokens") is not None:
                payload["max_tokens"] = role_kwargs["max_tokens"]
            return payload
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
        timeout=600,
        max_retries=2,
        **_llm_kwargs_for("outline", deepseek_model),
    )

    qwen_llm = LLM(
        model=qwen_model,
        api_key=keys.get("DASHSCOPE_API_KEY", ""),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        timeout=300,
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

    agent_outline = Agent(
        role="大纲动态优化师",
        goal="把用户提供的大纲细化成当前章节详细提纲、爽点清单、伏笔表",
        backstory="你是一位资深网文编辑，有着10年以上的网文大纲规划经验。你擅长把简单的创意扩展成完整的长篇小说大纲。",
        llm=deepseek_llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
        max_execution_time=600
    )
    agents.append(agent_outline)

    # 按需为守护者和主写手构建文件读取 Tools
    character_tools = []
    writer_tools = []
    if project_name:
        character_tools = [
            make_read_character_cards(project_name),
            make_read_world_settings(project_name),
        ]
        writer_tools = [
            make_read_chapter_outline_detail(project_name, chapter_number or 1),
        ]

    agent_character = Agent(
        role="人物与世界观守护者",
        goal="维护完整人物卡、世界观一致性检查，防止后期崩人设",
        backstory="你是一位严谨的小说世界观构建师，你会仔细记录每一个人物的性格、背景、能力，确保整个故事的一致性。",
        llm=qwen_llm,
        verbose=True,
        allow_delegation=False,
        tools=character_tools,
        max_iter=3,
        max_execution_time=300
    )
    agents.append(agent_character)

    agent_writer = Agent(
        role="章节主写手",
        goal="根据最新大纲 + 人物卡写出符合字数要求的正文",
        backstory="你是一位高产的网文作家，文笔流畅，代入感强，擅长写精彩的情节。",
        llm=writer_llm,
        verbose=True,
        allow_delegation=False,
        tools=writer_tools,
        max_iter=3,
        max_execution_time=900
    )
    agents.append(agent_writer)

    agent_editor = Agent(
        role="终极审校专家",
        goal="润色正文、检查一致性、确保符合网文节奏和爽点要求",
        backstory="你是一位严谨的网文主编，擅长发现问题、润色文字、确保故事节奏紧凑、爽点到位。",
        llm=editor_llm,
        verbose=True,
        allow_delegation=False,
        max_iter=2,
        max_execution_time=600
    )
    agents.append(agent_editor)

    return agents
