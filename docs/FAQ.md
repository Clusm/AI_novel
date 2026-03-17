# 常见问题（FAQ）

## 1）程序启动慢

可能原因：
- 如果使用的是单文件版 (onefile)，首次启动需要解压依赖到临时目录（需 30-60 秒）。
- 如果使用的是安装版/文件夹版 (onedir)，启动速度应较快（3-5 秒）。

建议：
- 推荐使用安装版 (onedir + Inno Setup)。
- 查看 `%APPDATA%\AI_Novel_Writer\logs\ai_novel_startup.log` 获取启动日志。

## 2）API 验证失败

常见原因：
- Key 填错/过期。
- 网络环境无法访问对应服务。
- 短时间请求过多触发限流。

建议：
- 更换 Key 后重新验证。
- 稍等 1–5 分钟再试。
- 检查网络代理/防火墙。

## 3）找不到配置文件 / 配置丢失

说明：
- API Key 和配置文件已迁移至系统标准数据目录：
  - Windows: `%APPDATA%\AI_Novel_Writer`
  - Linux/Mac: `~/.config/ai_novel_writer`
- 这意味着即使您移动了 EXE 文件，配置也会保留。

## 4）生成章节偏短（<3500 字）

说明：
- 项目已在保存前做字数校验，不足会自动扩写补足。
- 如果仍偏短，通常是扩写环节被中断或输出被截断。

建议：
- 查看运行日志，确认是否出现“扩写补足”提示。
- 尝试切换更稳定的链路策略或主写模型。

## 5）PowerShell 无法激活虚拟环境

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\.venv\Scripts\Activate.ps1
```

## 6）打包失败或提示“拒绝访问”

常见原因：
- `dist/AI_Novel_Writer` 文件夹或其中的 EXE 正在运行，导致无法覆盖写入。

解决：
- 先关闭正在运行的程序再打包。
