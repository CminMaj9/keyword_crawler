# 小红书聚光取数需求产品说明

## 后端

使用 FastAPI 构建后端，负责：

每天上午 8 点定时拉取数据并存入 MySQL 数据库。

提供 API 供前端调用（包括更新 Cookies、手动拉取数据、查看日志等）。

存储、记录拉取失败的日志。

## 数据库

使用 MySQL 存储关键词数据（月均搜索指数和市场出价），替代原来的 Excel 文件。

## **前端**

使用简单的 HTML + JavaScript（可以选择框架如 Vue.js，但为了简化我们先用原生 JS），实现：

- 实时显示 Cookies 状态（是否过期）。
- 提供输入框更新 Cookies。
- 显示拉取失败的日志。
- 提供手动拉取按钮，针对失败的日期重新拉取。

## **飞书集成**

通过飞书开发者平台，将 MySQL 数据转化为在线表格，供用户查看。



## 代码结构

```
keyword_crawler/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI 后端主文件
│   ├── database.py      # MySQL 数据库操作
│   ├── fetch_data.py    # 数据拉取逻辑
│   ├── scheduler.py     # 定时任务逻辑
├── static/
│   ├── index.html       # 前端页面
│   └── script.js        # 前端 JS 逻辑
├── requirements.txt      # 依赖文件
└── cookies.json          # 存储 Cookies
```

