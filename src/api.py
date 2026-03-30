"""
API 配置模块 - 管理 API 密钥、模型参数、路由策略

核心功能：
1. API 密钥管理：加密存储 DeepSeek、通义千问、Kimi 的 API Key
2. 模型参数配置：按角色（大纲优化师、人物守护者、主写手、审校专家）独立配置参数
3. 路由策略：极速/平衡/质量优先，影响模型选择
4. 模型能力边界：根据不同模型的 API 限制自动裁剪参数
5. 连接测试：验证 API Key 是否有效

配置文件位置：
- Windows: %APPDATA%/AI_Novel_Writer/
- macOS/Linux: ~/.config/AI_Novel_Writer/

文件：
- .api_keys.enc: 加密的 API 配置
- .encryption_key: 加密密钥
"""

import json
import litellm
import base64
import os
import sys
from cryptography.fernet import Fernet

# 用户配置文件位置
if sys.platform == "win32":
    CONFIG_DIR = os.path.join(os.environ["APPDATA"], "AI_Novel_Writer")
else:
    CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "AI_Novel_Writer")

if not os.path.exists(CONFIG_DIR):
    try:
        os.makedirs(CONFIG_DIR)
    except Exception:
        pass

# 配置文件路径
API_KEYS_FILE = os.path.join(CONFIG_DIR, ".api_keys.enc")    # 加密的 API 配置
KEY_FILE = os.path.join(CONFIG_DIR, ".encryption_key")       # 加密密钥

# 基础模型配置
BASE_PROVIDER_CONFIG = {
    "deepseek": {
        "model": "openai/deepseek-chat",
        "base_url": "https://api.deepseek.com/v1",
        "key_field": "DEEPSEEK_API_KEY",
    },
    "qwen": {
        "model": "openai/qwen-turbo",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "key_field": "DASHSCOPE_API_KEY",
    },
    "kimi": {
        "model": "openai/kimi-k2.5",
        "base_url": "https://api.moonshot.cn/v1",
        "key_field": "MOONSHOT_API_KEY",
    },
}

# 默认模型参数
DEFAULT_MODEL_PRESET = "default"
DEFAULT_MODEL_PARAMS = {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": None,
}
SUPPORTED_MODEL_PRESETS = {"default", "custom"}

# Agent 角色定义
MODEL_ROLES = ("outline", "character", "writer", "finalizer")
MODEL_ROLE_LABELS = {
    "outline": "大纲优化师",
    "character": "人物守护者",
    "writer": "主写手",
    "finalizer": "终极审校",
}

# 模型能力边界规则
# 不同模型的 API 对参数有不同的限制，需要自动裁剪
MODEL_CAPABILITY_RULES = [
    {
        "prefixes": ("openai/deepseek-reasoner", "openai/o1", "openai/o3"),
        "limits": {
            "temperature": {"min": 1.0, "max": 1.0, "step": 0.0},
            "top_p": {"min": 1.0, "max": 1.0, "step": 0.0},
            "max_tokens": {"min": 256, "max": 8192, "step": 128},
        },
    },
    {
        "prefixes": ("openai/deepseek",),
        "limits": {
            "temperature": {"min": 0.0, "max": 2.0, "step": 0.1},
            "top_p": {"min": 0.1, "max": 1.0, "step": 0.05},
            "max_tokens": {"min": 256, "max": 8192, "step": 128},
        },
    },
    {
        "prefixes": ("openai/qwen",),
        "limits": {
            "temperature": {"min": 0.0, "max": 2.0, "step": 0.1},
            "top_p": {"min": 0.1, "max": 1.0, "step": 0.05},
            "max_tokens": {"min": 256, "max": 8192, "step": 128},
        },
    },
    {
        "prefixes": ("openai/kimi",),
        "limits": {
            "temperature": {"min": 0.0, "max": 1.5, "step": 0.1},
            "top_p": {"min": 0.1, "max": 1.0, "step": 0.05},
            "max_tokens": {"min": 256, "max": 16384, "step": 128},
        },
    },
]

# 默认能力边界（用于未知模型）
DEFAULT_CAPABILITY_LIMITS = {
    "temperature": {"min": 0.0, "max": 2.0, "step": 0.1},
    "top_p": {"min": 0.1, "max": 1.0, "step": 0.05},
    "max_tokens": {"min": 256, "max": 8192, "step": 128},
}


