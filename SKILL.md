---
name: cninfo-to-notebooklm
description: Use when user wants to analyze China stock reports (A-share or Hong Kong), upload annual/quarterly reports to NotebookLM, or research a Chinese listed company's financials
---

# CNinfo to NotebookLM

## Overview

Download annual and periodic reports for China A-share and Hong Kong stocks from cninfo.com.cn and upload them to NotebookLM for AI-powered analysis with a specialized "Financial Analyst" persona.

## When to Use

- User provides a China stock name or code (A-share or Hong Kong)
- User wants to analyze a company's financial reports
- User asks to "download reports" or "research" a Chinese stock
- User wants to upload stock reports to NotebookLM

## Supported Markets

| Market | Code Pattern | Examples |
| :--- | :--- | :--- |
| A-share | 6-digit codes (0xxxxx, 3xxxxx, 6xxxxx) | 600519 (贵州茅台), 000001 (平安银行) |
| Hong Kong | 5-digit codes (00xxx, 01xxx, 02xxx, 09xxx) | 00700 (腾讯控股), 09988 (阿里巴巴) |

## Core Workflow

```text
User provides stock name/code
        ↓
1. Look up stock in database (auto-detect market)
        ↓
2. Download reports from cninfo:
   - Last 5 years annual reports (年度报告)
   - Current year: Q1, semi-annual, Q3 reports
        ↓
3. Create NotebookLM notebook
        ↓
4. Configure "Financial Analyst" persona with custom prompt
        ↓
5. Upload all PDFs as sources
        ↓
6. Return notebook ID ✅
```

## Step-by-Step Instructions

### Step 0: Environment Setup (First Run Only)

**Crucial**: Before running the script, verify the environment is ready.

1. **Check Dependencies**: Verify if the dependencies are installed (specifically `notebooklm` and `playwright`).
2. **Install**: If dependencies are missing or this is the first run, execute the installation script:

   ```bash
   chmod +x install.sh && ./install.sh
   ```

3. **Authenticate**: Ensure the user has authenticated with NotebookLM (`notebooklm login`). If not, ask them to do so.

### Step 1: Run Main Orchestration Script

Run the script from the skill directory:

```bash
python3 scripts/run.py <stock_code_or_name>
```

Examples:

- `python3 scripts/run.py 600350` - A-share stock
- `python3 scripts/run.py 山东高速` - A-share by name
- `python3 scripts/run.py 00700` - Hong Kong stock (Tencent)
- `python3 scripts/run.py 腾讯控股` - Hong Kong by name

This script handles everything:

1. Downloads reports to a temp directory.
2. Creates a NotebookLM notebook.
3. Configures the notebook with `assets/financial_analyst_prompt.txt`.
4. Uploads all PDFs.
5. Cleans up temp files.

### Step 2: Report to User

Provide:

- ✅ Number of reports downloaded & uploaded
- 📚 NotebookLM notebook ID
- 📊 Market type (A-share or Hong Kong)
- 💡 Remind user the notebook creates a "Financial Analyst" persona for deep analysis.

## Configuration

The skill uses a custom system prompt located at:
`assets/financial_analyst_prompt.txt`

This prompt configures NotebookLM to act as a "Financial Report Analyst" based on "Hand-holding Financial Reporting" methodology.

## Error Handling

| Error | Solution |
| :--- | :--- |
| Stock not found | Check if code is valid A-share or Hong Kong stock |
| NotebookLM CLI not found | Ensure `notebooklm-py` matches `requirements.txt` and is in PATH |
| Auth missing | Run `notebooklm login` to authenticate via browser |
| Upload failed | Check network connection and NotebookLM service status |

## Dependencies

- Python 3.8+
- `httpx` package
- `notebooklm-py` package
- `playwright` (for authentication)

## Quick Reference

### A-share Report Types

| Report Type | Category Code | Period |
| :--- | :--- | :--- |
| Annual | `category_ndbg_szsh` | Previous 5 years |
| Semi-Annual | `category_bndbg_szsh` | Current year |
| Q1 Report | `category_yjdbg_szsh` | Current year |
| Q3 Report | `category_sjdbg_szsh` | Current year |

### Hong Kong Stock Differences

| Aspect | A-share | Hong Kong |
| :--- | :--- | :--- |
| Market code | `szse` | `hke` |
| Categories | Uses category codes | Empty categories |
| Search key | Uses Chinese search terms | Empty search key |
| Report naming | `YYYY年年度报告` | May use Arabic/Chinese numerals |
| Search period | Following year (March-June) | Same year or following year |
