# 东方财富股吧自动化爬虫

## 项目介绍

该项目使用 Selenium 模拟用户操作抓取东方财富股吧的**发帖**和**评论**数据，支持多线程同时抓取多支股票的信息，并将抓取到的数据保存到 MongoDB 数据库中。项目支持批量化处理，能够根据指定的日期范围自动停止爬取，避免重复收集数据。

## 主要功能

1. **批量爬取股票信息**：从 `stock_codes.txt` 文件中读取股票代码列表，每次爬取 5 个股票
2. **按日期控制爬取范围**：可指定爬取截止日期，当爬取到早于该日期的帖子时自动停止
3. **多线程并行处理**：多个股票代码同时爬取，提高效率
4. **数据持久化**：所有数据保存到 MongoDB 数据库中，方便后续分析和处理

## 文件介绍

- `main_v2.py`：主程序，负责读取股票代码文件并控制批量爬取过程
- `crawler_v2.py`：爬虫主体，包含了 `PostCrawler` 和 `CommentCrawler` 两个类，负责爬取帖子和评论信息
- `parser.py`：解析器，包含了 `PostParser` 和 `CommentParser` 两个类，负责解析网页内容
- `mongodb.py`：数据库接口，负责与 MongoDB 数据库交互
- `stealth.min.js`：JavaScript 文件，用于隐藏 Selenium 的自动化特征
- `stock_codes.txt`：存放需要爬取的股票代码列表，每行一个代码

## 使用步骤

### 1. 环境准备

#### MongoDB 安装

安装 MongoDB 数据库（推荐使用 homebrew 安装）：

```bash
brew install mongodb-community@6.0
```

启动 MongoDB 服务：

```bash
brew services start mongodb-community@6.0
```

创建 `post_info` 和 `comment_info` 两个数据库，分别用于存储发帖信息和评论信息。

#### WebDriver 安装

安装与你的 Chrome 浏览器版本匹配的 ChromeDriver：

1. 查看 Chrome 版本：打开 Chrome，点击右上角的三个点 -> 帮助 -> 关于 Chrome
2. 下载对应版本的 ChromeDriver：[Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/)
3. 将下载的 ChromeDriver 放入系统路径中或项目目录下

#### Python 依赖安装

```bash
pip install selenium pymongo pandas
```

### 2. 配置股票代码

编辑 `stock_codes.txt` 文件，添加需要爬取的股票代码，每行一个。例如：

```
000651
000001
000002
600036
601318
```

可以使用 `//` 添加注释行，注释行会被自动忽略。

### 3. 运行爬虫

执行主程序：

```bash
python main_v2.py
```

根据提示输入爬取截止日期（格式：`YYYY-MM-DD`），例如 `2023-01-01`。爬虫将会从最新的帖子开始爬取，直到遇到早于该日期的帖子时停止。

如果直接按回车，将使用默认日期 `2025-05-01`。

### 4. 爬取逻辑

#### 发帖信息爬取

1. 爬虫会按批次（默认每批 5 个股票）读取股票代码列表
2. 对于每个股票，从第 1 页开始爬取，获取帖子信息
3. 当遇到早于指定截止日期的帖子时，自动停止爬取该股票
4. 爬虫会保留截止日期当天的帖子，但不保留早于该日期的帖子

#### 爬取结果

- 帖子信息会以 `post_股票代码` 为集合名存储在 `post_info` 数据库中
- 评论信息会以 `comment_股票代码` 为集合名存储在 `comment_info` 数据库中

## 数据字段说明

### 发帖信息（post_info 数据库）

- `_id`: 帖子ID
- `post_title`: 帖子标题
- `post_view`: 浏览量
- `comment_num`: 评论数量
- `post_url`: 帖子链接
- `post_date`: 发帖日期（YYYY-MM-DD）
- `post_time`: 发帖时间（HH:MM）
- `post_author`: 发帖人

### 评论信息（comment_info 数据库）

- `post_id`: 关联的帖子ID
- `comment_content`: 评论内容
- `comment_like`: 点赞数
- `comment_date`: 评论日期（YYYY-MM-DD）
- `comment_time`: 评论时间（HH:MM）
- `sub_comment`: 是否为二级评论（0表示一级评论，1表示二级评论）

## 注意事项

1. **爬取速度控制**：每批股票爬取完成后会等待 30 秒再爬取下一批，以避免被网站封禁
2. **错误处理**：爬虫遇到错误会自动重试，不会中断整个爬取过程
3. **帖子筛选**：只爬取东方财富官方股吧的帖子，其他网站的帖子会被自动过滤
4. **日期格式**：所有日期格式为 `YYYY-MM-DD`，请确保输入格式正确

## 示例

```
$ python main_v2.py
读取到 6 个股票代码
请输入爬取截止日期（格式：YYYY-MM-DD）,如果直接回车将默认使用 2025-05-01: 2023-01-01

===== 正在爬取第 1 批股票，共 5 个 =====
000651: 已经成功爬取第 1 页帖子基本信息，已爬取 30 条
000001: 已经成功爬取第 1 页帖子基本信息，已爬取 30 条
...
000651: 已达到终止日期 2023-01-01，停止爬取
...

===== 第 1 批股票爬取完成 =====
等待 30 秒后继续爬取下一批...

===== 正在爬取第 2 批股票，共 1 个 =====
...

所有股票爬取完成！
```
