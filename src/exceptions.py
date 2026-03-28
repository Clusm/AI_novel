"""
统一异常体系

定义所有业务异常，提供：
1. 清晰的异常层次结构
2. 用户友好的错误信息
3. 异常代码支持
4. 原始异常链追踪
"""

from typing import Optional, Any


class NovelWriterError(Exception):
    """
    基础异常类
    
    所有业务异常的基类，提供统一的异常接口。
    """
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Any] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code or "UNKNOWN_ERROR"
        self.details = details
        self.cause = cause
    
    def __str__(self) -> str:
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message
    
    def to_dict(self) -> dict:
        """转换为字典格式（用于日志和 API 响应）"""
        result = {
            "error": self.code,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        if self.cause:
            result["cause"] = str(self.cause)
        return result


# ===== 配置相关异常 =====

class ConfigError(NovelWriterError):
    """配置错误基类"""
    pass


class ConfigFileError(ConfigError):
    """配置文件错误"""
    
    def __init__(self, file_path: str, message: str = ""):
        super().__init__(
            message or f"配置文件错误: {file_path}",
            code="CONFIG_FILE_ERROR",
            details={"file_path": file_path},
        )


class ConfigValidationError(ConfigError):
    """配置验证错误"""
    
    def __init__(self, field: str, value: Any, reason: str = ""):
        super().__init__(
            f"配置验证失败: {field} - {reason}",
            code="CONFIG_VALIDATION_ERROR",
            details={"field": field, "value": str(value), "reason": reason},
        )


# ===== API 相关异常 =====

class APIError(NovelWriterError):
    """API 错误基类"""
    pass


class APIKeyMissingError(APIError):
    """API Key 缺失"""
    
    def __init__(self, provider: str):
        super().__init__(
            f"缺少 {provider} API Key，请在设置中配置",
            code="API_KEY_MISSING",
            details={"provider": provider},
        )


class APIConnectionError(APIError):
    """API 连接错误"""
    
    def __init__(self, provider: str, original_error: Optional[str] = None):
        message = f"{provider} API 连接失败"
        if original_error:
            message += f": {original_error}"
        super().__init__(
            message,
            code="API_CONNECTION_ERROR",
            details={"provider": provider, "original_error": original_error},
        )


class APIResponseError(APIError):
    """API 响应错误"""
    
    def __init__(self, provider: str, status_code: Optional[int] = None, message: str = ""):
        super().__init__(
            f"{provider} API 响应错误: {message}",
            code="API_RESPONSE_ERROR",
            details={"provider": provider, "status_code": status_code, "response": message},
        )


class APIRateLimitError(APIError):
    """API 速率限制"""
    
    def __init__(self, provider: str, retry_after: Optional[int] = None):
        message = f"{provider} API 请求频率超限"
        if retry_after:
            message += f"，请在 {retry_after} 秒后重试"
        super().__init__(
            message,
            code="API_RATE_LIMIT_ERROR",
            details={"provider": provider, "retry_after": retry_after},
        )


# ===== 项目相关异常 =====

class ProjectError(NovelWriterError):
    """项目错误基类"""
    pass


class ProjectNotFoundError(ProjectError):
    """项目不存在"""
    
    def __init__(self, project_name: str):
        super().__init__(
            f"项目不存在: {project_name}",
            code="PROJECT_NOT_FOUND",
            details={"project_name": project_name},
        )


class ProjectAlreadyExistsError(ProjectError):
    """项目已存在"""
    
    def __init__(self, project_name: str):
        super().__init__(
            f"项目已存在: {project_name}",
            code="PROJECT_ALREADY_EXISTS",
            details={"project_name": project_name},
        )


class ProjectCreationError(ProjectError):
    """项目创建失败"""
    
    def __init__(self, project_name: str, reason: str = ""):
        message = f"创建项目失败: {project_name}"
        if reason:
            message += f" - {reason}"
        super().__init__(
            message,
            code="PROJECT_CREATION_ERROR",
            details={"project_name": project_name, "reason": reason},
        )


class ProjectDeletionError(ProjectError):
    """项目删除失败"""
    
    def __init__(self, project_name: str, reason: str = ""):
        message = f"删除项目失败: {project_name}"
        if reason:
            message += f" - {reason}"
        super().__init__(
            message,
            code="PROJECT_DELETION_ERROR",
            details={"project_name": project_name, "reason": reason},
        )


# ===== 章节相关异常 =====

class ChapterError(NovelWriterError):
    """章节错误基类"""
    pass


class ChapterNotFoundError(ChapterError):
    """章节不存在"""
    
    def __init__(self, project_name: str, chapter_number: int):
        super().__init__(
            f"章节不存在: {project_name} 第{chapter_number}章",
            code="CHAPTER_NOT_FOUND",
            details={"project_name": project_name, "chapter_number": chapter_number},
        )


class ChapterGenerationError(ChapterError):
    """章节生成失败"""
    
    def __init__(
        self,
        project_name: str,
        chapter_number: int,
        reason: str = "",
        cause: Optional[Exception] = None,
    ):
        message = f"生成章节失败: {project_name} 第{chapter_number}章"
        if reason:
            message += f" - {reason}"
        super().__init__(
            message,
            code="CHAPTER_GENERATION_ERROR",
            details={"project_name": project_name, "chapter_number": chapter_number, "reason": reason},
            cause=cause,
        )


class ChapterSaveError(ChapterError):
    """章节保存失败"""
    
    def __init__(self, project_name: str, chapter_number: int, reason: str = ""):
        message = f"保存章节失败: {project_name} 第{chapter_number}章"
        if reason:
            message += f" - {reason}"
        super().__init__(
            message,
            code="CHAPTER_SAVE_ERROR",
            details={"project_name": project_name, "chapter_number": chapter_number, "reason": reason},
        )


class GenerationTimeoutError(ChapterError):
    """生成超时"""
    
    def __init__(self, project_name: str, chapter_number: int, timeout: int):
        super().__init__(
            f"生成超时: {project_name} 第{chapter_number}章（超时 {timeout} 秒）",
            code="GENERATION_TIMEOUT",
            details={"project_name": project_name, "chapter_number": chapter_number, "timeout": timeout},
        )


# ===== 大纲相关异常 =====

class OutlineError(NovelWriterError):
    """大纲错误基类"""
    pass


class OutlineNotFoundError(OutlineError):
    """大纲不存在"""
    
    def __init__(self, project_name: str):
        super().__init__(
            f"大纲不存在: {project_name}",
            code="OUTLINE_NOT_FOUND",
            details={"project_name": project_name},
        )


class OutlineTooShortError(OutlineError):
    """大纲过短"""
    
    def __init__(self, project_name: str, current_length: int, min_length: int):
        super().__init__(
            f"大纲内容过短: {project_name}（当前 {current_length} 字，最少需要 {min_length} 字）",
            code="OUTLINE_TOO_SHORT",
            details={"project_name": project_name, "current_length": current_length, "min_length": min_length},
        )


# ===== 导出相关异常 =====

class ExportError(NovelWriterError):
    """导出错误基类"""
    pass


class ExportFormatNotSupportedError(ExportError):
    """不支持的导出格式"""
    
    def __init__(self, format: str):
        super().__init__(
            f"不支持的导出格式: {format}",
            code="EXPORT_FORMAT_NOT_SUPPORTED",
            details={"format": format},
        )


class ExportFailedError(ExportError):
    """导出失败"""
    
    def __init__(self, project_name: str, format: str, reason: str = ""):
        message = f"导出失败: {project_name} -> {format}"
        if reason:
            message += f" - {reason}"
        super().__init__(
            message,
            code="EXPORT_FAILED",
            details={"project_name": project_name, "format": format, "reason": reason},
        )


# ===== 授权相关异常 =====

class LicenseError(NovelWriterError):
    """授权错误基类"""
    pass


class LicenseInvalidError(LicenseError):
    """授权码无效"""
    
    def __init__(self, reason: str = ""):
        message = "授权码无效"
        if reason:
            message += f": {reason}"
        super().__init__(
            message,
            code="LICENSE_INVALID",
            details={"reason": reason},
        )


class LicenseExpiredError(LicenseError):
    """授权已过期"""
    
    def __init__(self, expired_at: str):
        super().__init__(
            f"授权已于 {expired_at} 过期",
            code="LICENSE_EXPIRED",
            details={"expired_at": expired_at},
        )


class LicenseMachineCodeMismatchError(LicenseError):
    """机器码不匹配"""
    
    def __init__(self):
        super().__init__(
            "机器码不匹配，该授权码不能在本机使用",
            code="LICENSE_MACHINE_CODE_MISMATCH",
        )


# ===== Agent 相关异常 =====

class AgentError(NovelWriterError):
    """Agent 错误基类"""
    pass


class AgentCreationError(AgentError):
    """Agent 创建失败"""
    
    def __init__(self, role: str, reason: str = ""):
        message = f"创建 Agent 失败: {role}"
        if reason:
            message += f" - {reason}"
        super().__init__(
            message,
            code="AGENT_CREATION_ERROR",
            details={"role": role, "reason": reason},
        )


class AgentExecutionError(AgentError):
    """Agent 执行失败"""
    
    def __init__(self, role: str, task: str, reason: str = ""):
        message = f"Agent 执行失败: {role} - {task}"
        if reason:
            message += f" - {reason}"
        super().__init__(
            message,
            code="AGENT_EXECUTION_ERROR",
            details={"role": role, "task": task, "reason": reason},
        )


# ===== 工作空间相关异常 =====

class WorkspaceError(NovelWriterError):
    """工作空间错误基类"""
    pass


class WorkspaceNotSetError(WorkspaceError):
    """工作空间未设置"""
    
    def __init__(self):
        super().__init__(
            "工作空间未设置，请先选择工作空间目录",
            code="WORKSPACE_NOT_SET",
        )


class WorkspaceAccessError(WorkspaceError):
    """工作空间访问错误"""
    
    def __init__(self, path: str, reason: str = ""):
        message = f"无法访问工作空间: {path}"
        if reason:
            message += f" - {reason}"
        super().__init__(
            message,
            code="WORKSPACE_ACCESS_ERROR",
            details={"path": path, "reason": reason},
        )


# ===== 文件相关异常 =====

class FileError(NovelWriterError):
    """文件错误基类"""
    pass


class FileNotFoundError(FileError):
    """文件不存在"""
    
    def __init__(self, file_path: str):
        super().__init__(
            f"文件不存在: {file_path}",
            code="FILE_NOT_FOUND",
            details={"file_path": file_path},
        )


class FileReadError(FileError):
    """文件读取错误"""
    
    def __init__(self, file_path: str, reason: str = ""):
        message = f"读取文件失败: {file_path}"
        if reason:
            message += f" - {reason}"
        super().__init__(
            message,
            code="FILE_READ_ERROR",
            details={"file_path": file_path, "reason": reason},
        )


class FileWriteError(FileError):
    """文件写入错误"""
    
    def __init__(self, file_path: str, reason: str = ""):
        message = f"写入文件失败: {file_path}"
        if reason:
            message += f" - {reason}"
        super().__init__(
            message,
            code="FILE_WRITE_ERROR",
            details={"file_path": file_path, "reason": reason},
        )


# ===== 验证相关异常 =====

class ValidationError(NovelWriterError):
    """验证错误基类"""
    pass


class ValidationRequiredError(ValidationError):
    """必填字段缺失"""
    
    def __init__(self, field: str):
        super().__init__(
            f"必填字段缺失: {field}",
            code="VALIDATION_REQUIRED",
            details={"field": field},
        )


class ValidationFormatError(ValidationError):
    """格式验证失败"""
    
    def __init__(self, field: str, expected_format: str):
        super().__init__(
            f"字段格式错误: {field}（期望格式: {expected_format}）",
            code="VALIDATION_FORMAT",
            details={"field": field, "expected_format": expected_format},
        )


# ===== 辅助函数 =====

def wrap_exception(
    original_exception: Exception,
    wrapper_class: type,
    message: str = "",
    **kwargs,
) -> NovelWriterError:
    """
    将原始异常包装为业务异常
    
    参数:
        original_exception: 原始异常
        wrapper_class: 包装异常类
        message: 自定义消息
        **kwargs: 传递给包装异常的额外参数
    
    返回:
        包装后的业务异常
    """
    return wrapper_class(
        message or str(original_exception),
        cause=original_exception,
        **kwargs,
    )
