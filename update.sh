#!/usr/bin/env bash
set -euo pipefail

# 사용법: ./update.sh <CELL_MM> [GRID_W] [GRID_H]
# 예시  : ./update.sh 10 40 30
CELL_MM="${1:?Usage: ./update.sh <CELL_MM> [GRID_W] [GRID_H]}"
GRID_W="${2:-}"
GRID_H="${3:-}"

REMOTE="upstream"   # origin을 쓰면 origin으로 바꾸세요
BR="master"

cd "$(dirname "$0")"

# JSON만 sparse-checkout (디렉토리 항목 없이 패턴만!)
git sparse-checkout init --no-cone 2>/dev/null || true
git sparse-checkout set --no-cone "solutions/*.json" "solutions/**/*.json"

# 잔재 정리 후 패턴 재적용
git reset --hard
git sparse-checkout reapply

# 동기화
git fetch "$REMOTE"
git switch "$BR" 2>/dev/null || git switch --track "$REMOTE/$BR"
git pull "$REMOTE" "$BR"
echo "✅ solutions/*.json synced"

# 변환 실행: 셀 크기는 필수, 맵 사이즈는 있으면 넘김
CMD=(python3 tools/trans.py
  --solutions_glob "solutions/solution_*.json"
  --cell_mm "$CELL_MM"
  --center                           # 셀 '중심'을 찍는 경우(원하면 지워도 됨)
  --out_dir output
)

# 선택 인자(문서/메타 기록용)
if [[ -n "$GRID_W" ]]; then CMD+=(--grid_w "$GRID_W"); fi
if [[ -n "$GRID_H" ]]; then CMD+=(--grid_h "$GRID_H"); fi

"${CMD[@]}"

echo "✅ converted into output/"

# (선택) CROS 패키징도 함께
# python3 tools/pack_cros.py && echo "✅ CROS pack ready"