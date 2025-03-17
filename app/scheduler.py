# app/scheduler.py
import schedule
import time
from datetime import datetime
from app.fetch_data import fetch_data, load_cookies
from app.database import get_word_packages

def schedule_task():
    cookies = load_cookies()
    if not cookies:
        print("Cookies 未设置，无法拉取数据")
        return

    word_packages = get_word_packages()
    if not word_packages:
        print("词包列表为空，无法调度任务")
        return

    for i, package_name in enumerate(word_packages.keys()):
        # TODO. 调试自动拉取
        # time_str = f"13:{i*5:02d}"  # 暂时使用 13:xx 测试
        time_str = f"13:41"
        schedule.every().day.at(time_str).do(lambda pkg=package_name: fetch_data(cookies, package_name=pkg))
        print(f"已调度词包 {package_name} 于 {time_str} 执行")

    while True:
        schedule.run_pending()
        time.sleep(60)