def get_model_capability_limits(model_name):
    """
    获取模型的能力边界

    根据模型名称前缀匹配对应的参数限制规则。
    用于 UI 滑块范围限制和参数保存时的校验。

    参数：
    - model_name: 模型名称（如 "openai/deepseek-chat"）

    返回：{
        temperature: {min, max, step},
        top_p: {min, max, step},
        max_tokens: {min, max, step}
    }
    """
    model = (model_name or "").lower()
    for rule in MODEL_CAPABILITY_RULES:
        if any(model.startswith(prefix) for prefix in rule["prefixes"]):
            return {
                "temperature": dict(rule["limits"]["temperature"]),
                "top_p": dict(rule["limits"]["top_p"]),
                "max_tokens": dict(rule["limits"]["max_tokens"]),
            }
    return {
        "temperature": dict(DEFAULT_CAPABILITY_LIMITS["temperature"]),
        "top_p": dict(DEFAULT_CAPABILITY_LIMITS["top_p"]),
        "max_tokens": dict(DEFAULT_CAPABILITY_LIMITS["max_tokens"]),
    }


def resolve_runtime_role_models(keys=None):
    """
    根据路由策略和 Key 可用性解析 4 个角色的实际模型

    路由策略影响：
    - speed（极速）：使用轻量模型（deepseek-chat, qwen-turbo）
    - balanced（平衡）：使用标准模型（deepseek-chat, qwen-plus）
    - quality（质量）：使用高级模型（deepseek-reasoner, qwen-max）

    主写模型偏好：
    - auto：根据路由策略自动选择
    - qwen：强制使用通义千问
    - kimi：强制使用 Kimi（需要 Kimi Key）

    返回：{outline, character, writer, finalizer} -> 模型名称
    """
    raw = keys or {}
    route_profile = raw.get("ROUTE_PROFILE", "speed")
    writer_model_pref = raw.get("WRITER_MODEL", "auto")
    has_kimi_key = bool((raw.get("MOONSHOT_API_KEY") or "").strip())

    # 根据路由策略选择模型
    deepseek_model = "openai/deepseek-reasoner" if route_profile == "quality" else "openai/deepseek-chat"
    qwen_model = "openai/qwen-max" if route_profile == "quality" else "openai/qwen-plus"
    kimi_model = "openai/kimi-k2.5"

    # 主写手模型选择
    writer_model = qwen_model
    if writer_model_pref == "kimi" and has_kimi_key:
        writer_model = kimi_model
    elif writer_model_pref == "auto" and route_profile == "quality" and has_kimi_key:
        writer_model = kimi_model

    # 审校专家模型选择（优先 Kimi）
    finalizer_model = kimi_model if has_kimi_key else qwen_model
    return {
        "outline": deepseek_model,
        "character": qwen_model,
        "writer": writer_model,
        "finalizer": finalizer_model,
    }


def _normalize_model_params(params, capability_limits=None):
    """
    标准化并校验模型参数

    确保参数在模型能力边界内，处理类型异常。

    参数：
    - params: 原始参数字典
    - capability_limits: 能力边界（可选）

    返回：标准化后的参数字典
    """
    limits = capability_limits or DEFAULT_CAPABILITY_LIMITS
    src = params or {}
    try:
        temperature = float(src.get("temperature", DEFAULT_MODEL_PARAMS["temperature"]))
    except (TypeError, ValueError):
        temperature = DEFAULT_MODEL_PARAMS["temperature"]
    temperature = max(limits["temperature"]["min"], min(limits["temperature"]["max"], temperature))

    try:
        top_p = float(src.get("top_p", DEFAULT_MODEL_PARAMS["top_p"]))
    except (TypeError, ValueError):
        top_p = DEFAULT_MODEL_PARAMS["top_p"]
    top_p = max(limits["top_p"]["min"], min(limits["top_p"]["max"], top_p))

    raw_max_tokens = src.get("max_tokens", DEFAULT_MODEL_PARAMS["max_tokens"])
    max_tokens = None
    if raw_max_tokens not in (None, ""):
        try:
            max_tokens = int(raw_max_tokens)
            if max_tokens < int(limits["max_tokens"]["min"]):
                max_tokens = None
            else:
                max_tokens = min(max_tokens, int(limits["max_tokens"]["max"]))
        except (TypeError, ValueError):
            max_tokens = None

    return {
        "temperature": round(temperature, 2),
        "top_p": round(top_p, 2),
        "max_tokens": max_tokens,
    }


def _normalize_role_params_map(params_by_role, role_models):
    """
    按角色批量归一化参数

    对每个角色的参数进行校验和裁剪，确保符合对应模型的能力边界。

    参数：
    - params_by_role: 按角色的参数字典
    - role_models: 按角色的模型字典

    返回：归一化后的按角色参数字典
    """
    raw = params_by_role or {}
    out = {}
    for role in MODEL_ROLES:
        role_model = role_models.get(role, "")
        limits = get_model_capability_limits(role_model)
        candidate = raw.get(role, DEFAULT_MODEL_PARAMS)
        out[role] = _normalize_model_params(candidate, limits)
    return out


