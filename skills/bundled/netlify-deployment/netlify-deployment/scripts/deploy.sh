#!/bin/bash
# =============================================================================
# Netlify 一鍵部署腳本
# 將指定資料夾直接推送到 Netlify
#
# 用法:
#   ./deploy.sh <資料夾路徑> [--prod] [--site-id SITE_ID] [--message "部署訊息"]
#
# 範例:
#   ./deploy.sh ./dist                          # 預覽部署
#   ./deploy.sh ./dist --prod                   # 正式部署
#   ./deploy.sh ./out --prod --message "v1.0"   # 帶訊息的正式部署
#   ./deploy.sh ./build --site-id abc123        # 指定站點部署
# =============================================================================

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 預設值
DEPLOY_DIR=""
PROD_FLAG=""
SITE_ID=""
MESSAGE=""

# 解析參數
while [[ $# -gt 0 ]]; do
  case $1 in
    --prod)
      PROD_FLAG="--prod"
      shift
      ;;
    --site-id)
      SITE_ID="$2"
      shift 2
      ;;
    --message)
      MESSAGE="$2"
      shift 2
      ;;
    --help|-h)
      echo "用法: ./deploy.sh <資料夾路徑> [選項]"
      echo ""
      echo "選項:"
      echo "  --prod              部署到 Production（正式環境）"
      echo "  --site-id ID        指定 Netlify 站點 ID"
      echo "  --message MSG       部署訊息"
      echo "  --help, -h          顯示此說明"
      exit 0
      ;;
    *)
      if [[ -z "$DEPLOY_DIR" ]]; then
        DEPLOY_DIR="$1"
      fi
      shift
      ;;
  esac
done

# 檢查資料夾參數
if [[ -z "$DEPLOY_DIR" ]]; then
  echo -e "${RED}錯誤: 請指定要部署的資料夾路徑${NC}"
  echo "用法: ./deploy.sh <資料夾路徑> [--prod] [--site-id SITE_ID]"
  exit 1
fi

# 檢查資料夾是否存在
if [[ ! -d "$DEPLOY_DIR" ]]; then
  echo -e "${RED}錯誤: 資料夾不存在: $DEPLOY_DIR${NC}"
  exit 1
fi

# 檢查 Netlify CLI 是否安裝
if ! command -v netlify &> /dev/null; then
  echo -e "${YELLOW}Netlify CLI 未安裝，正在安裝...${NC}"
  npm install -g netlify-cli
fi

# 檢查是否已登入
if ! netlify status &> /dev/null; then
  echo -e "${YELLOW}尚未登入 Netlify，請先登入...${NC}"
  netlify login
fi

# 統計檔案數量和大小
FILE_COUNT=$(find "$DEPLOY_DIR" -type f | wc -l)
DIR_SIZE=$(du -sh "$DEPLOY_DIR" | cut -f1)

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  Netlify 部署${NC}"
echo -e "${BLUE}======================================${NC}"
echo -e "  資料夾: ${GREEN}$DEPLOY_DIR${NC}"
echo -e "  檔案數: ${GREEN}${FILE_COUNT} 個${NC}"
echo -e "  大小:   ${GREEN}${DIR_SIZE}${NC}"
echo -e "  模式:   ${GREEN}${PROD_FLAG:-預覽部署}${NC}"
if [[ -n "$MESSAGE" ]]; then
  echo -e "  訊息:   ${GREEN}$MESSAGE${NC}"
fi
echo -e "${BLUE}======================================${NC}"
echo ""

# 組合部署指令
DEPLOY_CMD="netlify deploy --dir=\"$DEPLOY_DIR\""

if [[ -n "$PROD_FLAG" ]]; then
  DEPLOY_CMD="$DEPLOY_CMD --prod"
fi

if [[ -n "$SITE_ID" ]]; then
  DEPLOY_CMD="$DEPLOY_CMD --site=$SITE_ID"
fi

if [[ -n "$MESSAGE" ]]; then
  DEPLOY_CMD="$DEPLOY_CMD --message=\"$MESSAGE\""
fi

# 執行部署
echo -e "${YELLOW}正在部署...${NC}"
eval $DEPLOY_CMD

echo ""
echo -e "${GREEN}部署完成!${NC}"
