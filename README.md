# CNinfo to NotebookLM

Download A-share stock reports from cninfo.com.cn and upload them to NotebookLM for AI-powered analysis with a specialized "Financial Analyst" persona.

> 💡 **Note**: This tool automatically configures NotebookLM with a professional "Financial Analyst" persona based on the "Hand-holding Financial Reporting" methodology.

## ✨ Features

- 📥 **Smart Download**: Automatically fetches annual reports (last 5 years) + all periodic reports for the current year (Q1/Semi/Q3).
- 🤖 **AI Analyst Persona**: Auto-injects a specialized System Prompt for risk detection, valuation, and "strike zone" analysis.
- 📦 **Automated Workflow**: One-step download, notebook creation, persona configuration, and file upload.
- 🧹 **Auto Cleanup**: Automatically removes temporary PDF files after upload.
- 🔐 **Stable Auth**: Uses `notebooklm-py` with browser automation for reliable authentication.

## 🚀 Usage

### Installation (Recommended)

1. Use `npx` to install this skill directly to your agent:

   ```bash
   npx skills add jarodise/CNinfo2Notebookllm
   ```

2. Install dependencies (First time only):

   ```bash
   # Enter the skill directory (e.g., ~/.gemini/antigravity/skills/cninfo-to-notebooklm)
   cd <skill_directory>
   
   # Run the setup script
   ./install.sh
   # OR
   pip install -r requirements.txt && playwright install chromium
   ```

3. Authenticate with NotebookLM:

   ```bash
   notebooklm login
   ```

### Manual Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/jarodise/CNinfo2Notebookllm.git
   cd CNinfo2Notebookllm
   ```

2. Run setup:

   ```bash
   ./install.sh
   ```

3. Authenticate:

   ```bash
   notebooklm login
   ```

### Running the Tool

You can run the tool directly from the terminal:

```bash
# Analyze by Stock Code
python3 scripts/run.py 600519

# Analyze by Stock Name
python3 scripts/run.py "贵州茅台"
```

### Using with AI Agents

This tool is designed to be easily used by AI agents (Claude, ChatGPT, etc.) that have shell access.

**Agent Instructions:**

1. Execute `python3 scripts/run.py <stock_name_or_code>`
2. Parse the JSON output (if needed) or read the standard output for the Notebook URL.

## 📂 Project Structure

```
cninfo-to-notebooklm/
├── skill.yaml          # Skill definition (for compatible agents)
├── package.json        # Project metadata
├── SKILL.md            # LLM Instructions / Context
├── scripts/
│   ├── run.py          # Main orchestration script
│   ├── download.py     # Download logic
│   └── upload.py       # NotebookLM interaction logic
└── assets/
    ├── financial_analyst_prompt.txt  # System Prompt
    └── stocks.json                   # Stock database
```

## ⚠️ Disclaimer

For educational and research purposes only. Please ensure compliance with cninfo.com.cn and Google NotebookLM terms of service. Financial analysis provided by AI is for reference only and does not constitute investment advice.
