
import os
import argparse
import pandas as pd
import requests
from bs4 import BeautifulSoup

class Output:

    def __init__(self):
        self.exit_when_error = True
        self.print_info = True

    def error(self, information):
        print(f'[ERROR]: {information}')
        if self.exit_when_error:
            exit(0)

    def info(self, information):
        if self.print_info:
            print(f'[INFO]: {information}')


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
            self.out.info(f'数据库 {self.db_name} 不存在！')
        else:
            self.out.info(f'已连接到数据库 {self.db_name}')

    def fetch_meeting_data(self, id_meeting):

        base_url = 'https://jvet-experts.org'
        meeting_url = f'/doc_end_user/current_meeting.php?id_meeting={id_meeting}&search_id_group=1&search_sub_group=1'

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
                            row_data.append(zip_file)
                            datas.append(row_data)

            return datas

        else:
            self.out.error(f'解析 {number_to_letters(id_meeting)} 会议时获取 HTML 失败！')
            return None

    def run_fetch(self):
        beg, end = 165, 200 # 起止会议的编号，根据JVET网站的结构，165代表第一次会议
        all_proposals = []
        self.out.info(f'开始解析 {number_to_letters(beg)}-{number_to_letters(end)} 会议......')
        for id_meeting in range(beg, end+1):

            proposals = self.fetch_meeting_data(id_meeting)
            if proposals is None:
                self.out.error(f'解析 {number_to_letters(id_meeting)} 会议失败')
            else:
                self.out.info(f'解析 {number_to_letters(id_meeting)} 会议成功，获取到 {len(proposals)} 份有效提案')
                all_proposals = all_proposals + proposals

        self.out.info(f'解析完成，共计获取到 {len(all_proposals)} 份有效提案，正在写入文件......')
        headers = ['JVET number','MPEG number','Created','First upload','Last upload','Title','Source','Download Link']
        df = pd.DataFrame(all_proposals, columns=headers)
        # 保存DataFrame为CSV文件
        df.to_csv(self.db_name, index=False, encoding='utf-8')
        self.out.info(f'写入文件 {self.db_name} 成功！')

    def run_search(self, keyword, download):

        matched = None
        try:
            content = pd.read_csv(self.db_name, sep=',', header=0, encoding='utf-8')
            matched = content[
                content['Title'].str.contains(keyword, case=False, na=False) |
                content['JVET number'].str.contains(keyword, case=False, na=False)
                ]
        except FileNotFoundError as _:
            self.out.error(f'打开数据库 {self.db_name} 失败！')

        if matched is not None:
            self.out.info(f'关键字「{keyword}」共匹配到 {len(matched)} 份提案：')
            for index, row in matched.iterrows():
                self.out.info(f"{row['JVET number']}: {row['Title']}")
        else:
            self.out.info(f'关键字「{keyword}」没有匹配到任何提案')
            return None

        if download:
            self.out.info(f'开始下载提案到目录 {download}......')
            if not os.path.exists(download):
                os.mkdir(download)

            for index, row in matched.iterrows():

                url = row['Download Link']
                response = requests.get(url)
                if response.status_code == 200:
                    filename = os.path.basename(url)
                    file_path = os.path.join(download, filename)
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    self.out.info(f"下载提案 {row['JVET number']} 成功")

                else:
                    self.out.info(f"下载提案 {row['JVET number']} 失败，状态码：{response.status_code}")


def main():
    parser = argparse.ArgumentParser(description='JVET Proposal Manager')
    parser.add_argument('--update', action='store_true', help='Fetch proposals from JVET website')
    parser.add_argument('--search', type=str, help='Search for proposals by keyword')
    parser.add_argument('--download', type=str, help='Download proposals in search results')

    args = parser.parse_args()
    app = ProposalManagerApp()

    if args.update:
        app.run_fetch()
    elif args.search:
        app.run_search(args.search, args.download)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

