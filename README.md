# JVET Proposal Manager

## 介绍

JVET Proposal Manager 是一个用 Python 实现的命令行工具，用于管理和下载 JVET（Joint Video Exploration Team）会议的提案数据。通过该工具，您可以从 JVET 网站上自动抓取会议提案，并将其保存到 CSV 数据库中，还可以按关键字搜索提案标题或编号，并批量下载匹配的提案文件。

## 功能

- 更新数据库：从 JVET 网站获取提案数据并保存到本地 CSV 文件。
- 搜索提案：根据关键字搜索提案的标题或编号。
- 下载提案：按搜索结果批量下载提案文件。

## 更新

- 11.6: 优化命令行的使用
- 11.5: 提升下载稳定性
- 11.5: 添加彩色输出系统，添加提案分类功能，引入多线程处理

## 依赖

- requests
- pandas
- beautifulsoup4

可以使用以下命令安装依赖项：

```python
pip install requests pandas beautifulsoup4 lxml
```

## 快速开始

```shell
# 更新数据库
python ProposalManager.py fetch
# 检索提案
python ProposalManager.py search -k <keyword>
# 检索并下载提案
python ProposalManager.py search -k <keyword> -d
# 检索并下载提案并指定下载路径
python ProposalManager.py search -k <keyword> -d -o <dir>
```

## 使用文档

```plaintxt
usage: ProposalManager.py [-h] [-v] {fetch,search} ...

JVET Proposal Manager

options:
  -h, --help      show this help message and exit
  -v, --version   show program's version number and exit

Commands:
  {fetch,search}
    fetch         Fetch the latest proposals from the JVET website
    search        Search for proposals by keyword
```

### fetch 子命令

使用 fetch 命令，

```plaintxt
usage: ProposalManager.py fetch [-h]

options:
  -h, --help  show this help message and exit
```

### search 子命令

使用 search 命令，根据关键字在提案的标题和编号中搜索匹配项。

```plaintxt
usage: ProposalManager.py search [-h] -k KEYWORD [-d] [-o OUTPUT]

options:
  -h, --help            show this help message and exit
  -k KEYWORD, --keyword KEYWORD
                        Keyword to search for in proposals
  -d, --download        Download proposals that match the search results
  -o OUTPUT, --output OUTPUT
                        Directory path to save downloaded proposals (default: ./download)
```

## 项目结构

- ProposalManagerApp：主应用类，包含数据获取、搜索和下载的核心功能。
- Output：日志输出类，用于打印错误和信息日志。
- number_to_letters：将会议编号转换为字母编码。

## 注意事项

- 网络连接：程序需要连接到互联网，以从 JVET 网站抓取提案数据。
- 文件格式：抓取的数据将以 CSV 格式存储。每次更新将覆盖原有的 proposals.csv 文件。

## 贡献

如有问题或改进建议，欢迎在本项目中提交 Issue 或 Pull Request。

希望这个 README 文件能帮助您更好地理解和使用该工具！