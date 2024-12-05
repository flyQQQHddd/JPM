# JVET Proposal Searcher

## 介绍

JVET Proposal Searcher 是一个用 Python 实现的命令行工具，用于管理和下载 JVET（Joint Video Exploration Team）会议的提案数据。通过该工具，您可以从 JVET 网站上自动抓取会议提案，并将其保存到 CSV 数据库中，还可以按关键字搜索提案标题或编号，并批量下载匹配的提案文件。

## 功能

- 更新数据库：从 JVET 网站获取提案数据并保存到本地 CSV 文件。
- 搜索提案：根据关键字搜索提案的标题或编号。
- 下载提案：按搜索结果批量下载提案文件。
- 会议列白：展示官网会议列表

## 更新

- 12.5: 新增提取会议列表的功能
- 11.7: 新增提取docx的功能
- 11.6: 优化命令行的使用
- 11.5: 提升下载稳定性
- 11.5: 添加彩色输出系统，添加提案分类功能，引入多线程处理

## 依赖

- requests
- pandas
- beautifulsoup4
- lxml

可以使用以下命令安装依赖项：

```python
pip install requests pandas beautifulsoup4 lxml
```

## 快速开始

请使用 `jvet.sh` 脚本（Windows 请使用 `jvet.ps1`）执行项目。首先在脚本中进行相应的配置：

```shell
PYTHON_SCRIPT="/Users/halley/代码/JPM/ProposalSearcher.py" # Python 文件路径
DATABASE_NAME="/Users/halley/代码/JPM/proposals.csv"       # 存储数据库的文件
DOWNLOAD_DIR="/Users/halley/Documents/jvet/download"      # 默认下载路径 
CONDA_ENV_NAME="JPM"  # 使用 Conda 配置的 Python 环境名称
```

然后调用脚本：

```shell
# 更新数据库
bash jvet.sh fetch
# 检索提案
bash jvet.sh search -k <keyword>
# 检索并下载提案
bash jvet.sh search -k <keyword> -d
# 检索并下载提案并指定下载路径
bash jvet.sh search -k <keyword> -d -o <dir>
# 从zip中提取docx
bash jvet.sh extract -i <input dir> -o <output dir>
# 获取 JVET 会议信息
bash jvet.sh info
```

## 使用文档

```plaintxt
usage: ProposalSearcher.py [-h] [-v] [--db_name DB_NAME] [--download_dir DOWNLOAD_DIR]
                           {fetch,search,extract,info} ...

JVET Proposal Searcher

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --db_name DB_NAME     Database name
  --download_dir DOWNLOAD_DIR
                        Download directory

Commands:
  {fetch,search,extract,info}
    fetch               Fetch the latest proposals from the JVET website
    search              Search for proposals by keyword
    extract             Extract .docx files from zip archives
    info                Information about JVET meetings
```

### fetch 子命令

使用 fetch 命令，

```plaintxt
usage: ProposalSearcher.py fetch [-h]

options:
  -h, --help  show this help message and exit
```

### search 子命令

使用 search 命令，根据关键字在提案的标题和编号中搜索匹配项。

```plaintxt
usage: ProposalSearcher.py search [-h] -k KEYWORD [-d] [-o OUTPUT]

options:
  -h, --help            show this help message and exit
  -k KEYWORD, --keyword KEYWORD
                        Keyword to search for in proposals
  -d, --download        Download proposals that match the search results
  -o OUTPUT, --output OUTPUT
                        Directory path to save downloaded proposals (default: ./download)
```

### extract 子命令

```plaintxt
usage: ProposalSearcher.py extract [-h] -i INPUT -o OUTPUT

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Directory path containing the zip files
  -o OUTPUT, --output OUTPUT
                        Directory path where extracted .docx files will be saved
```


## 注意事项

- 网络连接：程序需要连接到互联网，以从 JVET 网站抓取提案数据。
- 文件格式：抓取的数据将以 CSV 格式存储。每次更新将覆盖原有的 proposals.csv 文件。


## 贡献

如有问题或改进建议，欢迎在本项目中提交 Issue 或 Pull Request。

希望这个 README 文件能帮助您更好地理解和使用该工具！