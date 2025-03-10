# app/scheduler.py
import schedule
import time
from datetime import datetime
from app.fetch_data import fetch_data, load_cookies

def schedule_task():
    cookies = load_cookies()
    if not cookies:
        print("Cookies 未设置，无法拉取数据")
        return

    schedule.every().day.at("08:00").do(lambda: fetch_data(cookies))

    while True:
        schedule.run_pending()
        time.sleep(60)