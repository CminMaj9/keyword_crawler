# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.fetch_data import fetch_data, load_cookies, save_cookies, check_cookies
from app.database import get_logs, get_keyword_data
import threading
from app.scheduler import schedule_task
from datetime import datetime

app = FastAPI()

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

class CookiesUpdate(BaseModel):
    cookies: str  # 接收文本格式的 Cookie 字符串

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
    # 将文本格式的 Cookie 转换为字典
    cookie_text = cookies_update.cookies.strip()
    cookie_dict = {}
    if cookie_text:
        try:
            # 分割 Cookie 字符串（格式：name1=value1; name2=value2）
            cookie_pairs = cookie_text.split(";")
            for pair in cookie_pairs:
                pair = pair.strip()
                if pair:
                    key_value = pair.split("=", 1)  # 使用 split("=", 1) 确保只分割第一个 "="
                    if len(key_value) == 2:
                        key, value = key_value
                        cookie_dict[key.strip()] = value.strip()
                    else:
                        raise ValueError(f"无效的 Cookie 格式: {pair}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"解析 Cookies 失败: {str(e)}")

    # 保存到 cookies.json
    save_cookies(cookie_dict)

    # 验证 Cookie 有效性
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
async def manual_fetch():
    cookies = load_cookies()
    if not cookies:
        raise HTTPException(status_code=400, detail="Cookies 未设置")
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
    date = datetime.now().strftime("%m月%d日")
    success = fetch_data(cookies, date)
    if success:
        return {"message": f"{date} 数据拉取成功", "progress": 100}
    raise HTTPException(status_code=500, detail=f"{date} 数据拉取失败，请查看日志")

@app.get("/api/progress")
async def get_progress():
    # 这里可以扩展为实时进度（目前为模拟）
    return {"progress": 0}  # 待前端轮询更新

@app.get("/api/logs")
async def get_fetch_logs():
    return get_logs()

@app.get("/api/data")
async def get_data():
    return get_keyword_data()

# 启动定时任务
def start_scheduler():
    cookies = load_cookies()
    if not cookies:
        print("警告：cookies.json 未设置或无效，定时任务无法运行。请通过前端更新 Cookies。")
    threading.Thread(target=schedule_task, daemon=True).start()

@app.on_event("startup")
async def startup_event():
    start_scheduler()