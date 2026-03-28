import os
import sys
import json
import base64
import hashlib
import platform
import subprocess
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature

class LicenseManager:
    def __init__(self):
        # 你的应用专属公钥，用于验证签名
        self.public_key_pem = b"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzws3vkUBZ6mZjlQ/cXHn
ty6u+NPNc7hwc/Ogs/EucxEzR3kayJSiMApixgJ6rrs2oNvTiBf6Uj+VOlZEZUG2
X7TG1LL83dcmh3VqKM1VGuqUNq0MtSvPVllpWp6pdoyJEg4f0coCQPg1pA52fjKM
bgOW7XCiAhSaoWTB5jPmifTRawccSBhaE98yvuphzhpQ+XSLRcOAK71HxtcblBLZ
knCsfve4rMjAxiEo3qtmLCoxgVIhFhQX/wsOdbzjf4CkQ5vskOtGRvSqSFmG69io
WU6hyrjE0xgde5G9zPcqh5GZumPIExqh8QIOTmYeBIkt2T1RXLzQ2daIjtIkrzRs
6wIDAQAB
-----END PUBLIC KEY-----"""
        self.public_key = None
        self._load_public_key()

    def _load_public_key(self):
        """加载硬编码的公钥"""
        try:
            if b"YOUR_PUBLIC_KEY_HERE" not in self.public_key_pem:
                self.public_key = serialization.load_pem_public_key(self.public_key_pem)
        except Exception as e:
            print(f"公钥加载失败: {e}")

    def get_machine_code(self) -> str:
        """
        获取机器码，绑定主板和硬盘序列号
        这里使用跨平台的 hashlib 生成一个较短的机器指纹
        """
        machine_info = ""
        try:
            if platform.system() == "Windows":
                # 获取主板序列号
                cmd = 'wmic baseboard get serialnumber'
                output = subprocess.check_output(cmd, shell=True).decode('utf-8')
                serial = ''.join(output.split('\n')[1:]).strip()
                machine_info += serial
                
                # 尝试获取硬盘序列号
                cmd = 'wmic diskdrive get serialnumber'
                output = subprocess.check_output(cmd, shell=True).decode('utf-8')
                disk = ''.join(output.split('\n')[1:]).strip()
                machine_info += disk
            else:
                # 对于 Linux/Mac (简单后备方案)
                import uuid
                machine_info = str(uuid.getnode())
        except Exception:
            # 万一获取失败，退回到更基础的指纹
            machine_info = platform.node() + platform.processor()

        if not machine_info:
            machine_info = "UNKNOWN_MACHINE"

        # 使用 SHA-256 计算哈希，并截取前 16 位作为展示用机器码
        hash_obj = hashlib.sha256(machine_info.encode('utf-8')).hexdigest()
        return hash_obj[:16].upper()

    def verify_license(self, license_code: str) -> dict:
        """
        验证授权码
        :param license_code: 用户输入的授权码 (Base64 编码的 JSON + 签名)
        :return: { 'valid': bool, 'message': str, 'expires_at': str }
        """
        if not self.public_key:
            return {"valid": False, "message": "系统未配置公钥，无法验证", "expires_at": None}

        if not license_code:
            return {"valid": False, "message": "授权码为空", "expires_at": None}

        try:
            # 1. 解码 Base64
            decoded_data = base64.b64decode(license_code).decode('utf-8')
            license_data = json.loads(decoded_data)
            
            payload = license_data.get("payload", {})
            signature_b64 = license_data.get("signature", "")
            
            if not payload or not signature_b64:
                return {"valid": False, "message": "授权码格式错误", "expires_at": None}

            # 2. 验证机器码
            machine_code = self.get_machine_code()
            if payload.get("machine_code") != machine_code:
                return {"valid": False, "message": "机器码不匹配，该授权码不能在本机使用", "expires_at": None}

            # 3. 验证有效期
            expires_at_str = payload.get("expires_at")
            if expires_at_str:
                expires_at = datetime.fromisoformat(expires_at_str)
                if datetime.now() > expires_at:
                    return {"valid": False, "message": f"授权已于 {expires_at_str[:10]} 过期", "expires_at": expires_at_str}

            # 4. 验证 RSA 签名
            # 将 payload 重新序列化为字符串（确保排序一致）
            payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
            signature = base64.b64decode(signature_b64)
            
            self.public_key.verify(
                signature,
                payload_str.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return {"valid": True, "message": "授权有效", "expires_at": expires_at_str}

        except InvalidSignature:
            return {"valid": False, "message": "授权码签名验证失败，可能是伪造的", "expires_at": None}
        except Exception as e:
            return {"valid": False, "message": f"授权码解析失败: {str(e)}", "expires_at": None}

# 单例实例
license_manager = LicenseManager()