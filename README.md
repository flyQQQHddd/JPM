# JVET Proposal Manager

## 介绍

JVET Proposal Manager 是一个用 Python 实现的命令行工具，用于管理和下载 JVET（Joint Video Exploration Team）会议的提案数据。通过该工具，您可以从 JVET 网站上自动抓取会议提案，并将其保存到 CSV 数据库中，还可以按关键字搜索提案标题或编号，并批量下载匹配的提案文件。

## 功能

- 更新数据库：从 JVET 网站获取提案数据并保存到本地 CSV 文件。
- 搜索提案：根据关键字搜索提案的标题或编号。
- 下载提案：按搜索结果批量下载提案文件。

## 更新

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

## 使用方法

### 更新提案数据库

使用 --update 选项来从 JVET 网站获取会议提案并更新到本地数据库中。数据将保存到名为 proposals.csv 的文件中（默认值）。

```python
python ProposalManager.py --update
```

### 搜索提案

使用 --search 选项，根据关键字在提案的标题和编号中搜索匹配项。

```python
python ProposalManager.py --search <关键字>
```

例如，搜索包含“编码”的提案：

```python
python ProposalManager.py --search 编码
```

### 下载提案

使用 --download 参数指定下载路径，可将搜索结果中的提案文件批量下载到指定目录中。

```python
python ProposalManager.py --search <关键字> --download <下载路径>
```

例如，将匹配到的提案下载到 proposals 目录中：

```python
python ProposalManager.py --search 编码 --download proposals
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