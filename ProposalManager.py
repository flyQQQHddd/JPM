
import os
import argparse
import threading
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

class Output:

    def __init__(self):
        self.exit_when_error = False # 遇到 ERROR 时终止程序
        self.print_info = True # 输出 INFO 信息
        self.with_color = True # 带有颜色的输出

        # 定义颜色代码
        self.color_codes = {
            "black": "\033[30m",
            "red": "\033[31m",
            "green": "\033[32m",
            "yellow": "\033[33m",
            "blue": "\033[34m",
            "magenta": "\033[35m",
            "cyan": "\033[36m",
            "white": "\033[37m",
            "reset": "\033[0m"
        }

    def print_with_color(self, information, color=None):

        if self.with_color and color:
            print(f"{self.color_codes[color]}{information}{self.color_codes['reset']}")
        else:
            print(information)

    def error(self, information):
        self.print_with_color(f'[ERROR]: {information}', 'red')
        if self.exit_when_error:
            exit(0)

    def info(self, information, color=None):
        if self.print_info:
            self.print_with_color(f'[INFO]: {information}', color)

def number_to_letters(n):
    n -= 164
    letter = ""
    while n > 0:
        n -= 1  # 调整为0索引
        letter = chr(n % 26 + ord('A')) + letter
        n //= 26
    return letter

