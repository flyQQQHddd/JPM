
import argparse
import threading
import time
import os
import shutil
import zipfile
import tempfile
import pandas as pd
import requests
from bs4 import BeautifulSoup

class Output:

    def __init__(self):
        self.exit_when_error = False # 遇到 ERROR 时终止程序
        self.print_info = True       # 输出 INFO 信息
        self.with_color = True       # 带有颜色的输出

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

    def _print_with_color(self, information, color=None):

        if self.with_color and color:
            print(f"{self.color_codes[color]}{information}{self.color_codes['reset']}")
        else:
            print(information)

    def message(self, information, msg_type="INFO", color=None):
        if msg_type == "INFO" and self.print_info:
            self._print_with_color(f'[INFO]: {information}', color)
        elif msg_type == "ERROR":
            self._print_with_color(f'[ERROR]: {information}', 'red')
            if self.exit_when_error:
                exit(0)
        else:
            self.message("消息类型错误", "INFO", "yellow")

def number_to_letters(n):
    n -= 164
    letter = ""
    while n > 0:
        n -= 1  # 调整为0索引
        letter = chr(n % 26 + ord('A')) + letter
        n //= 26
    return letter

class Parser:

    def __init__(self):

        self.parser = argparse.ArgumentParser(description='JVET Proposal Searcher')

    def init_parser(self):

        # 创建主解析器以及子解析器
        self.parser = argparse.ArgumentParser(description='JVET Proposal Searcher')
        self.parser.add_argument('-v', '--version', action='version', version='JVET Proposal Searcher 1.0')
        subparsers = self.parser.add_subparsers(title='Commands', dest='command', required=True)

        # 程序执行配置
        self.parser.add_argument("--db_name", type=str, help="Database name")
        self.parser.add_argument("--download_dir", type=str, help="Download directory")

        # fetch 子命令
        fetch_parser = subparsers.add_parser('fetch', help='Fetch the latest proposals from the JVET website')

        # search 子命令
        search_parser = subparsers.add_parser('search', help='Search for proposals by keyword')
        search_parser.add_argument('-k', '--keyword', type=str, required=True,
                                   help='Keyword to search for in proposals')
        search_parser.add_argument('-d', '--download', action='store_true',
                                   help='Download proposals that match the search results')
        search_parser.add_argument('-o', '--output', type=str,
                                   help='Directory path to save downloaded proposals')

        # extract 子命令
        extract_parser = subparsers.add_parser('extract', help='Extract .docx files from zip archives')
        extract_parser.add_argument('-i', '--input', type=str, required=True,
                                    help='Directory path containing the zip files')
        extract_parser.add_argument('-o', '--output', type=str, required=True,
                                    help='Directory path where extracted .docx files will be saved')

        # information
        information_parser = subparsers.add_parser('info', help='Information about JVET meetings')

        return self.parser.parse_args()

