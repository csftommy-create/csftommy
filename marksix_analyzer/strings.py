# -*- coding: utf-8 -*-
"""UI strings with runtime locale switching (繁體中文 / English).

Access via ``s("key", **fmt)``. Switch language with ``set_lang("en")`` /
``set_lang("zh")``; missing keys fall back to Chinese, then to the key name.
"""
from __future__ import annotations

ZH: dict[str, str] = {
    # App / general
    "app_title": "六合彩數據分析器",
    "header_subtitle": "統計分析工具 · 版本 {version}",
    "ok": "確定",
    "cancel": "取消",
    "close": "關閉",
    "save": "儲存",
    "copy": "複製",
    "yes": "是",
    "no": "否",
    "all": "全部",

    # Menus / toolbar
    "menu_file": "檔案",
    "menu_help": "說明",
    "action_refresh": "重新整理",
    "action_import_csv": "匯入 CSV",
    "action_export_csv": "匯出 CSV",
    "action_manual_add": "手動新增攪珠結果",
    "action_about": "關於",
    "action_exit": "離開",

    # Tabs
    "tab_dashboard": "總覽",
    "tab_frequency": "號碼頻率",
    "tab_gaps": "遺漏分析",
    "tab_distribution": "分佈統計",
    "tab_trend": "走勢圖",
    "tab_smartpick": "智能選號",
    "tab_saved": "我的號碼",
    "tab_data": "資料管理",

    # Global filter bar
    "filter_label": "分析範圍：",
    "filter_all": "全部",
    "filter_last50": "最近 50 期",
    "filter_last100": "最近 100 期",
    "filter_custom": "自訂範圍",
    "filter_from": "由",
    "filter_to": "至",
    "filter_include_extra": "包含特別號碼",

    # Status bar
    "status_latest": "資料庫最新期數：第 {draw_id} 期（{date}）",
    "status_updating": "更新中…",
    "status_update_failed": "更新失敗（可手動匯入）",
    "status_up_to_date": "資料已是最新",
    "status_no_data": "資料庫沒有資料，請匯入 CSV 或手動新增",

    # Dashboard
    "dash_latest_draw": "最新攪珠結果",
    "dash_next_draw": "下期攪珠日",
    "dash_next_unknown": "未知",
    "dash_hot": "最熱號碼",
    "dash_cold": "最冷號碼",
    "dash_max_gap": "最大遺漏",
    "dash_mini_freq": "號碼頻率（概覽）",
    "dash_extra_label": "特別號碼",

    # Frequency tab
    "freq_title": "號碼出現頻率",
    "freq_col_number": "號碼",
    "freq_col_count": "出現次數",
    "freq_col_pct": "百分比",
    "freq_hot_hint": "紅色＝最熱門前 10，藍色＝最冷門後 10",

    # Gaps tab
    "gap_heading": "遺漏分析 · 已連續多少期未開出",
    "gap_hint2": "顏色越亮 = 遺漏越久",
    "gap_col_number": "號碼",
    "gap_col_current": "目前遺漏",
    "gap_col_max": "最大遺漏",
    "gap_col_avg": "平均遺漏",
    "gap_col_last": "最近出現",
    "gap_hint": "超過平均遺漏的號碼以顏色標示",

    # Distribution tab
    "dist_oddeven": "單雙比分佈",
    "dist_highlow": "大小比分佈（1-24 / 25-49）",
    "dist_sum": "六個號碼總和分佈",
    "dist_sum_stat": "平均：{mean:.1f}　中位數：{median:.1f}　標準差：{std:.1f}",
    "dist_consecutive": "連號統計",
    "dist_consecutive_stat": "含 2 個或以上連號的期數佔 {pct:.1f}%（歷史上約 50%）",

    # Tail digit
    "tail_title": "尾數分析",
    "tail_same_stat": "含 2 個或以上相同尾數的期數佔 {pct:.1f}%",

    # Trend tab
    "trend_title": "近期走勢圖",
    "trend_count_label": "顯示期數：",

    # Smart pick tab
    "sp_title": "智能選號",
    "sp_filters": "過濾條件",
    "sp_count_label": "產生組合數量：",
    "sp_generate": "產生號碼",
    "sp_filter_oddeven": "單雙比例（避開 6:0 或 0:6）",
    "sp_filter_highlow": "大小比例（避開全大或全細）",
    "sp_filter_sum": "總和範圍",
    "sp_filter_sum_min": "最小",
    "sp_filter_sum_max": "最大",
    "sp_filter_consecutive": "連號限制（避開 3 個或以上連號）",
    "sp_filter_sametail": "同尾限制（避開 3 個或以上同尾）",
    "sp_filter_birthday": "生日避開（避開全部號碼 ≤ 31）",
    "sp_filter_arithmetic": "熱門組合避開（避開等差數列）",
    "sp_filter_exclude_last": "排除上期號碼",
    "sp_saved_ok": "已儲存至我的號碼",
    "sp_copied": "已複製到剪貼簿",
    "sp_gen_failed": "在嘗試次數內無法產生符合條件的組合，請放寬過濾條件。",
    "sp_disclaimer": (
        "智能選號只過濾統計上少見或大眾常選的組合，"
        "不會提高中獎機率。每次攪珠均為獨立隨機事件。"
    ),

    # Saved picks tab
    "saved_col_created": "建立時間",
    "saved_col_numbers": "號碼",
    "saved_col_method": "方式",
    "saved_col_note": "備註",
    "saved_check": "對獎",
    "saved_delete": "刪除",
    "saved_method_smart": "智能",
    "saved_method_random": "隨機",
    "saved_method_manual": "手動",
    "saved_check_title": "對獎結果",
    "saved_check_pick": "選號：",
    "saved_check_against": "對獎期數：",
    "saved_check_result": "中獎等級：{tier}",
    "saved_check_none": "沒有中獎",
    "saved_check_matches": "命中主號：{mains}　特別號碼：{extra}",
    "saved_empty": "尚未儲存任何號碼",

    # Prize tiers
    "prize_1": "頭獎",
    "prize_2": "二獎",
    "prize_3": "三獎",
    "prize_4": "四獎",
    "prize_5": "五獎",
    "prize_6": "六獎",
    "prize_7": "七獎",

    # Data tab
    "data_title": "資料管理",
    "data_total": "總期數：{count}",
    "data_range": "日期範圍：{start} 至 {end}",
    "data_col_draw": "期數",
    "data_col_date": "日期",
    "data_col_numbers": "號碼",
    "data_col_extra": "特別",
    "data_col_jackpot": "頭獎基金",
    "data_page_prev": "上一頁",
    "data_page_next": "下一頁",
    "data_page_info": "第 {page} / {total} 頁",

    # Manual entry dialog
    "manual_title": "手動新增攪珠結果",
    "manual_draw_id": "期數（例：26/078）",
    "manual_date": "日期",
    "manual_numbers": "六個號碼",
    "manual_extra": "特別號碼",
    "manual_invalid": "輸入無效：{reason}",
    "manual_dup_number": "號碼不可重複",
    "manual_range": "號碼必須介乎 1 至 49",
    "manual_need_six": "必須輸入六個主號碼",

    # CSV import
    "csv_import_title": "匯入 CSV",
    "csv_import_done": "成功匯入 {ok} 筆，略過 {bad} 筆錯誤資料。",
    "csv_import_errors": "錯誤資料（行號）：\n{lines}",
    "csv_export_done": "已匯出 {count} 筆資料至：\n{path}",
    "csv_filter": "CSV 檔案 (*.csv)",

    # About / disclaimer
    "about_title": "關於六合彩數據分析器",
    "disclaimer_title": "重要聲明",
    "disclaimer_body": (
        "本程式為統計及分析工具，並非預測工具。\n"
        "每次攪珠均為獨立隨機事件，任何方法均無法預測未來結果。\n"
        "「智能選號」只是過濾統計上罕見或大眾常選的組合，"
        "以減低中獎需與他人攤分的機會，並不會提高中獎機率。\n"
        "請理性參與，量力而為。"
    ),
    "about_version": "版本：{version}",
    "about_data_source": "資料來源：香港賽馬會（HKJC）公開攪珠結果及社群歷史資料集。",
    "about_seed_note": "隨附之 seed_data.csv 收錄自 2002 年 7 月 4 日（改為 49 選 6 攪珠制）起之歷史攪珠結果；最新期數會於連線時自動更新。",

    # Errors / misc
    "error": "錯誤",
    "info": "訊息",
    "confirm_delete": "確定要刪除嗎？",
}

