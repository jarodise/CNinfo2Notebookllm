# CNinfo to NotebookLM

从巨潮资讯网自动下载 A 股上市公司财报，并上传至 Google NotebookLM，利用 AI 驱动的“财务分析师”角色进行深度分析。

> 💡 **提示**: 本工具会自动为 NotebookLM 配置一个专业的“财务分析师”角色（基于《手把手教你读财报》方法论），帮助你进行财报排雷和估值分析。

## ✨ 核心功能

- 📥 **智能下载**: 自动下载近 5 年年报 + 当年所有定期报告（一季报、中报、三季报）。
- 🤖 **AI 分析师**: 自动植入专用 System Prompt，进行风险检测、估值分析和“击球区”判断。
- 📦 **全自动流程**: 一键完成下载、笔记本创建、角色配置和文件上传。
- 🧹 **自动清理**: 上传完成后自动清理临时 PDF 文件，保持整洁。
- 🔐 **稳定登录**: 使用 `notebooklm-py` 配合浏览器自动化，确保鉴权稳定可靠。

## 🚀 使用方法

### 安装步骤

1. **安装 Skill**
   在你的 Agent 终端中运行以下命令：

   ```bash
   npx skills add jarodise/CNinfo2Notebookllm
   ```

2. **安装依赖** (首次运行)
   - **如果你使用 Agent**: 直接要求 Agent "开始分析股票"，它会自动检测并运行安装脚本。
   - **如果你手动运行**: 请进入目录并运行脚本：

     ```bash
     cd <skill_directory> && ./install.sh
     ```

3. **认证登录**
   如果你之前没用过 NotebookLM，请先登录：

   ```bash
   notebooklm login
   ```

### 运行工具

你可以直接在终端运行工具：

```bash
# 按股票代码分析
python3 scripts/run.py 600519

# 按股票名称分析
python3 scripts/run.py "贵州茅台"
```

### 配合 AI Agent 使用

本工具设计为可供拥有 Shell 权限的 AI Agent (如 Claude, ChatGPT 等) 直接调用。

**Agent 指令:**

1. **环境准备 (首次运行)**: 检查依赖，若未安装则执行 `./install.sh`。
2. **执行分析**: 运行 `python3 scripts/run.py <股票名称或代码>`。
3. **获取结果**: 解析 JSON 输出或读取标准输出中的 Notebook 链接。

## 📂 项目结构

```
cninfo-to-notebooklm/
├── package.json        # 项目元数据
├── SKILL.md            # LLM 指令和上下文说明
├── install.sh          # 依赖安装脚本
├── scripts/
│   ├── run.py          # 主流程控制脚本
│   ├── download.py     # 巨潮资讯下载逻辑
│   └── upload.py       # NotebookLM 交互逻辑
└── assets/
    ├── financial_analyst_prompt.txt  # AI 分析师 System Prompt
    └── stocks.json                   # 股票数据库
```

## ⚠️ 免责声明

本工具仅供教育和研究使用。请确保遵守巨潮资讯网 (cninfo.com.cn) 和 Google NotebookLM 的服务条款。AI 提供的财务分析仅供参考，不构成任何投资建议。