class ProposalManagerApp:

    def __init__(self, db_name='proposals.csv'):

        self.db_name = db_name
        self.out = Output()

        # initiate database
        if not os.path.exists(self.db_name):
            self.out.info(f'数据库 {self.db_name} 不存在！', 'red')
        else:
            self.out.info(f'已连接到数据库 {self.db_name}', 'green')

    def fetch_meeting_data(self, id_meeting):

        base_url = 'https://jvet-experts.org'
        meeting_url = f'/doc_end_user/current_meeting.php?id_meeting={id_meeting}&search_id_group=1&search_sub_group=1'

        def match_proposal_type(title:str):
            # 解析提案类型
            proposal_type = title.split(' ')[0].split(':')[0].lower()
            if 'ee' in proposal_type or 'ce' in proposal_type:
                proposal_type = 1
            elif 'ahg' in proposal_type:
                proposal_type = 2
            elif 'cross' in proposal_type:
                proposal_type = 3
            else:
                proposal_type = 0
            return proposal_type

        # 获取文件列表
        url = base_url + meeting_url
        response = requests.get(url.format(id_meeting))

        if response.status_code == 200:

            # 获取表格
            table = BeautifulSoup(response.text, 'lxml').find_all('table')[1]
            # 提取表格数据
            datas = []
            for row in table.find_all('tr')[1:]:  # 跳过表头
                columns = row.find_all('td')
                if len(columns) >= 7:  # 确保有足够的列
                    row_data = [column.text.strip() for column in columns]
                    if row_data[0] != '':  # 确保不是空行
                        links = row.find_all('a')
                        links = [link['href'] for link in links]
                        zip_file = list(filter(lambda link: link.endswith('.zip'), links))
                        if zip_file:  # 确保存在文件链接
                            zip_file = zip_file[0].replace('..', '')
                            zip_file = base_url + zip_file
                            row_data = row_data[:7]
                            row_data.append(zip_file) # 文件链接
                            row_data.append(match_proposal_type(row_data[5])) # 提案类型
                            datas.append(row_data)
            return datas

        else:
            self.out.error(f'解析 {number_to_letters(id_meeting)} 会议时获取 HTML 失败！')
            return None

    def run_fetch(self, beg=165, end=200):
        # 起止会议的编号，根据JVET网站的结构，165代表第一次会议

        proposal_lists = [None] * (end - beg + 1)  # 初始化一个有序的结果列表
        self.out.info(f'开始解析 {number_to_letters(beg)} - {number_to_letters(end)} 会议（采用多线程，输出顺序可能混乱）......')

        start_time = time.time()  # 记录开始时间

        # 定义线程锁
        lock = threading.Lock()

        # 定义线程任务函数
        def fetch_data_and_collect(mid: int):
            proposals = self.fetch_meeting_data(mid)
            if proposals is None:
                self.out.error(f'解析 {number_to_letters(mid)} 会议失败')
            else:
                self.out.info(f'解析 {number_to_letters(mid)} 会议成功，获取到 {len(proposals)} 份有效提案')
                with lock:
                    proposal_lists[mid-beg] = proposals  # 将结果按顺序插入

        # 启动线程池并行解析会议数据
        threads = []
        for id_meeting in range(beg, end + 1):
            thread = threading.Thread(target=fetch_data_and_collect, args=(id_meeting,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 合并结果为一个列表
        all_proposals = [proposal for proposal_list in proposal_lists for proposal in (proposal_list or [])]

        end_time = time.time()  # 记录结束时间
        execution_time = end_time - start_time
        self.out.info(f"执行时间: {execution_time:.2f} 秒")

        self.out.info(f'解析完成，共计获取到 {len(all_proposals)} 份有效提案，正在写入文件......')
        headers = ['JVET number','MPEG number','Created','First upload','Last upload','Title','Source','Download Link','Type']
        df = pd.DataFrame(all_proposals, columns=headers)
        # 保存DataFrame为CSV文件
        df.to_csv(self.db_name, index=False, encoding='utf-8')
        self.out.info(f'写入文件 {self.db_name} 成功！', 'green')

    def run_search(self, keyword, download, output):

        matched = None
        try:
            content = pd.read_csv(self.db_name, sep=',', header=0, encoding='utf-8')
            matched = content[
                content['Title'].str.contains(keyword, case=False, na=False) |
                content['JVET number'].str.contains(keyword, case=False, na=False)
                ]
        except FileNotFoundError as _:
            matched = None
            self.out.error(f'打开数据库 {self.db_name} 失败！')

        if matched is not None:
            self.out.info(f'关键字「{keyword}」共匹配到 {len(matched)} 份提案：')
            for index, row in matched.iterrows():
                if row['Type'] == 1:
                    color = 'yellow'
                elif row['Type'] == 2:
                    color = 'blue'
                elif row['Type'] == 3:
                    color = 'cyan'
                else:
                    color = 'black'

                self.out.info(f"{row['JVET number']}: {row['Title']}", color)
        else:
            self.out.info(f'关键字「{keyword}」没有匹配到任何提案')
            return None

        if download:
            self.out.info(f'开始下载提案到目录 {output}......')
            if not os.path.exists(output):
                os.mkdir(output)

            for index, (_, row) in enumerate(matched.iterrows()):
                url = row['Download Link']
                filename = os.path.basename(url)
                file_path = os.path.join(output, filename)
                if os.path.exists(file_path):
                    self.out.info(f"({index+1}/{len(matched)}) 提案 {row['JVET number']} 已存在于本地目录")
                    continue

                try:
                    # 请求下载
                    response = requests.get(url, timeout=(5, 15))
                    if response.status_code == 200:
                        with open(file_path, 'wb') as f:
                            f.write(response.content)
                        self.out.info(f"({index+1}/{len(matched)}) 下载提案 {row['JVET number']} 成功")
                    else:
                        self.out.error(f"({index+1}/{len(matched)}) 下载提案 {row['JVET number']} 失败，状态码：{response.status_code}")

                except Exception:
                    self.out.error(f"({index+1}/{len(matched)}) 下载提案 {row['JVET number']} 请求错误")

            self.out.info(f'下载提案完成到下载目录 {output}')


def main():

    # 创建主解析器
    parser = argparse.ArgumentParser(description='JVET Proposal Manager')
    parser.add_argument('-v', '--version', action='version', version='JVET Proposal Manager 1.0')

    # 添加子解析器
    subparsers = parser.add_subparsers(title='Commands', dest='command', required=True)

    # fetch 子命令
    fetch_parser = subparsers.add_parser('fetch', help='Fetch the latest proposals from the JVET website')

    # search 子命令
    search_parser = subparsers.add_parser('search', help='Search for proposals by keyword')
    search_parser.add_argument('-k', '--keyword', type=str, required=True,
                               help='Keyword to search for in proposals')
    search_parser.add_argument('-d', '--download', action='store_true',
                               help='Download proposals that match the search results')
    search_parser.add_argument('-o', '--output', type=str, default='download',
                               help='Directory path to save downloaded proposals (default: ./download)')

    # 解析参数
    args = parser.parse_args()
    app = ProposalManagerApp()

    # 根据子命令执行不同的逻辑
    if args.command == 'fetch':
        app.run_fetch()

    elif args.command == 'search':
        app.run_search(args.keyword, args.download, args.output)

if __name__ == '__main__':
    main()

