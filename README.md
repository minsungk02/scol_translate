📄 scol_translate Documentation

Requirements
	•	Git 2.27+
	•	git sparse-checkout --no-cone 옵션 지원 필요
	•	Python 3.8+
	•	OS: macOS / Linux / Windows(WSL)
	•	(선택) PyYAML

pip install pyyaml

tools/cfg.yaml에서 셀 크기 등을 읽고 싶을 때만 필요

⸻

Installation & Setup

# 1) 레포 클론
git clone https://github.com/<YOUR_ID>/scol_translate.git
cd scol_translate

# 2) upstream(원본 act) 연결 — 처음 1회만
git remote add upstream https://github.com/upoque/act.git

# 3) 권한 부여
chmod +x update.sh


⸻

Usage

기본 실행:

./update.sh <CELL_MM>

예시:

./update.sh 10          # 셀 크기 10mm
./update.sh 12 40 30    # 셀 12mm, 그리드 40x30 (메타 기록 포함)

실행 후 산출물은 output/solution_xxx/ 아래에 저장된다:
	•	pointdata_points.csv → TSPC POINT DATA 테이블 import용
	•	tspc_path_pointdata.prg → Toshiba SCOL 프로그램
	•	trans_meta.json → 변환 당시 파라미터 스냅샷

⸻

Conversion Process

Input
	•	JSON (solutions/solution_xxx.json)

{
  "path": [[x0, y0], [x1, y1], ...]
}



Transformation

좌표 변환 수식:

\begin{aligned}
gx &= (cx + \delta) \cdot cell \\
gy &= (cy + \delta) \cdot cell \\
\begin{bmatrix}rx \\ ry\end{bmatrix}
&= R(\theta) \cdot \begin{bmatrix}gx \\ gy\end{bmatrix} \\
X &= X_0 + s_x \cdot rx \\
Y &= Y_0 + s_y \cdot ry
\end{aligned}
	•	cell: 셀 크기(mm)
	•	δ: 0.0 (꼭짓점) / 0.5 (--center, 중심)
	•	s_x, s_y: 축 방향(±1)
	•	R(θ): θ만큼 회전 변환 행렬
	•	X0, Y0: 원점(mm)

Output
	•	CSV:

NAME,X,Y,Z,C,T,CONFIG
P000,123.000,456.000,10.000,0.000,0.000,RIGHTY


	•	PRG:

PROGRAM MAIN
SAFEZ = 100
WORKZ = 10
C = 0
T = 0
MOVE POINT(123.0, 456.0, SAFEZ, C, T, RIGHTY)
MOVE POINT(123.0, 456.0, WORKZ, C, T, RIGHTY)
END


	•	META(JSON): 변환 파라미터 기록

⸻

CLI Options (trans.py)

python3 tools/trans.py \
  --solutions_glob "solutions/solution_*.json" \
  --cell_mm 10 \
  --center \
  --origin_x 0 --origin_y 0 \
  --x_dir 1 --y_dir 1 \
  --theta_deg 0.0 \
  --safez 100 --workz 10 \
  --out_dir output

주요 옵션:
	•	--cell_mm : 셀 크기(mm) (CLI > cfg.yaml > 기본 10mm)
	•	--center : 셀 중심 기준 (없으면 꼭짓점)
	•	--origin_x, --origin_y : 원점(mm)
	•	--x_dir, --y_dir : 축 방향 (±1)
	•	--theta_deg : 회전(도)
	•	--safez, --workz : 로봇 Z축 위치
	•	--grid_w, --grid_h : 메타 기록용 (변환 자체에는 기본적으로 미사용)

⸻

Troubleshooting
	•	JSON이 안 받아질 때

git reset --hard
git sparse-checkout reapply


	•	권한 문제

chmod +x update.sh


	•	셀 크기 변경

./update.sh <CELL_MM>


	•	Y축 반전 필요(이미지 좌표 → 로봇 좌표)

./update.sh 10 --y_dir -1
