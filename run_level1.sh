#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$ROOT_DIR/.env"
VARIANT="${1:-handson}"
PORT="${2:-8080}"
APP_DIR="$ROOT_DIR/level1/$VARIANT"

if [ ! -d "$APP_DIR" ]; then
  echo "ERROR: 경로가 없습니다: $APP_DIR"
  echo "사용법: ./run_level1.sh [handson|solution] [port]"
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: .env 파일이 없습니다. .env.example을 복사 후 API Key를 입력하세요."
  echo "  cp .env.example .env"
  exit 1
fi

export GOOGLE_GENAI_USE_VERTEXAI=False
export GOOGLE_API_KEY
GOOGLE_API_KEY="$(grep '^GOOGLE_API_KEY=' "$ENV_FILE" | cut -d '=' -f2-)"

if [ -z "${GOOGLE_API_KEY}" ] || [ "${GOOGLE_API_KEY}" = "your-gemini-api-key-here" ]; then
  echo "ERROR: .env 파일에 유효한 GOOGLE_API_KEY를 입력하세요."
  echo "  발급: https://aistudio.google.com/app/apikey"
  exit 1
fi

if lsof -ti:"$PORT" >/dev/null 2>&1; then
  echo "포트 ${PORT} 사용 중인 프로세스 종료..."
  lsof -ti:"$PORT" | xargs kill -9 2>/dev/null || true
  sleep 1
fi

echo "==================================="
echo " Level 1 / ${VARIANT} 실행"
echo " URL: http://localhost:${PORT}"
echo "==================================="
echo ""
echo " 1. 브라우저에서 위 URL 접속"
echo " 2. 'Select an app' → crypto_dashboard 선택"
echo " 3. 종료: Ctrl+C"
echo ""

cd "$APP_DIR"
adk web --port "$PORT" --allow_origins "*" --reload_agents .
