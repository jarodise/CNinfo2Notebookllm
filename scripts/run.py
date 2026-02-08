#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNinfo to NotebookLM - Main Orchestration Script

Downloads A-share and Hong Kong stock reports from cninfo.com.cn and uploads to NotebookLM.
"""

import sys
import os
import json
import tempfile
import shutil

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from download import CnInfoDownloader
import datetime


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python run.py <stock_code_or_name>")
        print("")
        print("Examples:")
        print("  python run.py 600519       # A-share by code")
        print("  python run.py 贵州茅台      # A-share by name")
        print("  python run.py 00700        # Hong Kong stock by code")
        print("  python run.py 腾讯控股      # Hong Kong stock by name")
        print("")
        print("This will:")
        print("  1. Download annual reports (last 5 years)")
        print("  2. Download periodic reports (Q1, semi-annual, Q3)")
        print("  3. Upload all to NotebookLM")
        sys.exit(1)

    stock_input = sys.argv[1]

    # Initialize downloader
    downloader = CnInfoDownloader()

    # Find stock (now returns market too)
    stock_code, stock_info, market = downloader.find_stock(stock_input)
    if not stock_code:
        print(f"❌ Stock not found: {stock_input}", file=sys.stderr)
        sys.exit(1)

    stock_name = stock_info.get("zwjc", stock_code)
    market_display = "Hong Kong" if market == "hke" else "A-share"
    print(f"📊 Found stock: {stock_code} ({stock_name}) [{market_display}]")

    # Create temp directory
    output_dir = tempfile.mkdtemp(prefix="cninfo_reports_")
    print(f"📁 Temp directory: {output_dir}")

    # Calculate years
    current_year = datetime.datetime.now().year
    annual_years = list(range(current_year - 5, current_year))

    # Download annual reports
    print(f"\n📥 Downloading annual reports for: {annual_years}")
    annual_files = downloader.download_annual_reports(
        stock_code, annual_years, output_dir, market
    )

    # Download periodic reports
    print(f"\n📥 Downloading periodic reports (Q1, semi-annual, Q3)...")
    periodic_files = downloader.download_periodic_reports(
        stock_code, current_year, output_dir, market
    )

    if not periodic_files:
        print(f"   No {current_year} reports yet, trying {current_year - 1}...")
        periodic_files = downloader.download_periodic_reports(
            stock_code, current_year - 1, output_dir, market
        )
    elif len(periodic_files) < 3:
        print(f"   Checking {current_year - 1} for additional reports...")
        prev_year_files = downloader.download_periodic_reports(
            stock_code, current_year - 1, output_dir, market
        )
        periodic_files.extend(prev_year_files)

    all_files = annual_files + periodic_files

    if not all_files:
        print("❌ No reports downloaded")
        shutil.rmtree(output_dir)
        sys.exit(1)

    print(f"\n{'=' * 50}")
    print(f"✅ Downloaded {len(all_files)} reports")

    # Check if notebooklm is available
    if not shutil.which("notebooklm"):
        print("\n⚠️ NotebookLM CLI not found!")
        print("Install with: pip install notebooklm-py playwright")
        print("Then: playwright install chromium")
        print("Then authenticate with: notebooklm login")
        print(f"\n📁 Files saved to: {output_dir}")
        print("You can manually upload these PDFs to NotebookLM")

        # Output JSON for manual use
        result = {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "market": market,
            "output_dir": output_dir,
            "files": all_files,
        }
        print("\n---JSON_OUTPUT---")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0)

    # Upload to NotebookLM
    print(f"\n📤 Uploading to NotebookLM...")

    from upload import (
        create_notebook,
        upload_all_sources,
        cleanup_temp_files,
        configure_notebook,
    )

    notebook_title = f"{stock_name} 财务报告"
    notebook_id = create_notebook(notebook_title)

    if not notebook_id:
        print("❌ Failed to create notebook")
        print(f"📁 Files saved to: {output_dir}")
        sys.exit(1)

    # Configure custom prompt
    prompt_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "assets",
        "financial_analyst_prompt.txt",
    )
    if os.path.exists(prompt_path):
        configure_notebook(notebook_id, prompt_path)
    else:
        print(f"⚠️ Prompt file not found at: {prompt_path}")

    results = upload_all_sources(notebook_id, all_files)

    # Cleanup
    cleanup_temp_files(all_files, output_dir)

    # Summary
    print(f"\n{'=' * 50}")
    print(f"🎉 COMPLETE!")
    print(f"{'=' * 50}")
    print(f"📊 Stock: {stock_code} ({stock_name}) [{market_display}]")
    print(f"📚 Notebook: {notebook_title}")
    print(f"📄 Uploaded: {len(results['success'])} reports")
    if results["failed"]:
        print(f"❌ Failed: {len(results['failed'])} reports")
    print(f"\n💡 Open NotebookLM and ask questions about {stock_name}'s financials!")


if __name__ == "__main__":
    main()
