# tools/trans.py
# -*- coding: utf-8 -*-
import json, os, math, argparse, glob
from datetime import datetime
try:
    import yaml  # 선택 의존성
except Exception:
    yaml = None

def load_json(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def load_yaml_cell_mm(p, default_cell=10.0):
    if yaml is None or not p or not os.path.exists(p):
        return default_cell
    with open(p, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    for k in ("cell", "cell_mm", "cell_size_mm", "cell_size"):
        if k in cfg:
            v = cfg[k]
            if isinstance(v, (int, float)): return float(v)
            if isinstance(v, (list, tuple)) and v: return float(v[0])
    return default_cell

def grid_to_mm(cx, cy, cell, ox, oy, xsign, ysign, delta, theta_deg):
    gx = (float(cx) + delta) * cell
    gy = (float(cy) + delta) * cell
    th = math.radians(theta_deg)
    rx =  gx*math.cos(th) - gy*math.sin(th)
    ry =  gx*math.sin(th) + gy*math.cos(th)
    return ox + xsign*rx, oy + ysign*ry

def emit_prg(points, safez, workz, c_val, t_val, config):
    lines = ["PROGRAM MAIN",
            f"SAFEZ = {safez}",
            f"WORKZ = {workz}",
            f"C = {c_val}",
            f"T = {t_val}"]
    for x,y in points:
        lines.append(f"MOVE POINT({x:.1f}, {y:.1f}, SAFEZ, C, T, {config})")
        lines.append(f"MOVE POINT({x:.1f}, {y:.1f}, WORKZ, C, T, {config})")
    lines.append("END")
    return "\n".join(lines)

def convert_one(json_path, out_root, cell_mm, ox, oy, xdir, ydir, delta, theta,
                safez, workz, c_val, t_val, config, grid_w, grid_h):
    name = os.path.splitext(os.path.basename(json_path))[0]
    out_dir = os.path.join(out_root, name)
    os.makedirs(out_dir, exist_ok=True)

    cells = load_json(json_path).get("path", [])
    pts = [grid_to_mm(cx, cy, cell_mm, ox, oy, xdir, ydir, delta, theta) for cx,cy in cells]

    with open(os.path.join(out_dir, "pointdata_points.csv"), "w", encoding="utf-8") as f:
        f.write("NAME,X,Y,Z,C,T,CONFIG\n")
        for i,(x,y) in enumerate(pts):
            f.write(f"P{i:03d},{x:.3f},{y:.3f},{workz:.3f},{c_val:.3f},{t_val:.3f},RIGHTY\n")

    with open(os.path.join(out_dir, "tspc_path_pointdata.prg"), "w", encoding="utf-8") as f:
        f.write(emit_prg(pts, safez, workz, c_val, t_val, "RIGHTY"))

    meta = {
        "source_json": json_path,
        "cell_mm": cell_mm,
        "origin": [ox, oy],
        "x_dir": xdir, "y_dir": ydir,
        "delta": delta, "theta_deg": theta,
        "safez": safez, "workz": workz,
        "grid_w": grid_w, "grid_h": grid_h,   # ← 기록용
        "timestamp": datetime.now().isoformat(timespec="seconds")
    }
    with open(os.path.join(out_dir, "trans_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

def main():
    ap = argparse.ArgumentParser(description="solutions → TSPC(SCOL) batch converter")
    ap.add_argument("--solutions_glob", default="solutions/solution_*.json")
    ap.add_argument("--cfg", default="tools/cfg.yaml")  # 있으면 읽음(선택)
    ap.add_argument("--out_dir", default="output")
    # 좌표 변환
    ap.add_argument("--cell_mm", type=float, default=None)
    ap.add_argument("--origin_x", type=float, default=0.0)
    ap.add_argument("--origin_y", type=float, default=0.0)
    ap.add_argument("--x_dir", type=int, default=1, choices=[-1,1])
    ap.add_argument("--y_dir", type=int, default=1, choices=[-1,1])
    ap.add_argument("--center", action="store_true")
    ap.add_argument("--theta_deg", type=float, default=0.0)
    # 동작 파라미터
    ap.add_argument("--safez", type=float, default=100.0)
    ap.add_argument("--workz", type=float, default=10.0)
    ap.add_argument("--c_val", type=float, default=0.0)
    ap.add_argument("--t_val", type=float, default=0.0)
    # 문서/메타용 그리드 사이즈(선택)
    ap.add_argument("--grid_w", type=int, default=None)
    ap.add_argument("--grid_h", type=int, default=None)

    args = ap.parse_args()

    # cell_mm 우선순위: CLI > cfg.yaml > 10mm
    cell_mm = args.cell_mm if args.cell_mm is not None else load_yaml_cell_mm(args.cfg, 10.0)
    delta = 0.5 if args.center else 0.0

    os.makedirs(args.out_dir, exist_ok=True)
    paths = sorted(glob.glob(args.solutions_glob))
    if not paths:
        raise SystemExit(f"No JSON matched: {args.solutions_glob}")
    for jp in paths:
        convert_one(jp, args.out_dir, cell_mm, args.origin_x, args.origin_y,
                    args.x_dir, args.y_dir, delta, args.theta_deg,
                    args.safez, args.workz, args.c_val, args.t_val, "RIGHTY",
                    args.grid_w, args.grid_h)
    print(f"[OK] converted {len(paths)} file(s) into '{args.out_dir}'")

if __name__ == "__main__":
    main()