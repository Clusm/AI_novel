class Colors:
    PRIMARY_50 = "#EFF6FF"
    PRIMARY_100 = "#DBEAFE"
    PRIMARY_200 = "#BFDBFE"
    PRIMARY_300 = "#93C5FD"
    PRIMARY_400 = "#60A5FA"
    PRIMARY_500 = "#3B82F6"
    PRIMARY_600 = "#2563EB"
    PRIMARY_700 = "#1D4ED8"
    PRIMARY_800 = "#1E40AF"
    PRIMARY_900 = "#1E3A8A"

    GRAY_50 = "#F8FAFC"
    GRAY_100 = "#F1F5F9"
    GRAY_200 = "#E2E8F0"
    GRAY_300 = "#CBD5E1"
    GRAY_400 = "#94A3B8"
    GRAY_500 = "#64748B"
    GRAY_600 = "#475569"
    GRAY_700 = "#334155"
    GRAY_800 = "#1E293B"
    GRAY_900 = "#0F172A"

    SUCCESS_50 = "#F0FDF4"
    SUCCESS_100 = "#DCFCE7"
    SUCCESS_200 = "#BBF7D0"
    SUCCESS_300 = "#86EFAC"
    SUCCESS_500 = "#22C55E"
    SUCCESS_600 = "#16A34A"

    WARNING_50 = "#FFFBEB"
    WARNING_100 = "#FEF3C7"
    WARNING_200 = "#FDE68A"
    WARNING_300 = "#FCD34D"
    WARNING_500 = "#F59E0B"
    WARNING_600 = "#D97706"

    ERROR_50 = "#FEF2F2"
    ERROR_100 = "#FEE2E2"
    ERROR_200 = "#FECACA"
    ERROR_300 = "#FCA5A5"
    ERROR_500 = "#EF4444"
    ERROR_600 = "#DC2626"

    PURPLE_50 = "#F5F3FF"
    PURPLE_100 = "#EDE9FE"
    PURPLE_500 = "#A855F7"
    PURPLE_600 = "#7C3AED"

    WHITE = "#FFFFFF"
    BLACK = "#000000"
    TRANSPARENT = "transparent"

    TEXT_PRIMARY = GRAY_900
    TEXT_SECONDARY = GRAY_600
    TEXT_TERTIARY = GRAY_500
    TEXT_MUTED = GRAY_400

    SURFACE = WHITE
    BACKGROUND = GRAY_50
    BORDER = GRAY_200
    BORDER_LIGHT = GRAY_100

    GRADIENT_PRIMARY = f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {PRIMARY_500}, stop:1 {PRIMARY_600})"

    # 统计卡片专属配色
    STAT_CARD_CHAPTERS_BG = PRIMARY_50  # 已生成章节 - 蓝色
    STAT_CARD_CHAPTERS_TEXT = PRIMARY_600
    STAT_CARD_WORDS_BG = SUCCESS_50  # 总字数 - 绿色
    STAT_CARD_WORDS_TEXT = SUCCESS_600
    STAT_CARD_AVG_BG = WARNING_50  # 平均字数 - 黄色
    STAT_CARD_AVG_TEXT = WARNING_600
    STAT_CARD_TOTAL_BG = PURPLE_50  # 预计总章数 - 紫色
    STAT_CARD_TOTAL_TEXT = PURPLE_600


