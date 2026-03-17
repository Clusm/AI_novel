import re
from PySide6.QtGui import (
    QColor,
    QFont,
    QSyntaxHighlighter,
    QTextCharFormat,
)

class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rules = []
        
        # 1. Headers (# H1, ## H2, etc.)
        h1_format = QTextCharFormat()
        h1_format.setForeground(QColor("#2563eb"))  # Blue-600
        h1_format.setFontWeight(QFont.Bold)
        h1_format.setFontPointSize(18)
        self.rules.append((re.compile(r"^# [^\n]*"), h1_format))
        
        h2_format = QTextCharFormat()
        h2_format.setForeground(QColor("#0ea5e9"))  # Sky-500
        h2_format.setFontWeight(QFont.Bold)
        h2_format.setFontPointSize(16)
        self.rules.append((re.compile(r"^## [^\n]*"), h2_format))
        
        h3_format = QTextCharFormat()
        h3_format.setForeground(QColor("#0284c7"))  # Sky-600
        h3_format.setFontWeight(QFont.Bold)
        h3_format.setFontPointSize(14)
        self.rules.append((re.compile(r"^### [^\n]*"), h3_format))
        
        # 4. Bold (**text**)
        bold_format = QTextCharFormat()
        bold_format.setFontWeight(QFont.Bold)
        bold_format.setForeground(QColor("#1e293b"))  # Slate-800
        self.rules.append((re.compile(r"\*\*[^\n]*\*\*"), bold_format))
        
        # 5. Lists (- item, * item)
        list_format = QTextCharFormat()
        list_format.setForeground(QColor("#d97706"))  # Amber-600
        self.rules.append((re.compile(r"^\s*[-*+] [^\n]*"), list_format))
        
        # 6. Quotes (> text)
        quote_format = QTextCharFormat()
        quote_format.setForeground(QColor("#64748b"))  # Slate-500
        quote_format.setFontItalic(True)
        self.rules.append((re.compile(r"^> [^\n]*"), quote_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)