EN: dict[str, str] = {
    # App / general
    "app_title": "Mark Six Analyzer",
    "header_subtitle": "Statistics & Analysis · v{version}",
    "ok": "OK",
    "cancel": "Cancel",
    "close": "Close",
    "save": "Save",
    "copy": "Copy",
    "yes": "Yes",
    "no": "No",
    "all": "All",

    # Menus / toolbar
    "menu_file": "File",
    "menu_help": "Help",
    "action_refresh": "Refresh",
    "action_import_csv": "Import CSV",
    "action_export_csv": "Export CSV",
    "action_manual_add": "Add Draw Manually",
    "action_about": "About",
    "action_exit": "Exit",

    # Tabs
    "tab_dashboard": "Dashboard",
    "tab_frequency": "Frequency",
    "tab_gaps": "Gaps",
    "tab_distribution": "Distribution",
    "tab_trend": "Trend",
    "tab_smartpick": "Smart Pick",
    "tab_saved": "My Numbers",
    "tab_data": "Data",

    # Global filter bar
    "filter_label": "Range:",
    "filter_all": "All",
    "filter_last50": "Last 50 draws",
    "filter_last100": "Last 100 draws",
    "filter_custom": "Custom range",
    "filter_from": "From",
    "filter_to": "To",
    "filter_include_extra": "Include extra number",

    # Status bar
    "status_latest": "Latest draw: #{draw_id} ({date})",
    "status_updating": "Updating…",
    "status_update_failed": "Update failed (import manually)",
    "status_up_to_date": "Data is up to date",
    "status_no_data": "No data — import a CSV or add draws manually",

    # Dashboard
    "dash_latest_draw": "Latest Draw",
    "dash_next_draw": "Next Draw",
    "dash_next_unknown": "Unknown",
    "dash_hot": "Hottest Numbers",
    "dash_cold": "Coldest Numbers",
    "dash_max_gap": "Longest Gap",
    "dash_mini_freq": "Number Frequency (overview)",
    "dash_extra_label": "Extra Number",

    # Frequency tab
    "freq_title": "Number Frequency",
    "freq_col_number": "No.",
    "freq_col_count": "Count",
    "freq_col_pct": "Percent",
    "freq_hot_hint": "Red = hottest 10, Blue = coldest 10",

    # Gaps tab
    "gap_heading": "Gap Analysis · draws since last seen",
    "gap_hint2": "Brighter = longer gap",
    "gap_col_number": "No.",
    "gap_col_current": "Current Gap",
    "gap_col_max": "Max Gap",
    "gap_col_avg": "Avg Gap",
    "gap_col_last": "Last Seen",
    "gap_hint": "Numbers past their average gap are highlighted",

    # Distribution tab
    "dist_oddeven": "Odd : Even Ratio",
    "dist_highlow": "High : Low Ratio (1-24 / 25-49)",
    "dist_sum": "Sum of Six Numbers",
    "dist_sum_stat": "Mean: {mean:.1f}   Median: {median:.1f}   Std: {std:.1f}",
    "dist_consecutive": "Consecutive Numbers",
    "dist_consecutive_stat": "{pct:.1f}% of draws contain 2+ consecutive numbers (historically ~50%)",

    # Tail digit
    "tail_title": "Tail Digits",
    "tail_same_stat": "{pct:.1f}% of draws contain 2+ numbers sharing a tail digit",

    # Trend tab
    "trend_title": "Recent Trend",
    "trend_count_label": "Draws shown:",

    # Smart pick tab
    "sp_title": "Smart Pick",
    "sp_filters": "Filters",
    "sp_count_label": "Combinations to generate:",
    "sp_generate": "Generate",
    "sp_filter_oddeven": "Odd/even (reject 6:0 or 0:6)",
    "sp_filter_highlow": "High/low (reject all-high or all-low)",
    "sp_filter_sum": "Sum range",
    "sp_filter_sum_min": "Min",
    "sp_filter_sum_max": "Max",
    "sp_filter_consecutive": "Consecutive (reject 3+ in a row)",
    "sp_filter_sametail": "Same tail (reject 3+ sharing a tail digit)",
    "sp_filter_birthday": "Birthday (reject all numbers ≤ 31)",
    "sp_filter_arithmetic": "Popular combos (reject arithmetic sequences)",
    "sp_filter_exclude_last": "Exclude last draw's numbers",
    "sp_saved_ok": "Saved to My Numbers",
    "sp_copied": "Copied to clipboard",
    "sp_gen_failed": "Could not generate a combination within the attempt limit — loosen the filters.",
    "sp_disclaimer": (
        "Smart Pick only filters out statistically rare or commonly-picked "
        "combinations; it does not improve your chance of winning. Every draw "
        "is an independent random event."
    ),

    # Saved picks tab
    "saved_col_created": "Created",
    "saved_col_numbers": "Numbers",
    "saved_col_method": "Method",
    "saved_col_note": "Note",
    "saved_check": "Check Prize",
    "saved_delete": "Delete",
    "saved_method_smart": "Smart",
    "saved_method_random": "Random",
    "saved_method_manual": "Manual",
    "saved_check_title": "Prize Check",
    "saved_check_pick": "Your pick:",
    "saved_check_against": "Against draw:",
    "saved_check_result": "Prize tier: {tier}",
    "saved_check_none": "No prize",
    "saved_check_matches": "Main matches: {mains}   Extra: {extra}",
    "saved_empty": "No saved numbers yet",

    # Prize tiers
    "prize_1": "1st Prize",
    "prize_2": "2nd Prize",
    "prize_3": "3rd Prize",
    "prize_4": "4th Prize",
    "prize_5": "5th Prize",
    "prize_6": "6th Prize",
    "prize_7": "7th Prize",

    # Data tab
    "data_title": "Data",
    "data_total": "Total draws: {count}",
    "data_range": "Date range: {start} to {end}",
    "data_col_draw": "Draw",
    "data_col_date": "Date",
    "data_col_numbers": "Numbers",
    "data_col_extra": "Extra",
    "data_col_jackpot": "1st Prize Fund",
    "data_page_prev": "Previous",
    "data_page_next": "Next",
    "data_page_info": "Page {page} / {total}",

    # Manual entry dialog
    "manual_title": "Add Draw Manually",
    "manual_draw_id": "Draw no. (e.g. 26/078)",
    "manual_date": "Date",
    "manual_numbers": "Six numbers",
    "manual_extra": "Extra number",
    "manual_invalid": "Invalid input: {reason}",
    "manual_dup_number": "Numbers must not repeat",
    "manual_range": "Numbers must be between 1 and 49",
    "manual_need_six": "Six main numbers are required",

    # CSV import
    "csv_import_title": "Import CSV",
    "csv_import_done": "Imported {ok} rows, skipped {bad} invalid rows.",
    "csv_import_errors": "Invalid rows (line numbers):\n{lines}",
    "csv_export_done": "Exported {count} rows to:\n{path}",
    "csv_filter": "CSV files (*.csv)",

    # About / disclaimer
    "about_title": "About Mark Six Analyzer",
    "disclaimer_title": "Important Disclaimer",
    "disclaimer_body": (
        "This is a statistics and analysis tool, not a prediction tool.\n"
        "Every draw is an independent random event; no method can predict "
        "future results.\n"
        "\"Smart Pick\" only filters out statistically rare or commonly-chosen "
        "combinations to reduce the chance of splitting a prize — it does not "
        "improve your odds of winning.\n"
        "Please play responsibly."
    ),
    "about_version": "Version: {version}",
    "about_data_source": "Data source: Hong Kong Jockey Club (HKJC) public draw results and community historical datasets.",
    "about_seed_note": "The bundled seed_data.csv covers draws from 2002-07-04 (when Mark Six moved to the 6-from-49 format); the latest draws are fetched automatically when online.",

    # Errors / misc
    "error": "Error",
    "info": "Message",
    "confirm_delete": "Delete this item?",
}

LOCALES = {"zh": ZH, "en": EN}
_lang = "zh"


def set_lang(lang: str) -> None:
    global _lang
    _lang = lang if lang in LOCALES else "zh"


def get_lang() -> str:
    return _lang


def other_lang() -> str:
    """The language the toggle would switch to."""
    return "en" if _lang == "zh" else "zh"


def lang_button_label() -> str:
    """Label for the toggle button: shows the language it switches TO."""
    return "EN" if _lang == "zh" else "中文"


def s(key: str, **kwargs) -> str:
    text = LOCALES[_lang].get(key)
    if text is None:
        text = ZH.get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text
