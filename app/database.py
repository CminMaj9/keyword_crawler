# app/database.py
from mysql.connector import connect, Error
import os
from dotenv import load_dotenv
import json

load_dotenv()

def get_db_connection():
    try:
        connection = connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE")
        )
        return connection
    except Error as e:
        print(f"数据库连接失败: {e}")
        return None

def initialize_database(connection):
    cursor = connection.cursor()
    try:
        # 创建或更新 keyword_data 表，确保有唯一索引
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS keyword_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date VARCHAR(10),
                keyword VARCHAR(255),
                monthpv INT,
                bid DECIMAL(10, 2),
                package VARCHAR(100),
                UNIQUE KEY unique_record (date, keyword, package)
            )
        """)
        connection.commit()
        print("数据库表 keyword_data 初始化或验证完成")
    except Error as e:
        print(f"初始化数据库失败: {e}")
    finally:
        cursor.close()

def insert_keyword_data(date, keyword, monthpv, bid, package):
    connection = get_db_connection()
    if connection is None:
        print("无法插入数据：数据库连接失败")
        return False
    cursor = None
    try:
        initialize_database(connection)  # 确保表结构正确
        cursor = connection.cursor()
        query = "INSERT IGNORE INTO keyword_data (date, keyword, monthpv, bid, package) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (date, keyword, monthpv, bid, package))
        if cursor.rowcount > 0:
            connection.commit()
            print(f"成功插入数据: {date}, {keyword}, {monthpv}, {bid}, {package}")
            return True
        else:
            print(f"数据已存在，跳过插入: {date}, {keyword}, {package}")
            return True
    except Error as e:
        print(f"插入数据失败: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def insert_log(date, status, message):
    connection = get_db_connection()
    if connection is None:
        print("无法插入日志：数据库连接失败")
        return
    cursor = None
    try:
        cursor = connection.cursor()
        query = "INSERT INTO fetch_logs (date, status, message, timestamp) VALUES (%s, %s, %s, NOW())"
        cursor.execute(query, (date, status, message))
        connection.commit()
        print(f"成功插入日志: {date}, {status}, {message}")
    except Error as e:
        print(f"插入日志失败: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_logs():
    connection = get_db_connection()
    if connection is None:
        return []
    cursor = None
    try:
        cursor = connection.cursor()
        query = "SELECT date, status, message, timestamp FROM fetch_logs ORDER BY timestamp DESC"
        cursor.execute(query)
        logs = [{"date": row[0], "status": row[1], "message": row[2], "timestamp": row[3]} for row in cursor.fetchall()]
        return logs
    except Error as e:
        print(f"获取日志失败: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_keyword_data():
    connection = get_db_connection()
    if connection is None:
        return []
    cursor = None
    try:
        cursor = connection.cursor()
        query = "SELECT date, keyword, monthpv, bid, package FROM keyword_data"
        cursor.execute(query)
        data = [{"date": row[0], "keyword": row[1], "monthpv": row[2], "bid": row[3], "package": row[4]} for row in cursor.fetchall()]
        return data
    except Error as e:
        print(f"获取关键词数据失败: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_word_packages():
    connection = get_db_connection()
    if connection is None:
        return {}
    cursor = None
    try:
        cursor = connection.cursor()
        query = "SELECT package_name, words FROM word_packages"
        cursor.execute(query)
        packages = {row[0]: json.loads(row[1]) for row in cursor.fetchall()}
        return packages
    except Error as e:
        print(f"获取词包失败: {e}")
        return {}
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()