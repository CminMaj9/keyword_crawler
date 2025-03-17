# 小红书聚光取数需求产品说明

## 演示界面：

http://47.251.73.120:8000/

### 取数链接：

https://ad.xiaohongshu.com/aurora/ad/tools/keywordTool

## 日常运维

每天看看 Cookie 是否失效，并维护 Cookie 和数据

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

通过飞书集成平台，将 MySQL 数据转化为在线表格，供用户查看。具体是通过后端接口提供 JSON 格式的数据，并结合飞书集成平台（Lark Suite）的工作流实现每日定时拉取和存储到飞书多维表格。

#### 优点

**自动化**：通过飞书工作流实现每日定时调用，无需手动运行脚本。

**云端协作**：飞书多维表格支持多人协作、权限管理，数据存储在云端，方便团队共享和查看。

**集成性强**：飞书集成平台可以轻松调用后端接口，并将数据写入多维表格，简化工作流。

**JSON 格式灵活**：JSON 是一种通用的数据格式，方便接口传输和处理。

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

## 整体流程

1. 平台接口获取
2. 取数爬虫完成
3. 数据持久化
4. 前后端搭建
5. 对外数据提供接口建立
6. **👀如何把 mysql 数据同步飞书云文档**，这是难事。

### 参考链接

https://anycross.feishu.cn/documentation/template/all/schedule-sync-mysql-data-base#%E4%B8%80%E3%80%81%E6%A6%82%E8%BF%B0

https://anycross.feishu.cn/console?templateId=7204769068350701570
