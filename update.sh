#!/usr/bin/env bash
# cron:0 9 * * *
# new Env("myhoyo更新脚本")

# 获取脚本所在目录
SCRIPT_DIR=$(dirname "$0")
# 如果需要绝对路径，可以在前面加上 `cd` 和 `pwd`
ABS_SCRIPT_DIR=$(cd "$SCRIPT_DIR" && pwd)
echo "Script directory is: $ABS_SCRIPT_DIR"

cd "$SCRIPT_DIR" && git pull

echo "Update script repository successfully!"