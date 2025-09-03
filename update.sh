#!/usr/bin/env bash
set -euo pipefail

# 사용법: ./update.sh <CELL_MM> [GRID_W] [GRID_H]
CELL_MM="${1:?Usage: ./update.sh <CELL_MM> [GRID_W] [GRID_H]}"
GRID_W="${2:-}"
GRID_H="${3:-}"

# 원본(act) 설정
UPSTREAM_URL="https://github.com/upoque/act.git"
UPSTREAM_BRANCH="master"

# 현재 러너 레포 루트
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
CACHE_DIR="$ROOT_DIR/.cache/act_upstream"   # 원본을 받아올 임시/캐시 디렉토리
DEST_SOL="$ROOT_DIR/solutions"              # 러너 레포 내(JSON만 모아둘 폴더)
OUT_DIR="$ROOT_DIR/output"

echo "==> Upstream(JSON) sync to local solutions/"

# 1) upstream을 별도 캐시에 sparse clone (최초 1회) 또는 갱신
if [ ! -d "$CACHE_DIR/.git" ]; then
  mkdir -p "$CACHE_DIR"
  git clone --depth 1 --filter=blob:none --no-checkout -b "$UPSTREAM_BRANCH" "$UPSTREAM_URL" "$CACHE_DIR"
  (
    cd "$CACHE_DIR"
    git sparse-checkout init --no-cone
    git sparse-checkout set "solutions/*.json" "solutions/**/*.json"
    git checkout "$UPSTREAM_BRANCH"
  )
else
  (
    cd "$CACHE_DIR"
    git fetch origin "$UPSTREAM_BRANCH" --depth 1
    git checkout "$UPSTREAM_BRANCH"
    # 패턴 보장
    git sparse-checkout init --no-cone 2>/dev/null || true
    git sparse-checkout set "solutions/*.json" "solutions/**/*.json"
    git pull --ff-only origin "$UPSTREAM_BRANCH"
  )
fi

# 2) 캐시에서 러너 레포의 solutions/로 JSON만 동기화
rm -rf "$DEST_SOL"
mkdir -p "$DEST_SOL"
(
  cd "$CACHE_DIR/solutions"
  # 하위 디렉토리 구조 유지하며 *.json만 복사 (BSD/GNU find 모두 호환)
  find . -type f -name '*.json' | while IFS= read -r f; do
    mkdir -p "$DEST_SOL/$(dirname "$f")"
    cp "$f" "$DEST_SOL/$f"
  done
)
echo "✅ solutions/*.json synced into $DEST_SOL"

# 3) 변환 실행
mkdir -p "$OUT_DIR"
CMD=(python3 "$ROOT_DIR/tools/trans.py"
  --solutions_glob "$DEST_SOL/solution_*.json"
  --cell_mm "$CELL_MM"
  --center
  --out_dir "$OUT_DIR"
)
[[ -n "$GRID_W" ]] && CMD+=(--grid_w "$GRID_W")
[[ -n "$GRID_H" ]] && CMD+=(--grid_h "$GRID_H")
"${CMD[@]}"
echo "✅ converted into $OUT_DIR"

# 4) (선택) CROS 패키징
# python3 "$ROOT_DIR/tools/pack_cros.py" && echo "✅ CROS pack ready"
