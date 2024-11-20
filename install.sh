#!/bin/bash

# 定义脚本目标名称
SOURCE_NAME="jps.sh"
# 定义目标名称
TARGET_NAME="jvet"
# 定义安装路径
INSTALL_DIR="/opt/tools"

# 检查用户是否具有 sudo 权限
if [ "$EUID" -ne 0 ]; then
  echo "Please run this script with sudo or as root."
  exit 1
fi

# 检查安装路径是否存在
if [ ! -d "$INSTALL_DIR" ]; then
  echo "Installation directory $INSTALL_DIR does not exist. Creating it now..."
  mkdir -p "$INSTALL_DIR"
  if [ $? -ne 0 ]; then
    echo "Failed to create directory $INSTALL_DIR. Please check permissions."
    exit 1
  fi
fi

# 检查源文件是否存在
if [ ! -f "$SOURCE_NAME" ]; then
  echo "Error: '$SOURCE_NAME' not found in the current directory."
  exit 1
fi

# 为脚本赋予可执行权限
chmod +x "$SOURCE_NAME"

# 将脚本移动到安装目录，并重命名为目标名称
cp "$SOURCE_NAME" "$INSTALL_DIR/$TARGET_NAME"

# 确认安装成功
if [ -f "$INSTALL_DIR/$TARGET_NAME" ]; then
  echo "Installed successfully! You can now run the script using the command: $TARGET_NAME"
else
  echo "Installation failed. Please check permissions and try again."
  exit 1
fi