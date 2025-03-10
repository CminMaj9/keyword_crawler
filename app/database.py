# app/database.py
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE")
        )
        return connection
    except Error as e:
        print(f"数据库连接失败: {e}")
        return None

def insert_keyword_data(date, keyword, monthpv, bid):
    connection = get_db_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        # 检查是否已存在相同日期和关键词的记录
        check_query = """
        SELECT COUNT(*) FROM keyword_data 
        WHERE date = %s AND keyword = %s
        """
        cursor.execute(check_query, (date, keyword))
        if cursor.fetchone()[0] > 0:
            return True  # 已存在，跳过插入
        # 如果不存在，插入新记录
        insert_query = """
        INSERT INTO keyword_data (date, keyword, monthpv, bid)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (date, keyword, monthpv, bid))
        connection.commit()
        return True
    except Error as e:
        print(f"插入数据失败: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def insert_log(date, status, message):
    connection = get_db_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """
        INSERT INTO fetch_logs (date, status, message)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (date, status, message))
        connection.commit()
        return True
    except Error as e:
        print(f"插入日志失败: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def get_logs():
    connection = get_db_connection()
    if connection is None:
        return []
    try:
        cursor = connection.cursor()
        query = "SELECT date, status, message, timestamp FROM fetch_logs ORDER BY timestamp DESC"
        cursor.execute(query)
        logs = cursor.fetchall()
        return [{"date": log[0], "status": log[1], "message": log[2], "timestamp": log[3]} for log in logs]
    except Error as e:
        print(f"获取日志失败: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_keyword_data():
    connection = get_db_connection()
    if connection is None:
        return []
    try:
        cursor = connection.cursor()
        query = "SELECT date, keyword, monthpv, bid FROM keyword_data ORDER BY date DESC"
        cursor.execute(query)
        data = cursor.fetchall()
        return [{"date": d[0], "keyword": d[1], "monthpv": d[2], "bid": d[3]} for d in data]
    except Error as e:
        print(f"获取数据失败: {e}")
        return []
    finally:
        cursor.close()
        connection.close()