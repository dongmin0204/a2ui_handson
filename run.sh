#!/bin/bash
set -e

if [ ! -f .env ]; then
  echo "ERROR: .env 파일이 없습니다. .env.example을 복사 후 API Key를 입력하세요."
  echo "  cp .env.example .env"
  exit 1
fi

export GOOGLE_GENAI_USE_VERTEXAI=False
export GOOGLE_API_KEY=$(grep GOOGLE_API_KEY .env | cut -d '=' -f2)

if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "your-gemini-api-key-here" ]; then
  echo "ERROR: .env 파일에 유효한 GOOGLE_API_KEY를 입력하세요."
  echo "  발급: https://aistudio.google.com/app/apikey"
  exit 1
fi

PORT=${1:-8080}

# 기존 프로세스 종료 후 재시작
if lsof -ti:"$PORT" >/dev/null 2>&1; then
  echo "포트 ${PORT} 사용 중인 프로세스 종료..."
  lsof -ti:"$PORT" | xargs kill -9 2>/dev/null
  sleep 2
fi

echo "==================================="
echo " ADK + A2UI Agent 서버 시작"
echo " URL: http://localhost:${PORT}"
echo "==================================="
echo ""
echo " 1. 브라우저에서 위 URL 접속"
echo " 2. 'Select an app' → a2ui_agent 선택"
echo " 3. 프롬프트 입력: 오늘의 할 일 체크리스트 만들어줘"
echo " 4. 종료: Ctrl+C"
echo ""

adk web --port "$PORT" --allow_origins "*" --reload_agents .
