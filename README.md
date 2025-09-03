# scol_translate

`upoque/act` 저장소의 `solutions/*.json`만 받아서 **Toshiba TSPC(SCOL)** 코드로 변환하고,  
`output/` 아래에 **CSV/PRG/메타** 파일을 생성하는 러너입니다.

> 한 줄 실행: `./update.sh <CELL_MM>`

---

## Quick Start

''''bash

# 1) 레포 클론
git clone https://github.com/<YOUR_ID>/scol_translate.git
cd scol_translate

# 2) upstream(원본 act) 연결 — 처음 1회만
git remote add upstream https://github.com/upoque/act.git

# 3) 권한 부여
chmod +x update.sh

# 4) 실행 (셀 크기 mm)
./update.sh 10
# 또는 메타 기록 겸: ./update.sh 12 40 30   # 셀 12mm, 그리드 40x30(메타 기록만)
