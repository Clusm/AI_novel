import argparse
import json
import base64
import os
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

KEYS_DIR = "license_keys"
PRIVATE_KEY_FILE = os.path.join(KEYS_DIR, "private_key.pem")
PUBLIC_KEY_FILE = os.path.join(KEYS_DIR, "public_key.pem")

def generate_keys():
    """生成 RSA 密钥对"""
    if not os.path.exists(KEYS_DIR):
        os.makedirs(KEYS_DIR)
        
    print("正在生成 2048 位 RSA 密钥对...")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()

    # 保存私钥 (妥善保管，千万不要放进最终产品代码中！)
    with open(PRIVATE_KEY_FILE, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
        
    # 保存公钥 (用于放到 src/license.py 中)
    with open(PUBLIC_KEY_FILE, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
        
    print(f"密钥对生成成功！\n私钥: {PRIVATE_KEY_FILE}\n公钥: {PUBLIC_KEY_FILE}")
    print("请将 public_key.pem 的内容复制到 src/license.py 中的 public_key_pem 变量处。")

def generate_license(machine_code: str, days: int, note: str):
    """根据机器码和天数生成授权码"""
    if not os.path.exists(PRIVATE_KEY_FILE):
        print(f"错误: 找不到私钥文件 {PRIVATE_KEY_FILE}，请先运行 generate_keys")
        return

    # 加载私钥
    with open(PRIVATE_KEY_FILE, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )

    # 构造 payload
    expires_at = datetime.now() + timedelta(days=days)
    payload = {
        "machine_code": machine_code,
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now().isoformat(),
        "note": note
    }
    
    # 序列化 payload，必须保证排序和分隔符固定，以保证签名一致性
    payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    
    # 使用私钥签名
    signature = private_key.sign(
        payload_str.encode('utf-8'),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    # 组装最终授权数据
    license_data = {
        "payload": payload,
        "signature": base64.b64encode(signature).decode('utf-8')
    }
    
    # 将整个 JSON 进行 Base64 编码，作为最终发给用户的字符串
    final_license_code = base64.b64encode(json.dumps(license_data).encode('utf-8')).decode('utf-8')
    
    print("\n" + "="*50)
    print(f"为机器码 [{machine_code}] 生成了授权")
    print(f"有效期至: {expires_at.strftime('%Y-%m-%d %H:%M:%S')} ({days} 天)")
    print(f"备注: {note}")
    print("="*50)
    print("授权码 (请复制发给用户):")
    print(final_license_code)
    print("="*50 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI_Novel_Writer 授权码签发工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # generate_keys command
    parser_keys = subparsers.add_parser("init", help="初始化/生成 RSA 密钥对")

    # issue command
    parser_issue = subparsers.add_parser("issue", help="签发授权码")
    parser_issue.add_argument("-m", "--machine", required=True, help="用户的机器码")
    parser_issue.add_argument("-d", "--days", type=int, default=30, help="授权天数 (默认 30 天)")
    parser_issue.add_argument("-n", "--note", type=str, default="", help="备注信息 (如用户名)")

    args = parser.parse_args()

    if args.command == "init":
        generate_keys()
    elif args.command == "issue":
        generate_license(args.machine, args.days, args.note)
    else:
        parser.print_help()