def _role_params_from_legacy(model_params):
    """
    兼容旧配置：将单份 MODEL_PARAMS 扩展到 4 个角色

    用于迁移旧版本的配置文件。
    """
    normalized_single = _normalize_model_params(model_params or DEFAULT_MODEL_PARAMS, DEFAULT_CAPABILITY_LIMITS)
    return {role: dict(normalized_single) for role in MODEL_ROLES}


def _default_model_params_by_role(role_models):
    """
    基于角色当前模型生成默认参数

    返回：按角色的默认参数字典（已按能力裁剪）
    """
    return _normalize_role_params_map({role: DEFAULT_MODEL_PARAMS for role in MODEL_ROLES}, role_models)


def resolve_provider_config(route_profile="speed"):
    """
    根据路由策略解析模型配置

    返回：{deepseek, qwen, kimi} -> {model, base_url, key_field}
    """
    config = {k: v.copy() for k, v in BASE_PROVIDER_CONFIG.items()}
    if route_profile == "quality":
        config["deepseek"]["model"] = "openai/deepseek-reasoner"
        config["qwen"]["model"] = "openai/qwen-max"
        config["kimi"]["model"] = "openai/kimi-k2.5"
    return config


def get_encryption_key():
    """
    获取或生成加密密钥

    密钥存储在 .encryption_key 文件中，首次使用时自动生成。
    使用 Fernet 对称加密算法。
    """
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        return key
    else:
        with open(KEY_FILE, "rb") as f:
            return f.read()


def save_api_keys(
    deepseek,
    qwen,
    kimi,
    auth_code="",
    route_profile="speed",
    writer_model="auto",
    model_preset=DEFAULT_MODEL_PRESET,
    model_params_by_role=None,
    model_defaults_by_role=None,
    model_params=None,
    memory_enabled=False,
):
    """
    保存 API 与模型配置（加密存储）

    参数：
    - deepseek: DeepSeek API Key
    - qwen: 通义千问 API Key
    - kimi: Kimi API Key
    - auth_code: 授权码
    - route_profile: 路由策略（speed/balanced/quality）
    - writer_model: 主写模型偏好（auto/qwen/kimi）
    - model_preset: 参数模式（default/custom）
    - model_params_by_role: 按角色的自定义参数
    - model_defaults_by_role: 按角色的默认参数
    - model_params: 旧版单份参数（兼容迁移）
    - memory_enabled: 是否启用 CrewAI 长期记忆
    """
    runtime_keys = {
        "ROUTE_PROFILE": route_profile,
        "WRITER_MODEL": writer_model,
        "MOONSHOT_API_KEY": kimi,
    }
    role_models = resolve_runtime_role_models(runtime_keys)
    default_role_params = _default_model_params_by_role(role_models)
    raw_defaults = model_defaults_by_role or default_role_params
    normalized_defaults = _normalize_role_params_map(raw_defaults, role_models)
    if model_params_by_role is None and model_params is not None:
        model_params_by_role = _role_params_from_legacy(model_params)
    raw_custom = model_params_by_role or normalized_defaults
    normalized_custom = _normalize_role_params_map(raw_custom, role_models)
    preset = model_preset if model_preset in SUPPORTED_MODEL_PRESETS else DEFAULT_MODEL_PRESET

    keys = {
        "DEEPSEEK_API_KEY": deepseek,
        "DASHSCOPE_API_KEY": qwen,
        "MOONSHOT_API_KEY": kimi,
        "AUTH_CODE": auth_code,
        "ROUTE_PROFILE": route_profile,
        "WRITER_MODEL": writer_model,
        "CREWAI_ENABLE_MEMORY": bool(memory_enabled),
        "MODEL_PRESET": preset,
        "MODEL_PARAMS_BY_ROLE": normalized_custom,
        "MODEL_DEFAULTS_BY_ROLE": normalized_defaults,
        "MODEL_PARAMS": dict(normalized_custom["writer"]),
    }

    key = get_encryption_key()
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(json.dumps(keys).encode())

    with open(API_KEYS_FILE, "wb") as f:
        f.write(encrypted_data)


