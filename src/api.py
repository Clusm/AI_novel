import json
import litellm
import base64
import os
import sys
from cryptography.fernet import Fernet

# User config file location
if sys.platform == "win32":
    CONFIG_DIR = os.path.join(os.environ["APPDATA"], "AI_Novel_Writer")
else:
    CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "ai_novel_writer")

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


def save_api_keys(deepseek, qwen, kimi, auth_code="", route_profile="speed", writer_model="auto"):
    """保存API Key（加密）"""
    keys = {
        "DEEPSEEK_API_KEY": deepseek,
        "DASHSCOPE_API_KEY": qwen,
        "MOONSHOT_API_KEY": kimi,
        "AUTH_CODE": auth_code,
        "ROUTE_PROFILE": route_profile,
        "WRITER_MODEL": writer_model,
        "CREWAI_ENABLE_MEMORY": False,
    }
    
    key = get_encryption_key()
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(json.dumps(keys).encode())
    
    with open(API_KEYS_FILE, "wb") as f:
        f.write(encrypted_data)


def load_api_keys():
    """加载API Key（解密）"""
    try:
        if not os.path.exists(API_KEYS_FILE):
            return {
                "DEEPSEEK_API_KEY": "",
                "DASHSCOPE_API_KEY": "",
                "MOONSHOT_API_KEY": "",
                "AUTH_CODE": "",
                "ROUTE_PROFILE": "speed",
                "WRITER_MODEL": "auto",
                "CREWAI_ENABLE_MEMORY": False,
            }
        
        key = get_encryption_key()
        with open(API_KEYS_FILE, "rb") as f:
            encrypted_data = f.read()
        
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data)
        keys = json.loads(decrypted_data.decode())
        
        # 兼容旧版本 key 结构
        return {
            "DEEPSEEK_API_KEY": keys.get("DEEPSEEK_API_KEY", ""),
            "DASHSCOPE_API_KEY": keys.get("DASHSCOPE_API_KEY", ""),
            "MOONSHOT_API_KEY": keys.get("MOONSHOT_API_KEY", ""),
            "AUTH_CODE": keys.get("AUTH_CODE", ""),
            "ROUTE_PROFILE": keys.get("ROUTE_PROFILE", "speed"),
            "WRITER_MODEL": keys.get("WRITER_MODEL", "auto"),
            "CREWAI_ENABLE_MEMORY": False,
        }
    except Exception:
        return {
            "DEEPSEEK_API_KEY": "",
            "DASHSCOPE_API_KEY": "",
            "MOONSHOT_API_KEY": "",
            "AUTH_CODE": "",
            "ROUTE_PROFILE": "speed",
            "WRITER_MODEL": "auto",
            "CREWAI_ENABLE_MEMORY": False,
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
