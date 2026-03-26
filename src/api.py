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

API_KEYS_FILE = os.path.join(CONFIG_DIR, ".api_keys.enc")
KEY_FILE = os.path.join(CONFIG_DIR, ".encryption_key")
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

DEFAULT_MODEL_PRESET = "default"
DEFAULT_MODEL_PARAMS = {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": None,
}
SUPPORTED_MODEL_PRESETS = {"default", "custom"}
MODEL_ROLES = ("outline", "character", "writer", "finalizer")
MODEL_ROLE_LABELS = {
    "outline": "大纲优化师",
    "character": "人物守护者",
    "writer": "主写手",
    "finalizer": "终极审校",
}
MODEL_CAPABILITY_RULES = [
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
DEFAULT_CAPABILITY_LIMITS = {
    "temperature": {"min": 0.0, "max": 2.0, "step": 0.1},
    "top_p": {"min": 0.1, "max": 1.0, "step": 0.05},
    "max_tokens": {"min": 256, "max": 8192, "step": 128},
}


def get_model_capability_limits(model_name):
    """按模型名前缀返回参数能力边界，供 UI 与保存阶段共用。"""
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
    """根据当前路由与 Key 可用性解析 4 个角色实际模型。"""
    raw = keys or {}
    route_profile = raw.get("ROUTE_PROFILE", "speed")
    writer_model_pref = raw.get("WRITER_MODEL", "auto")
    has_kimi_key = bool((raw.get("MOONSHOT_API_KEY") or "").strip())

    deepseek_model = "openai/deepseek-reasoner" if route_profile == "quality" else "openai/deepseek-chat"
    qwen_model = "openai/qwen-max" if route_profile == "quality" else "openai/qwen-plus"
    kimi_model = "openai/kimi-k2.5"

    writer_model = qwen_model
    if writer_model_pref == "kimi" and has_kimi_key:
        writer_model = kimi_model
    elif writer_model_pref == "auto" and route_profile == "quality" and has_kimi_key:
        writer_model = kimi_model

    finalizer_model = kimi_model if has_kimi_key else qwen_model
    return {
        "outline": deepseek_model,
        "character": qwen_model,
        "writer": writer_model,
        "finalizer": finalizer_model,
    }


def _normalize_model_params(params, capability_limits=None):
    """标准化并校验模型参数，保证配置可回读。"""
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
    """按角色批量归一化参数，统一处理越界与类型异常。"""
    raw = params_by_role or {}
    out = {}
    for role in MODEL_ROLES:
        role_model = role_models.get(role, "")
        limits = get_model_capability_limits(role_model)
        candidate = raw.get(role, DEFAULT_MODEL_PARAMS)
        out[role] = _normalize_model_params(candidate, limits)
    return out


def _role_params_from_legacy(model_params):
    """兼容旧配置：单份 MODEL_PARAMS 扩展到 4 个角色。"""
    normalized_single = _normalize_model_params(model_params or DEFAULT_MODEL_PARAMS, DEFAULT_CAPABILITY_LIMITS)
    return {role: dict(normalized_single) for role in MODEL_ROLES}


def _default_model_params_by_role(role_models):
    """基于角色当前模型生成默认参数（并按能力裁剪）。"""
    return _normalize_role_params_map({role: DEFAULT_MODEL_PARAMS for role in MODEL_ROLES}, role_models)


def resolve_provider_config(route_profile="speed"):
    config = {k: v.copy() for k, v in BASE_PROVIDER_CONFIG.items()}
    if route_profile == "quality":
        config["deepseek"]["model"] = "openai/deepseek-reasoner"
        config["qwen"]["model"] = "openai/qwen-max"
        config["kimi"]["model"] = "openai/kimi-k2.5"
    return config


def get_encryption_key():
    """获取或生成加密密钥"""
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
):
    """保存 API 与模型配置（加密）。

    说明：
    - model_preset 支持 default/custom
    - model_params_by_role 支持 4 角色独立参数
    - 旧字段 model_params 仅用于兼容迁移
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
        "CREWAI_ENABLE_MEMORY": False,
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
    """加载并迁移 API 配置（解密 + 结构兼容）。"""
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
                "CREWAI_ENABLE_MEMORY": False,
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
            "CREWAI_ENABLE_MEMORY": False,
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
            "CREWAI_ENABLE_MEMORY": False,
            "MODEL_PRESET": DEFAULT_MODEL_PRESET,
            "MODEL_PARAMS_BY_ROLE": defaults_by_role,
            "MODEL_DEFAULTS_BY_ROLE": defaults_by_role,
            "MODEL_PARAMS": dict(defaults_by_role["writer"]),
        }


def test_api_connection(provider, api_key, route_profile="speed"):
    """测试API连接"""
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
    """测试所有API连接"""
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