def load_api_keys():
    """
    加载并迁移 API 配置（解密 + 结构兼容）

    返回完整的配置字典，包含：
    - API Keys（DEEPSEEK_API_KEY, DASHSCOPE_API_KEY, MOONSHOT_API_KEY）
    - 授权码（AUTH_CODE）
    - 路由策略（ROUTE_PROFILE）
    - 主写模型偏好（WRITER_MODEL）
    - 参数模式（MODEL_PRESET）
    - 按角色参数（MODEL_PARAMS_BY_ROLE, MODEL_DEFAULTS_BY_ROLE）

    若配置文件不存在或解密失败，返回默认配置。
    """
    try:
        if not os.path.exists(API_KEYS_FILE):
            role_models = resolve_runtime_role_models({})
            defaults_by_role = _default_model_params_by_role(role_models)
            return {
                "DEEPSEEK_API_KEY": "",
                "DASHSCOPE_API_KEY": "",
                "MOONSHOT_API_KEY": "",
                "AUTH_CODE": "",
                "ROUTE_PROFILE": "speed",
                "WRITER_MODEL": "auto",
                "CREWAI_ENABLE_MEMORY": False,  # 首次使用默认关闭
                "MODEL_PRESET": DEFAULT_MODEL_PRESET,
                "MODEL_PARAMS_BY_ROLE": defaults_by_role,
                "MODEL_DEFAULTS_BY_ROLE": defaults_by_role,
                "MODEL_PARAMS": dict(defaults_by_role["writer"]),
            }

        key = get_encryption_key()
        with open(API_KEYS_FILE, "rb") as f:
            encrypted_data = f.read()

        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data)
        keys = json.loads(decrypted_data.decode())
        role_models = resolve_runtime_role_models(keys)
        defaults_by_role = _normalize_role_params_map(
            keys.get("MODEL_DEFAULTS_BY_ROLE", _default_model_params_by_role(role_models)),
            role_models,
        )
        role_params = keys.get("MODEL_PARAMS_BY_ROLE")
        if not isinstance(role_params, dict):
            role_params = _role_params_from_legacy(keys.get("MODEL_PARAMS", DEFAULT_MODEL_PARAMS))
        role_params = _normalize_role_params_map(role_params, role_models)
        preset = keys.get("MODEL_PRESET", DEFAULT_MODEL_PRESET)
        if preset not in SUPPORTED_MODEL_PRESETS:
            preset = DEFAULT_MODEL_PRESET

        # 兼容旧版本 key 结构
        return {
            "DEEPSEEK_API_KEY": keys.get("DEEPSEEK_API_KEY", ""),
            "DASHSCOPE_API_KEY": keys.get("DASHSCOPE_API_KEY", ""),
            "MOONSHOT_API_KEY": keys.get("MOONSHOT_API_KEY", ""),
            "AUTH_CODE": keys.get("AUTH_CODE", ""),
            "ROUTE_PROFILE": keys.get("ROUTE_PROFILE", "speed"),
            "WRITER_MODEL": keys.get("WRITER_MODEL", "auto"),
            "CREWAI_ENABLE_MEMORY": bool(keys.get("CREWAI_ENABLE_MEMORY", False)),
            "MODEL_PRESET": preset,
            "MODEL_PARAMS_BY_ROLE": role_params,
            "MODEL_DEFAULTS_BY_ROLE": defaults_by_role,
            "MODEL_PARAMS": dict(role_params["writer"]),
        }
    except Exception:
        role_models = resolve_runtime_role_models({})
        defaults_by_role = _default_model_params_by_role(role_models)
        return {
            "DEEPSEEK_API_KEY": "",
            "DASHSCOPE_API_KEY": "",
            "MOONSHOT_API_KEY": "",
            "AUTH_CODE": "",
            "ROUTE_PROFILE": "speed",
            "WRITER_MODEL": "auto",
            "CREWAI_ENABLE_MEMORY": False,  # 异常时安全默认关闭
            "MODEL_PRESET": DEFAULT_MODEL_PRESET,
            "MODEL_PARAMS_BY_ROLE": defaults_by_role,
            "MODEL_DEFAULTS_BY_ROLE": defaults_by_role,
            "MODEL_PARAMS": dict(defaults_by_role["writer"]),
        }


def test_api_connection(provider, api_key, route_profile="speed"):
    """
    测试 API 连接

    参数：
    - provider: 提供商名称（deepseek/qwen/kimi）
    - api_key: API Key
    - route_profile: 路由策略

    返回：(成功与否, 消息)
    """
    try:
        config = resolve_provider_config(route_profile).get(provider)
        if not config:
            return False, f"未知 provider: {provider}"
        if not (api_key or "").strip():
            return False, "未配置 API Key"

        litellm.completion(
            model=config["model"],
            api_key=api_key,
            base_url=config["base_url"],
            messages=[{"role": "user", "content": "OK"}],
            max_tokens=5,
            timeout=10
        )
        return True, "连接成功"
    except Exception as e:
        return False, str(e)


def test_all_apis(providers=None):
    """
    测试所有 API 连接

    参数：
    - providers: 要测试的提供商列表（可选，默认全部）

    返回：{provider: (成功与否, 消息)}
    """
    keys = load_api_keys()
    results = {}
    route_profile = keys.get("ROUTE_PROFILE", "speed")
    provider_config = resolve_provider_config(route_profile)

    target_providers = providers or list(provider_config.keys())
    for provider in target_providers:
        config = provider_config.get(provider)
        if not config:
            results[provider] = (False, f"未知 provider: {provider}")
            continue
        api_key = keys.get(config["key_field"], "")
        results[provider] = test_api_connection(provider, api_key, route_profile)

    return results
