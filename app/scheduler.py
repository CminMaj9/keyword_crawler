# app/scheduler.py
import schedule
import time
from datetime import datetime
from app.fetch_data import fetch_data, load_cookies
from app.database import get_word_packages


def run_fetch(package_name):
    # 执行单个词包的数据拉取任务
    cookies = load_cookies()
    if not cookies:
        print(f"[{datetime.now()}] 词包 {package_name} 拉取失败：Cookies 未设置")
        return
    date = datetime.now().strftime("%m月%d日")
    print(f"[{datetime.now()}] 开始拉取词包 {package_name} 的数据")
    success = fetch_data(cookies, date=date, package_name=package_name)
    if success:
        print(f"[{datetime.now()}] 词包 {package_name} 拉取成功")
    else:
        print(f"[{datetime.now()}] 词包 {package_name} 拉取失败，请检查日志")
   

def schedule_task():
    """
    设置定时任务，每天下午 13 点拉取所有词包的数据
    """
    word_packages = get_word_packages()
    if not word_packages:
        print(f"[{datetime.now()}] 词包列表为空，无法调度任务")
        return

    for package_name in word_packages.keys():
        time_str = "13:00"  # 需求中的下午 13 点
        # 使用 lambda 确保 package_name 被正确传递
        schedule.every().day.at(time_str).do(lambda pkg=package_name: run_fetch(pkg))
        print(f"[{datetime.now()}] 已调度词包 {package_name} 于 {time_str} 执行")

    print(f"[{datetime.now()}] 定时任务调度完成，开始运行调度器")
    while True:
        schedule.run_pending()
        time.sleep(60)