class ProposalSearcherApp:

    def __init__(self, db_name='proposals.csv', download_dir='download'):

        self.db_name = db_name
        self.out = Output()
        self.download_dir = download_dir
        self.base_url = 'https://jvet-experts.org'

    def fetch_meeting_list(self):

        meetings_url = "/doc_end_user/all_meeting.php"
        url = self.base_url + meetings_url
        response = requests.get(url)

        if response.status_code == 200:
            # 获取表格
            table = BeautifulSoup(response.text, 'lxml').find_all('table')[0]
            # 提取表格数据
            datas = []
            for row in table.find_all('tr')[1:]:  # 跳过表头
                columns = row.find_all('td')
                if len(columns) >= 5:  # 确保有足够的列
                    row_data = [column.text.strip() for column in columns]
                    if row_data[0] != '':  # 确保不是空行
                        links = row.find_all('a')
                        links = [link['href'] for link in links]
                        datas.append(row_data)

            df = pd.DataFrame(datas, columns=["Number", "Name", "Start Date", "End Date", "USL"])
            df.set_index("Number", inplace=True)
            return df

        else:
            self.out.message('解析会议列表时获取 HTML 失败！', 'ERROR')
            return None

    def fetch_meeting_data(self, id_meeting):

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
        url = self.base_url + meeting_url
        response = requests.get(url)

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
                            zip_file = self.base_url + zip_file
                            row_data = row_data[:7]
                            row_data.append(zip_file) # 文件链接
                            row_data.append(match_proposal_type(row_data[5])) # 提案类型
                            datas.append(row_data)
            return datas

        else:
            self.out.message(f'解析 {number_to_letters(id_meeting)} 会议时获取 HTML 失败！', "ERROR")
            return None

    def run_fetch(self, beg=1, end=36):

        meetings = self.fetch_meeting_list()

        # 起止会议的编号，根据JVET网站的结构，165代表第一次会议
        beg = 1 + 164
        end = len(meetings) + 164

        proposal_lists = [None] * (end - beg + 1)  # 初始化一个有序的结果列表
        self.out.message(f'开始解析 {number_to_letters(beg)} - {number_to_letters(end)} 会议（采用多线程，输出顺序可能混乱）......')

        start_time = time.time()  # 记录开始时间

        # 定义线程锁
        lock = threading.Lock()

        # 定义线程任务函数
        def fetch_data_and_collect(mid: int):
            proposals = self.fetch_meeting_data(mid)
            if proposals is None:
                self.out.message(f'解析 {number_to_letters(mid)} 会议失败', 'ERROR')
            else:
                self.out.message(f'解析 {number_to_letters(mid)} 会议成功，获取到 {len(proposals)} 份有效提案')
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
        self.out.message(f"执行时间: {execution_time:.2f} 秒")

        headers = ['JVET number','MPEG number','Created','First upload','Last upload','Title','Source','Download Link','Type']
        df = pd.DataFrame(all_proposals, columns=headers)

        self.out.message(f'解析完成，共计获取到 {len(all_proposals)} 份有效提案，正在写入文件......')
        os.makedirs(os.path.dirname(self.db_name), exist_ok=True)

        # 保存DataFrame为CSV文件
        df.to_csv(self.db_name, index=False, encoding='utf-8')
        self.out.message(f'写入文件 {self.db_name} 成功！', color='green')

    def run_search(self, keyword, download, download_dir=None):

        matched = None

        if download_dir is None:
             download_dir = self.download_dir

        try:
            content = pd.read_csv(self.db_name, sep=',', header=0, encoding='utf-8')
            matched = content[
                content['Title'].str.contains(keyword, case=False, na=False) |
                content['JVET number'].str.contains(keyword, case=False, na=False)
                ]
        except FileNotFoundError as _:
            matched = None
            self.out.message(f'打开数据库 {self.db_name} 失败！', 'ERROR')
            return None

        if matched is not None:
            self.out.message(f'关键字「{keyword}」共匹配到 {len(matched)} 份提案：')
            for index, row in matched.iterrows():
                if row['Type'] == 1:
                    color = 'yellow'
                elif row['Type'] == 2:
                    color = 'blue'
                elif row['Type'] == 3:
                    color = 'cyan'
                else:
                    color = 'black'

                self.out.message(f"{row['JVET number']}: {row['Title']}", color=color)
        else:
            self.out.message(f'关键字「{keyword}」没有匹配到任何提案')
            return None

        if download:
            self.out.message(f'开始下载提案到目录 {download_dir}......')
            os.makedirs(download_dir, exist_ok=True)

            for index, (_, row) in enumerate(matched.iterrows()):
                url = row['Download Link']
                filename = os.path.basename(url)
                file_path = os.path.join(download_dir, filename)
                if os.path.exists(file_path):
                    self.out.message(f"({index+1}/{len(matched)}) 提案 {row['JVET number']} 已存在于本地目录")
                    continue

                try:
                    # 请求下载
                    response = requests.get(url, timeout=(5, 15))
                    if response.status_code == 200:
                        with open(file_path, 'wb') as f:
                            f.write(response.content)
                        self.out.message(f"({index+1}/{len(matched)}) 下载提案 {row['JVET number']} 成功")
                    else:
                        self.out.message(f"({index+1}/{len(matched)}) 下载提案 {row['JVET number']} 失败，状态码：{response.status_code}", 'ERROR')

                except Exception:
                    self.out.message(f"({index+1}/{len(matched)}) 下载提案 {row['JVET number']} 请求错误", 'ERROR')

            self.out.message(f'下载提案完成到下载目录 {download_dir}')

    def run_extract(self, source_dir, destination_dir):

        # 检查源文件夹是否存在
        if not os.path.isdir(source_dir):
            self.out.message(f"源文件夹不存在: {source_dir}", 'ERROR')
            return None
        # 创建目标文件夹（如果不存在）
        os.makedirs(destination_dir, exist_ok=True)

        # 遍历源文件夹中的所有 zip 文件（递归查找）
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.endswith(".zip"):
                    zip_path = str(os.path.join(root, file))

                    # 创建一个临时文件夹用于解压缩
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # 解压到临时文件夹
                        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                            zip_ref.extractall(temp_dir)

                        # 查找解压后的 docx 文件，排除以 . 和 ~ 开头的文件
                        for docx_root, _, docx_files in os.walk(temp_dir):
                            for docx_file in docx_files:
                                if docx_file.endswith(".docx") and not docx_file.startswith((".", "~")):
                                    docx_path = os.path.join(docx_root, docx_file)
                                    # 将 docx 文件复制到目标文件夹
                                    shutil.copy(docx_path, destination_dir)

        self.out.message(f"所有 docx 文件已提取到: {destination_dir}")

    def run_info(self):

        meetings = self.fetch_meeting_list()
        print(meetings)


def main():

    # 解析参数
    args = Parser().init_parser()
    app = ProposalSearcherApp(args.db_name, args.download_dir)

    # 根据子命令执行不同的逻辑
    if args.command == 'fetch':
        app.run_fetch()
    elif args.command == 'search':
        app.run_search(args.keyword, args.download, args.output)
    elif args.command == 'extract':
        app.run_extract(args.input, args.output)
    elif args.command == 'info':
        app.run_info()

if __name__ == '__main__':

    main()

