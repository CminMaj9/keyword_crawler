# app/fetch_data.py
import requests
import json
from datetime import datetime
from app.database import insert_keyword_data, insert_log

def load_cookies():
    try:
        with open("cookies.json", "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                print("cookies.json 文件为空，返回空字典")
                return {}
            return json.loads(content)
    except FileNotFoundError:
        print("cookies.json 文件不存在，返回空字典")
        return {}
    except json.JSONDecodeError as e:
        print(f"cookies.json 文件格式错误，无法解析 JSON: {e}")
        return {}
    except Exception as e:
        print(f"读取 cookies.json 文件时发生未知错误: {e}")
        return {}

def save_cookies(cookies):
    with open("cookies.json", "w", encoding="utf-8") as f:
        json.dump(cookies, f, ensure_ascii=False, indent=4)

def check_cookies(cookies, url, headers):
    try:
        response = requests.post(url, headers=headers, cookies=cookies, json={"words": ["apoem"]}, timeout=10)
        if response.status_code == 200 and response.json().get("code") == 0:
            return True
        return False
    except:
        return False

def fetch_data(cookies, date=None):
    if date is None:
        date = datetime.now().strftime("%m月%d日")

    url = "https://ad.xiaohongshu.com/api/leona/rtb/tool/keyword/effect"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9",
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://ad.xiaohongshu.com",
        "referer": "https://ad.xiaohongshu.com/aurora/ad/tools/keywordTool",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-b3-traceid": "5477b90d21d2c2eb",
        "priority": "u=1, i"
    }

    try:
        response = requests.post(url, headers=headers, cookies=cookies, json={"words": ["apoem", "apoem安诗悦小金珠", "apoem七花小金珠", "apoem玫瑰籽精华油", "apoem小金珠", "apoem精华油", "七花小金珠"]}, timeout=10)
        response.raise_for_status()
        result = response.json()

        if result.get("code") != 0:
            insert_log(date, "failed", f"API 返回错误: {result.get('msg')}")
            return False

        keywords_data = result.get("data", {}).get("list", [])
        total_items = len(keywords_data)
        for i, item in enumerate(keywords_data, 1):
            keyword = item["keyword"]
            monthpv = item["monthpv"]
            bid = item["bid"]
            insert_keyword_data(date, keyword, monthpv, bid)
            # 模拟进度（实际进度取决于数据库插入速度）
            if total_items > 0:
                progress = (i / total_items) * 100
                print(f"进度: {progress:.1f}%")  # 后期可通过 API 返回进度

        insert_log(date, "success", "数据拉取成功")
        return True
    except requests.exceptions.RequestException as e:
        insert_log(date, "failed", f"请求失败: {str(e)}")
        return False