class Typography:
    WEIGHT_LIGHT = 300
    WEIGHT_REGULAR = 400
    WEIGHT_MEDIUM = 500
    WEIGHT_SEMIBOLD = 600
    WEIGHT_BOLD = 700
    WEIGHT_EXTRABOLD = 800

    # 字体栈
    FONT_CHINESE = "-apple-system, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif"
    FONT_ENGLISH = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif"
    FONT_MONO = "'JetBrains Mono', 'Fira Code', 'Consolas', monospace"

    DISPLAY = {"size": "32px", "weight": WEIGHT_EXTRABOLD, "letter_spacing": "-0.02em"}
    H1 = {"size": "28px", "weight": WEIGHT_BOLD, "letter_spacing": "-0.01em"}
    H2 = {"size": "20px", "weight": WEIGHT_SEMIBOLD, "letter_spacing": "0"}
    H3 = {"size": "16px", "weight": WEIGHT_SEMIBOLD, "letter_spacing": "0"}
    H4 = {"size": "14px", "weight": WEIGHT_MEDIUM, "letter_spacing": "0"}

    BODY = {"size": "14px", "weight": WEIGHT_REGULAR, "letter_spacing": "0"}
    BODY_SMALL = {"size": "12px", "weight": WEIGHT_REGULAR, "letter_spacing": "0"}
    CAPTION = {"size": "11px", "weight": WEIGHT_MEDIUM, "letter_spacing": "0.01em"}
    MICRO = {"size": "10px", "weight": WEIGHT_REGULAR, "letter_spacing": "0.02em"}


class Spacing:
    XS = "4px"
    SM = "8px"
    MD = "12px"
    LG = "16px"
    XL = "24px"
    XL2 = "32px"


class Radius:
    NONE = "0px"
    SM = "4px"
    MD = "6px"
    LG = "8px"
    XL = "12px"
    XL2 = "16px"
    FULL = "9999px"


class Shadows:
    SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    XL = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"


class Transitions:
    FAST = "150ms ease"
    NORMAL = "200ms ease"
    SLOW = "300ms ease"


class ZIndex:
    DROPDOWN = 1000
    STICKY = 1020
    FIXED = 1030
    MODAL_BACKDROP = 1040
    MODAL = 1050
    POPOVER = 1060
    TOOLTIP = 1070


class Breakpoints:
    SM = 640
    MD = 768
    LG = 1024
    XL = 1280
    XL2 = 1536


class Sizes:
    INPUT_HEIGHT_SM = 28
    INPUT_HEIGHT_MD = 32
    INPUT_HEIGHT_LG = 36

    BUTTON_HEIGHT_SM = 24
    BUTTON_HEIGHT_MD = 28
    BUTTON_HEIGHT_LG = 32

    BUTTON_MIN_WIDTH = 72
    BUTTON_MIN_WIDTH_LG = 100

    ICON_SIZE_SM = 14
    ICON_SIZE_MD = 16
    ICON_SIZE_LG = 20
    ICON_SIZE_XL = 24

    TITLE_BAR_HEIGHT = 36

    SIDEBAR_WIDTH = 220
    SIDEBAR_WIDTH_COLLAPSED = 48

    DIALOG_WIDTH_SM = 360
    DIALOG_WIDTH_MD = 420
    DIALOG_WIDTH_LG = 500

    CARD_WIDTH_SM = 160
    CARD_WIDTH_MD = 200
    CARD_WIDTH_LG = 260

    TAB_HEIGHT = 36
    STAT_CARD_HEIGHT = 72


class Icons:
    """图标映射表 - 使用 Emoji 作为图标"""
    # 操作类
    NEW = "➕"
    DELETE = "🗑️"
    EDIT = "✏️"
    SAVE = "💾"
    COPY = "📋"
    SETTINGS = "⚙️"
    SEARCH = "🔍"

    # 文档类
    FILE = "📄"
    CHAPTER = "📖"
    FOLDER = "📁"

    # 功能类
    GENERATE = "✨"
    STOP = "⏹️"
    PLAY = "▶️"
    PAUSE = "⏸️"

    # 导航类
    PREV = "◀"
    NEXT = "▶"
    UP = "▲"
    DOWN = "▼"

    # 状态类
    SUCCESS = "✅"
    WARNING = "⚠️"
    ERROR = "❌"
    INFO = "ℹ️"


DESIGN_TOKENS = {
    "colors": Colors,
    "typography": Typography,
    "spacing": Spacing,
    "radius": Radius,
    "shadows": Shadows,
    "transitions": Transitions,
    "z_index": ZIndex,
    "breakpoints": Breakpoints,
    "sizes": Sizes,
    "icons": Icons,
}
