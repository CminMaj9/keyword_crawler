# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.fetch_data import fetch_data, load_cookies, save_cookies, check_cookies
from app.database import get_logs, get_keyword_data, get_db_connection, get_word_packages
import threading
from app.scheduler import schedule_task
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import json

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class CookiesUpdate(BaseModel):
    cookies: str

class WordPackage(BaseModel):
    package_name: str
    words: list[str]

class FetchRequest(BaseModel):
    package_name: str

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/cookies/status")
async def get_cookies_status():
    cookies = load_cookies()
    if not cookies:
        return {"status": "expired", "message": "Cookies 未设置"}
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
    if check_cookies(cookies, url, headers):
        return {"status": "valid", "message": "Cookies 有效"}
    return {"status": "expired", "message": "Cookies 已过期"}

@app.post("/api/cookies/update")
async def update_cookies(cookies_update: CookiesUpdate):
    cookie_text = cookies_update.cookies.strip()
    cookie_dict = {}
    if cookie_text:
        try:
            cookie_pairs = cookie_text.split(";")
            for pair in cookie_pairs:
                pair = pair.strip()
                if pair:
                    key_value = pair.split("=", 1)
                    if len(key_value) == 2:
                        cookie_dict[key_value[0].strip()] = key_value[1].strip()
                    else:
                        raise ValueError(f"无效的 Cookie 格式: {pair}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"解析 Cookies 失败: {str(e)}")
    save_cookies(cookie_dict)
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
    if check_cookies(cookie_dict, url, headers):
        return {"message": "Cookies 更新成功"}
    raise HTTPException(status_code=400, detail="Cookies 无效，请检查")

@app.post("/api/fetch")
async def manual_fetch(request: FetchRequest):
    cookies = load_cookies()
    if not cookies:
        raise HTTPException(status_code=400, detail="Cookies 未设置")
    date = datetime.now().strftime("%m月%d日")
    package_name = request.package_name
    print(f"前端请求拉取词包: {package_name}")  # 调试前端传来的 package_name
    if not package_name:
        raise HTTPException(status_code=400, detail="请选择一个词包")
    success = fetch_data(cookies, date, package_name)
    if success:
        return {"message": f"{date} 数据拉取成功 (词包: {package_name})", "progress": 100}
    raise HTTPException(status_code=500, detail=f"{date} 数据拉取失败 (词包: {package_name})，请查看日志")

@app.get("/api/daily-records")
async def get_daily_records():
    today = datetime.now().strftime("%m月%d日")
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="数据库连接失败")
    cursor = None
    try:
        cursor = connection.cursor()
        query = "SELECT date, keyword, monthpv, bid, package FROM keyword_data WHERE date = %s"
        cursor.execute(query, (today,))
        records = cursor.fetchall()
        if not records:
            return {"message": f"{today} 没有记录", "data": []}
        formatted_records = [
            {"date": r[0], "keyword": r[1], "monthpv": r[2], "bid": r[3], "package": r[4]}
            for r in records
        ]
        return {"message": f"成功获取 {today} 的记录", "data": formatted_records}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"获取当天记录失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.get("/api/progress")
async def get_progress():
    return {"progress": 0}

@app.get("/api/logs")
async def get_fetch_logs():
    return get_logs()

@app.get("/api/data")
async def get_data():
    return get_keyword_data()

@app.post("/api/word-packages")
async def add_word_package(package: WordPackage):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="数据库连接失败")
    cursor = None
    try:
        cursor = connection.cursor()
        query = "INSERT INTO word_packages (package_name, words) VALUES (%s, %s) ON DUPLICATE KEY UPDATE words=%s"
        cursor.execute(query, (package.package_name, json.dumps(package.words), json.dumps(package.words)))
        connection.commit()
        return {"message": f"词包 {package.package_name} 添加/更新成功"}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"添加词包失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.get("/api/word-packages")
async def list_word_packages():
    return get_word_packages()

def start_scheduler():
    cookies = load_cookies()
    if not cookies:
        print("警告：cookies.json 未设置或无效，定时任务无法运行。请通过前端更新 Cookies。")
    threading.Thread(target=schedule_task, daemon=True).start()

@app.on_event("startup")
async def startup_event():
    start_scheduler()