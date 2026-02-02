# 📊 CNinfo to NotebookLM

Download annual/periodic reports for China A-share stocks and upload them to Google NotebookLM for AI-powered financial analysis.

> **Note**: This tool creates a specialized "Financial Analyst" persona in NotebookLM, based on the methodology from "Hand-holding Financial Reporting".

## ✨ Features

- 📥 **Smart Download**: Fetches last 5 years of annual reports + current year's periodic reports (Q1/Q2/Q3).
- 🤖 **AI Analyst Persona**: Automatically configures the notebook with a professional "Financial Analyst" system prompt for deep mining.
- 📦 **Automated Workflow**: One command to download, create notebook, configure persona, and upload all files.
- 🧹 **Auto Cleanup**: Keeps disk clean by removing temporary PDF files after upload.
- 🔐 **One-Time Auth**: Uses `notebooklm-py` with browser-based check-in for stable authentication.

## 🎯 Use as Claude Skill (Recommended)

### Installation

```bash
# 1. Navigate to your skills directory (e.g. ~/.gemini/antigravity/skills)
cd ~/.gemini/antigravity/skills

# 2. Clone the repository
git clone https://github.com/jarodise/CNinfo2Notebookllm.git cninfo-to-notebooklm

# 3. Install dependencies
cd cninfo-to-notebooklm
pip install -r requirements.txt
playwright install chromium

# 4. Complete initial login (one-time)
notebooklm login
```

### Usage

Simply tell Claude Code:

```text
Use cninfo-to-notebooklm skill to analyze 600519
```

or

```text
Run cninfo-to-notebooklm for Ping An Bank
```

Claude will automatically:

1. Look up stock code (if name provided)
2. Download relevant reports
3. Create & Configure NotebookLM
4. Upload files
5. Return the Notebook link

---

## 🛠️ Manual Usage

You can also run the scripts directly from the terminal:

```bash
# Analyze by Stock Code
python3 scripts/run.py 000519

# Analyze by Stock Name
python3 scripts/run.py "贵州茅台"
```

## 📂 Project Structure

```
cninfo-to-notebooklm/
├── skill.yaml          # Skill definition
├── package.json        # Project metadata
├── SKILL.md            # LLM Instructions
├── scripts/
│   ├── run.py          # Main orchestration
│   ├── download.py     # Download logic
│   └── upload.py       # NotebookLM interaction
└── assets/
    ├── financial_analyst_prompt.txt  # System prompt
    └── stocks.json                   # Stock database
```

## 🔧 Configuration

The "Financial Analyst" persona is defined in `assets/financial_analyst_prompt.txt`. You can modify this file to change how the AI analyzes the financial reports.

## ⚠️ Disclaimer

This tool is for educational and research purposes only. Please ensure you comply with the terms of service of cninfo.com.cn and Google NotebookLM. The financial analysis provided by the AI persona should not be considered professional investment advice.
