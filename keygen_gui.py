import sys
import os
import json
import base64
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QDateEdit, QTextEdit, QFormLayout,
    QMessageBox
)
from PySide6.QtCore import Qt, QDate

# ---------------------------------------------------------
# 配置区：私钥内容
# 这里的私钥必须与你主程序 (src/license.py) 中的公钥配对！
# 我们把之前用 license_cli.py 生成的 private_key.pem 内容硬编码进来
# 这样你把这个 exe 拷到哪里都可以直接发卡
# ---------------------------------------------------------
PRIVATE_KEY_PEM = b"""-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDPCze+RQFnqZmO
VD9xcee3Lq74081zuHBz86Cz8S5zETNHeRrIlKIwCmLGAnquuzag29OIF/pSP5U6
VkRlQbZftMbUsvzd1yaHdWoozVUa6pQ2rQy1K89WWWlanql2jIkSDh/RygJA+DWk
DnZ+MoxuA5btcKICFJqhZMHmM+aJ9NFrBxxIGFoT3zK+6mHOGlD5dItFw4ArvUfG
1xuUEtmScKx+97isyMDGISjeq2YsKjGBUiEWFBf/Cw51vON/gKRDm+yQ60ZG9KpI
WYbr2KhZTqHKuMTTGB17kb3M9yqHkZm6Y8gTGqHxAg5OZh4EiS3ZPVFcvNDZ1oiO
0iSvNGzrAgMBAAECggEAB/ISDIHllGfseFRXgYbRv5kj+N8PaTBFMRhCyFmhNTaO
IOFF1zgMdaY6rAcaL8N18U6OYEdRk794x4u1jqvPa5BqjCPUUywAyb2Yum/9IumE
bC2ZO7+KBPIaw3IHwdv/i4INZiEsbxyS2dlr9JG6eTWAfDar/YxOcpMFPsyYYh54
aI/s2jwESnuDao2KbN52F5UgPIPeckSaKMKi8tdwJqIOlDi8NFnjKM7CWy6KufO8
jJtPxYGvFLgwQIAUco68UUa24aQgG/d4Ait9ChqlPSFDswkF/2uVAGsvz2a/G2ez
AfXvrYu3B9amE98J94PDtntz3Ov6ejw/g0zh1QI2DQKBgQD+Uo1g+/IoVcyxAsuC
Tliehiv9l5Gp5k2H5rvtnsigaP9NXQor6O4Bp17PZY+6jXXmasNnNw6mqfIDieXG
yR9WSKsAXiaS/l8j2BEqiFwKangvRkLS7glEQQMXk0RQvgAIIkvOPou4/UaRf6yI
d/xML80zUp/uQvnvzwKVhNlMzwKBgQDQaNS65Vf+jSAto1UtpNGDpzkhIfsB1EJ5
/cLm9uLs6M1I8Z7Av07xINjIs9eIpHOjE5r3pRoh/hRTuRDlUcKacUHbGS7UrLRx
EFtJUOnsIpEPmfkfU4ge1CfOp5mv1CUhqel3nGtfGUuLrG7RFq4R3JcworTtiAk9
t94Z6VE9JQKBgC0C0VDb5nTrEoo1k20hjp+n4XtFaxtlzk0CMjqRArMZQi4gDF/P
HuieBbKxJ+n9hWNde+31mZs3ssSbkFZJXEl6HQG4qB0V9iKy5/7eGWQiidjcF5Gb
XXp+Ax0WDF458ml+IGqFOVdpRCcWMKQKkFWvlCLEOdgCdJfTzIJH++mTAoGAUn8M
piaenF6UvDwJPZYecTTCgoEG8QRqhAuVGQPlc837ZMJwCvAveXd9GIVH7gja1VSv
ZRPvskD3HuUE8SFaHPR0Exx20yzCCHdnCzCCSDyumzRhzqqsGTf1wfHJ/jXFtPuj
NPuv7OcAZnuNKisGIH/nQRNG9zeAIPQlcLBQvhkCgYBTKF96QdUj6v+3iL4ks2Fi
/n2ApicZpP6ddm2eDAZ5oLpBxm0qLCZUDsUT3QxkaX9V3qqMXGtcfH8HNYFfN50f
dLbYnqmLC1+afWonNrTo1VmULQPgNZ0gM8AQvvcGiwtPSqaQGQIlBD/Rlv138vmo
8J0wjkbzG09WvasOwTNFaA==
-----END PRIVATE KEY-----"""

class KeygenWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI_Novel_Writer 授权码生成器 (内部使用)")
        self.resize(500, 450)
        self.setStyleSheet("""
            QWidget {
                font-family: 'Microsoft YaHei', sans-serif;
                font-size: 14px;
            }
            QLineEdit, QDateEdit, QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px;
            }
            QLineEdit::clear-button {
                width: 0px;
                height: 0px;
                border: none;
                background: transparent;
            }
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """)

        # 尝试加载私钥
        try:
            self.private_key = serialization.load_pem_private_key(
                PRIVATE_KEY_PEM,
                password=None
            )
        except Exception as e:
            QMessageBox.critical(self, "错误", f"私钥加载失败，请检查配置：{e}")
            self.private_key = None

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)

        title = QLabel("🔑 授权码签发系统")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1e293b;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(15)

        # 机器码输入
        self.input_machine = QLineEdit()
        self.input_machine.setPlaceholderText("请输入用户的机器码 (如: A1B2C3D4E5F6)")
        self.input_machine.setClearButtonEnabled(False)
        form.addRow("机器码:", self.input_machine)

        # 到期时间选择
        self.input_date = QDateEdit()
        self.input_date.setCalendarPopup(True)
        # 默认到期时间为一个月后
        default_date = QDate.currentDate().addMonths(1)
        self.input_date.setDate(default_date)
        form.addRow("到期时间:", self.input_date)

        # 备注输入 (可选)
        self.input_note = QLineEdit()
        self.input_note.setPlaceholderText("选填：发卡备注 (如：客户张三)")
        self.input_note.setClearButtonEnabled(False)
        form.addRow("备注信息:", self.input_note)

        main_layout.addLayout(form)

        # 生成按钮
        self.btn_generate = QPushButton("生成授权码")
        self.btn_generate.clicked.connect(self.generate_license)
        main_layout.addWidget(self.btn_generate)

        # 结果输出区
        main_layout.addWidget(QLabel("生成的授权码 (点击复制):"))
        self.output_code = QTextEdit()
        self.output_code.setReadOnly(True)
        self.output_code.setStyleSheet("background-color: #f8fafc;")
        main_layout.addWidget(self.output_code)

        # 复制按钮
        self.btn_copy = QPushButton("📋 一键复制授权码")
        self.btn_copy.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.btn_copy.clicked.connect(self.copy_to_clipboard)
        main_layout.addWidget(self.btn_copy)

    def generate_license(self):
        if not self.private_key:
            QMessageBox.critical(self, "错误", "私钥无效，无法生成！")
            return

        machine_code = self.input_machine.text().strip()
        if not machine_code:
            QMessageBox.warning(self, "提示", "请输入机器码！")
            return

        # 获取日期并设置为当天的 23:59:59
        qdate = self.input_date.date()
        expires_at = datetime(qdate.year(), qdate.month(), qdate.day(), 23, 59, 59)
        
        if expires_at < datetime.now():
            QMessageBox.warning(self, "提示", "到期时间不能早于当前时间！")
            return

        note = self.input_note.text().strip()

        # 构造 Payload
        payload = {
            "machine_code": machine_code,
            "expires_at": expires_at.isoformat(),
            "created_at": datetime.now().isoformat(),
            "note": note
        }

        try:
            # 序列化并签名
            payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
            signature = self.private_key.sign(
                payload_str.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            # 组装最终数据
            license_data = {
                "payload": payload,
                "signature": base64.b64encode(signature).decode('utf-8')
            }

            final_code = base64.b64encode(json.dumps(license_data).encode('utf-8')).decode('utf-8')
            self.output_code.setText(final_code)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成失败: {str(e)}")

    def copy_to_clipboard(self):
        code = self.output_code.toPlainText()
        if code:
            QApplication.clipboard().setText(code)
            self.btn_copy.setText("✅ 已复制！")
            # 2秒后恢复按钮文字
            from PySide6.QtCore import QTimer
            QTimer.singleShot(2000, lambda: self.btn_copy.setText("📋 一键复制授权码"))
        else:
            QMessageBox.information(self, "提示", "还没有生成授权码哦！")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KeygenWindow()
    window.show()
    sys.exit(app.exec())