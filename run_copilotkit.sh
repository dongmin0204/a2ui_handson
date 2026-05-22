#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$ROOT_DIR/.env"
APP_DIR="$ROOT_DIR/CopilotKit/examples/integrations/adk"

if [ ! -d "$APP_DIR" ]; then
  echo "ERROR: CopilotKit ADK 예제 경로가 없습니다: $APP_DIR"
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

for PORT in 3000 8000; do
  if lsof -ti:"$PORT" >/dev/null 2>&1; then
    echo "포트 ${PORT} 사용 중인 프로세스 종료..."
    lsof -ti:"$PORT" | xargs kill -9 2>/dev/null || true
    sleep 1
  fi
done

echo "==================================="
echo " CopilotKit ADK 예제 실행"
echo " UI:    http://localhost:3000"
echo " Agent: http://localhost:8000"
echo "==================================="
echo ""
echo " 추천 프롬프트:"
echo " - 오늘 할 계획 하나 추가해줘."
echo " - 테마를 초록색으로 바꾸고 글자는 검은색으로 해줘."
echo " - 구글 검색으로 엔비디아 5일 차트 보여줘."
echo ""

cd "$APP_DIR"
if ! command -v npm >/dev/null 2>&1; then
  NVM_SH="${NVM_DIR:-/usr/local/share/nvm}/nvm.sh"
  if [ -s "$NVM_SH" ]; then
    . "$NVM_SH"
    nvm use default >/dev/null
  fi
fi

if [ ! -d "node_modules" ]; then
  npm install
fi
npm run dev
