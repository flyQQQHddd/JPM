#!/bin/bash

PYTHON_SCRIPT="/Users/halley/Documents/jvet/ProposalSearcher.py"
CONDA_ENV_NAME="jvetDocxEnv"

# 激活 Conda 环境
if ! command -v conda &> /dev/null; then
  echo "Conda is not installed or not in PATH. Please install Miniconda or Anaconda."
  exit 1
fi
# 使用 conda 激活环境
eval "$(conda shell.bash hook)"  # 使脚本能够激活 Conda 环境
conda activate "$CONDA_ENV_NAME"
if [ $? -ne 0 ]; then
  echo "Failed to activate Conda environment: $CONDA_ENV_NAME"
  exit 1
fi
python "$PYTHON_SCRIPT" "$@"
conda deactivate