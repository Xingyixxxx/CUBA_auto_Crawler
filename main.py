from crawler import PostCrawler
from crawler import CommentCrawler
import threading
import time
from datetime import datetime
import os
from mongodb import MongoAPI


def read_stock_codes(file_path):
    """
    读取包含股票代码的文本文件
    :param file_path: 股票代码文件路径
    :return: 股票代码列表
    """
    with open(file_path, 'r') as f:
        # 去掉每行末尾的换行符，并过滤掉空行和注释行
        stock_codes = [line.strip() for line in f if line.strip() and not line.strip().startswith('//')]
    return stock_codes


def get_latest_date(stock_symbol):
    """
    获取指定股票在数据库中最新的帖子日期
    如果数据库为空或者不存在，返回一个默认日期
    :param stock_symbol: 股票代码
    :return: 格式为 'YYYY-MM-DD' 的日期字符串
    """
    try:
        postdb = MongoAPI('post_info', f'post_{stock_symbol}')
        latest_post = postdb.find_first()
        if latest_post and 'post_date' in latest_post:
            return latest_post['post_date']
    except Exception as e:
        print(f"获取 {stock_symbol} 最新日期时出错: {e}")
    
    # 如果数据库为空或出错，返回一个默认日期（比如当前日期）
    return datetime.now().strftime('%Y-%m-%d')


def post_thread_until_date(stock_symbol, end_date):
    """
    爬取帖子信息，直到指定日期
    :param stock_symbol: 股票代码
    :param end_date: 指定的结束日期
    """
    post_crawler = PostCrawler(stock_symbol)
    post_crawler.crawl_post_info_until_date(end_date)


def comment_thread_date(stock_symbol, start_date, end_date):
    """
    爬取评论信息，按照日期范围
    :param stock_symbol: 股票代码
    :param start_date: 开始日期
    :param end_date: 结束日期
    """
    comment_crawler = CommentCrawler(stock_symbol)
    comment_crawler.find_by_date(start_date, end_date)
    comment_crawler.crawl_comment_info()


def comment_thread_id(stock_symbol, start_id, end_id):
    """
    爬取评论信息，按照ID范围
    :param stock_symbol: 股票代码
    :param start_id: 开始ID
    :param end_id: 结束ID
    """
    comment_crawler = CommentCrawler(stock_symbol)
    comment_crawler.find_by_id(start_id, end_id)
    comment_crawler.crawl_comment_info()


def batch_crawl_stocks(stock_codes, end_date, batch_size=5):
    """
    批量爬取股票信息，每次爬取指定数量的股票
    :param stock_codes: 股票代码列表
    :param end_date: 爬取截止日期
    :param batch_size: 每批爬取的股票数量
    """
    total_stocks = len(stock_codes)
    for i in range(0, total_stocks, batch_size):
        batch = stock_codes[i:i+batch_size]
        threads = []
        
        print(f"\n===== 正在爬取第 {i//batch_size + 1} 批股票，共 {len(batch)} 个 =====")
        
        # 为每个股票创建一个线程
        for stock_code in batch:
            t = threading.Thread(target=post_thread_until_date, args=(stock_code, end_date))
            threads.append(t)
            t.start()
        
        # 等待所有线程完成
        for t in threads:
            t.join()
        
        print(f"\n===== 第 {i//batch_size + 1} 批股票爬取完成 =====")
        
        # 如果还有下一批，等待一段时间再继续，避免被网站封禁
        if i + batch_size < total_stocks:
            wait_time = 30
            print(f"等待 {wait_time} 秒后继续爬取下一批...")
            time.sleep(wait_time)


if __name__ == "__main__":
    # 股票代码文件路径
    stock_codes_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stock_codes.txt')
    
    # 读取股票代码
    stock_codes = read_stock_codes(stock_codes_file)
    if not stock_codes:
        print("股票代码文件为空或格式不正确，请检查 stock_codes.txt 文件")
        exit(1)
    
    print(f"读取到 {len(stock_codes)} 个股票代码")
    
    # 设置爬取截止日期，可以根据需要修改
    end_date = input("请输入爬取截止日期（格式：YYYY-MM-DD）,如果直接回车将默认使用 2025-05-01: ")
    if not end_date:
        end_date = "2025-05-01"
    
    # 设置每批爬取的股票数量
    batch_size = 5
    
    # 开始批量爬取
    batch_crawl_stocks(stock_codes, end_date, batch_size)
    
    print(f"\n所有股票爬取完成！")
