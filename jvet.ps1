# PowerShell 脚本路径和参数
$PYTHON_SCRIPT = "C:\Users\halley\代码\JPM\ProposalSearcher.py"
$DATABASE_NAME = "C:\Users\halley\代码\JPM\proposals.csv"
$DOWNLOAD_DIR = "C:\Users\halley\Documents\jvet\download"
$CONDA_ENV_NAME = "JPM"

# 检查 Conda 是否已安装
if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    Write-Host "Conda is not installed or not in PATH. Please install Miniconda or Anaconda." -ForegroundColor Red
    exit 1
}

# 激活 Conda 环境
& conda "shell.powershell" "hook" | Out-String | Invoke-Expression

conda activate $CONDA_ENV_NAME
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to activate Conda environment: $CONDA_ENV_NAME" -ForegroundColor Red
    exit 1
}

# 运行 Python 脚本
python $PYTHON_SCRIPT --db_name=$DATABASE_NAME --download_dir=$DOWNLOAD_DIR @args
if ($LASTEXITCODE -ne 0) {
    Write-Host "Python script failed to execute." -ForegroundColor Red
    exit 1
}

# 关闭 Conda 环境
conda deactivate