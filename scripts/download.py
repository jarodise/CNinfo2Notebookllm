#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download A-share and Hong Kong stock reports from cninfo.com.cn
Stores PDFs in temporary directory, outputs file paths for upload
"""

import sys
import os
import json
import tempfile
import datetime
import time
import random
import httpx

# Stock database location
STOCKS_JSON = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "stocks.json"
)


def to_chinese_year(year: int) -> str:
    """Convert year to Chinese numerals (e.g., 2023 -> 二零二三)"""
    mapping = {
        "0": "零",
        "1": "一",
        "2": "二",
        "3": "三",
        "4": "四",
        "5": "五",
        "6": "六",
        "7": "七",
        "8": "八",
        "9": "九",
    }
    return "".join(mapping[d] for d in str(year))


class CnInfoDownloader:
    """Downloads reports from cninfo.com.cn - supports A-share and Hong Kong stocks"""

    def __init__(self):
        self.cookies = {
            "JSESSIONID": "9A110350B0056BE0C4FDD8A627EF2868",
            "insert_cookie": "37836164",
        }
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:110.0) Gecko/20100101 Firefox/110.0",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "http://www.cninfo.com.cn",
            "Referer": "http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search&lastPage=index",
        }
        self.timeout = httpx.Timeout(60.0)
        self.query_url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
        self.market_to_stocks = self._load_stocks()

    def _load_stocks(self) -> dict:
        """Load stock database from JSON file"""
        if os.path.exists(STOCKS_JSON):
            with open(STOCKS_JSON, "r") as f:
                return json.load(f)
        return {}

    def _detect_market(self, stock_code: str) -> str:
        """Auto-detect market based on stock code"""
        # Check database first (most reliable)
        if stock_code in self.market_to_stocks.get("hke", {}):
            return "hke"
        if stock_code in self.market_to_stocks.get("szse", {}):
            return "szse"

        # Fallback to code pattern
        # Hong Kong: typically 5 digits, often starting with 00, 01, 02, 09
        if len(stock_code) == 5 and stock_code.startswith(("00", "01", "02", "09")):
            return "hke"
        # A-shares: 6 digits starting with 0, 3, 6
        if len(stock_code) == 6 and stock_code[0] in "036":
            return "szse"

        return "szse"  # Default to A-share

    def find_stock(self, stock_input: str) -> tuple:
        """
        Find stock by code or name
        Returns: (stock_code, stock_info, market) or (None, None, None)
        """
        # Try as code first
        for market, market_stocks in self.market_to_stocks.items():
            if stock_input in market_stocks:
                return stock_input, market_stocks[stock_input], market

        # Try as name
        for market, market_stocks in self.market_to_stocks.items():
            for code, info in market_stocks.items():
                if info.get("zwjc") == stock_input:
                    return code, info, market

        return None, None, None

    def _query_announcements(self, filter_params: dict, market: str = "szse") -> list:
        """Query cninfo API for announcements"""
        client = httpx.Client(
            headers=self.headers, cookies=self.cookies, timeout=self.timeout
        )

        # Get orgId for stock
        stock_code = filter_params["stock"][0]
        stock_info = None
        for market_stocks in self.market_to_stocks.values():
            if stock_code in market_stocks:
                stock_info = market_stocks[stock_code]
                break

        if not stock_info:
            return []

        payload = self._build_payload(
            stock_code, stock_info, market, filter_params
        )

        announcements = []
        has_more = True

        while has_more:
            payload["pageNum"] += 1
            try:
                resp = client.post(self.query_url, data=payload).json()
                has_more = resp.get("hasMore", False)
                if resp.get("announcements"):
                    announcements.extend(resp["announcements"])
            except Exception as e:
                print(f"Error querying API: {e}", file=sys.stderr)
                break

        return announcements

    def _build_payload(
        self, stock_code: str, stock_info: dict, market: str, filter_params: dict
    ) -> dict:
        """Build API payload with market-aware parameters"""
        # Hong Kong stocks use empty categories and searchkey
        if market == "hke":
            category = ""
            searchkey = ""
        else:
            category = ";".join(filter_params.get("category", []))
            searchkey = filter_params.get("searchkey", "")

        return {
            "pageNum": 0,
            "pageSize": 30,
            "column": market,  # 'szse' for A-share, 'hke' for Hong Kong
            "tabName": "fulltext",
            "plate": "",
            "stock": f"{stock_code},{stock_info['orgId']}",
            "searchkey": searchkey,
            "secid": "",
            "category": category,
            "trade": "",
            "seDate": filter_params.get("seDate", ""),
            "sortName": "",
            "sortType": "",
            "isHLtitle": False,
        }

    def _download_pdf(self, announcement: dict, output_dir: str) -> str:
        """Download a single PDF file, returns file path"""
        client = httpx.Client(
            headers=self.headers, cookies=self.cookies, timeout=self.timeout
        )

        sec_code = announcement["secCode"]
        sec_name = announcement["secName"].replace("*", "s").replace("/", "-")
        title = announcement["announcementTitle"].replace("/", "-").replace("\\", "-")
        adjunct_url = announcement["adjunctUrl"]
        announcement_id = announcement["announcementId"]

        if announcement.get("adjunctType") != "PDF":
            return None

        filename = f"{sec_code}_{sec_name}_{title}_{announcement_id}.pdf"
        # Clean filename
        filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        filepath = os.path.join(output_dir, filename)

        if not os.path.exists(filepath):
            try:
                print(f"Downloading: {title}")
                resp = client.get(f"http://static.cninfo.com.cn/{adjunct_url}")
                with open(filepath, "wb") as f:
                    f.write(resp.content)
                time.sleep(random.uniform(0.5, 1.5))  # Rate limiting
            except Exception as e:
                print(f"Download failed: {e}", file=sys.stderr)
                return None

        return filepath

    def _is_main_annual_report(self, title: str, year: int, market: str = "szse") -> bool:
        """Check if this is the main annual report (not summary/English)"""
        chinese_year = to_chinese_year(year)

        if market == "hke":
            # Hong Kong naming patterns
            # Check for both Arabic (2023) and Chinese (二零二三) numerals
            has_year = f"{year}" in title or chinese_year in title
            is_annual = (
                "annual report" in title.lower()
                or "年度报告" in title
                or "年报" in title
                or f"{year}财务年度报告" in title
            )
            is_summary = (
                "summary" in title.lower()
                or "摘要" in title
            )
            is_quarterly = (
                "季度" in title
                or "半年度" in title
                or "中期" in title
            )
            is_english_only = "英文" in title

            return has_year and is_annual and not is_summary and not is_quarterly and not is_english_only
        else:
            # Mainland China naming patterns
            if f"{year}年年度报告" not in title and f"{year}年年报" not in title:
                return False
            if "摘要" in title or "英文" in title or "summary" in title.lower():
                return False
            if "更正" in title or "修订" in title:
                return False
            return True

    def _get_annual_report_search_period(self, year: int, market: str = "szse") -> tuple:
        """Get search period for annual reports based on market"""
        if market == "hke":
            # HK stocks may publish in the same year
            search_start = f"{year}-01-01"
            search_end = f"{year + 1}-06-30"
        else:
            # A-shares are published in the following year (March-April)
            search_start = f"{year + 1}-03-01"
            search_end = f"{year + 1}-06-30"
        return search_start, search_end

    def _is_main_periodic_report(self, title: str, report_type: str) -> bool:
        """Check if this is a main periodic report"""
        if "摘要" in title or "英文" in title:
            return False
        if "更正" in title or "修订" in title:
            return False

        if report_type == "semi":
            return "半年度报告" in title or "中期报告" in title
        elif report_type == "q1":
            return "一季度" in title or "第一季度" in title
        elif report_type == "q3":
            return "三季度" in title or "第三季度" in title

        return False

    def download_annual_reports(
        self, stock_code: str, years: list, output_dir: str, market: str = "szse"
    ) -> list:
        """Download annual reports for specified years"""
        downloaded = []

        for year in years:
            search_start, search_end = self._get_annual_report_search_period(year, market)

            # Build filter params based on market
            if market == "hke":
                filter_params = {
                    "stock": [stock_code],
                    "category": [],  # HK stocks don't use categories
                    "searchkey": "",  # HK stocks use empty search key
                    "seDate": f"{search_start}~{search_end}",
                }
            else:
                filter_params = {
                    "stock": [stock_code],
                    "category": ["category_ndbg_szsh"],  # Annual reports
                    "searchkey": f"{year}年年度报告",
                    "seDate": f"{search_start}~{search_end}",
                }

            announcements = self._query_announcements(filter_params, market)

            for ann in announcements:
                if self._is_main_annual_report(ann["announcementTitle"], year, market):
                    filepath = self._download_pdf(ann, output_dir)
                    if filepath:
                        downloaded.append(filepath)
                        print(f"✅ Downloaded: {year} Annual Report")
                    break  # Only get one per year

        return downloaded

    def download_periodic_reports(
        self, stock_code: str, year: int, output_dir: str, market: str = "szse"
    ) -> list:
        """Download Q1, semi-annual, Q3 reports for current year"""
        downloaded = []

        # Note: HK stocks may not have the same periodic report structure
        # Using same config for both markets
        report_configs = [
            (
                "q1",
                "category_yjdbg_szsh",
                "一季度报告",
                f"{year}-04-01",
                f"{year}-05-31",
            ),
            (
                "semi",
                "category_bndbg_szsh",
                "半年度报告",
                f"{year}-08-01",
                f"{year}-09-30",
            ),
            (
                "q3",
                "category_sjdbg_szsh",
                "三季度报告",
                f"{year}-10-01",
                f"{year}-11-30",
            ),
        ]

        for report_type, category, search_term, start_date, end_date in report_configs:
            if market == "hke":
                filter_params = {
                    "stock": [stock_code],
                    "category": [],  # HK stocks don't use categories
                    "searchkey": "",  # HK stocks use empty search key
                    "seDate": f"{start_date}~{end_date}",
                }
            else:
                filter_params = {
                    "stock": [stock_code],
                    "category": [category],
                    "searchkey": search_term,
                    "seDate": f"{start_date}~{end_date}",
                }

            announcements = self._query_announcements(filter_params, market)

            for ann in announcements:
                if self._is_main_periodic_report(ann["announcementTitle"], report_type):
                    filepath = self._download_pdf(ann, output_dir)
                    if filepath:
                        downloaded.append(filepath)
                        print(f"✅ Downloaded: {year} {search_term}")
                    break

        return downloaded


def main():
    """Main entry point - downloads reports and prints file paths"""
    if len(sys.argv) < 2:
        print("Usage: python download.py <stock_code_or_name> [output_dir]")
        print("Example: python download.py 600350        # A-share")
        print("Example: python download.py 00700        # Hong Kong stock")
        print("Example: python download.py 山东高速")
        sys.exit(1)

    stock_input = sys.argv[1]
    output_dir = (
        sys.argv[2] if len(sys.argv) > 2 else tempfile.mkdtemp(prefix="cninfo_reports_")
    )

    downloader = CnInfoDownloader()

    # Find stock (now returns market too)
    stock_code, stock_info, market = downloader.find_stock(stock_input)
    if not stock_code:
        print(f"❌ Stock not found: {stock_input}", file=sys.stderr)
        sys.exit(1)

    stock_name = stock_info.get("zwjc", stock_code)
    market_display = "Hong Kong" if market == "hke" else "A-share"
    print(f"📊 Found stock: {stock_code} ({stock_name}) [{market_display}]")
    print(f"📁 Output directory: {output_dir}")

    # Calculate years
    current_year = datetime.datetime.now().year
    annual_years = list(range(current_year - 5, current_year))  # Last 5 years

    print(f"\n📥 Downloading annual reports for: {annual_years}")
    annual_files = downloader.download_annual_reports(
        stock_code, annual_years, output_dir, market
    )

    # Try current year for periodic reports, fallback to previous year
    print(f"\n📥 Downloading periodic reports (Q1, semi-annual, Q3)...")
    periodic_files = downloader.download_periodic_reports(
        stock_code, current_year, output_dir, market
    )

    # If no periodic reports found in current year, try previous year
    if not periodic_files:
        print(f"   No {current_year} reports yet, trying {current_year - 1}...")
        periodic_files = downloader.download_periodic_reports(
            stock_code, current_year - 1, output_dir, market
        )
    # If some but not all, also check previous year for missing ones
    elif len(periodic_files) < 3:
        print(f"   Checking {current_year - 1} for additional reports...")
        prev_year_files = downloader.download_periodic_reports(
            stock_code, current_year - 1, output_dir, market
        )
        periodic_files.extend(prev_year_files)

    all_files = annual_files + periodic_files

    print(f"\n{'=' * 50}")
    print(f"✅ Downloaded {len(all_files)} reports")
    print(f"📁 Location: {output_dir}")
    print(f"\n📄 Files:")
    for f in all_files:
        print(f"  {os.path.basename(f)}")

    # Output JSON for easy parsing by upload script
    result = {
        "stock_code": stock_code,
        "stock_name": stock_name,
        "market": market,
        "output_dir": output_dir,
        "files": all_files,
    }

    # Write result to stdout marker for parsing
    print(f"\n---JSON_OUTPUT---")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
