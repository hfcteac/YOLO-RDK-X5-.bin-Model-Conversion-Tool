"""
YOLOv5 .pt -> ONNX for Horizon X5 RDK
Run in Ubuntu 22.04 host (NOT in Docker)

Usage:
  python3 export_onnx.py              正常转换
  python3 export_onnx.py --clean      清理旧文件后重新转换
  python3 export_onnx.py --clean-only 仅清理，不转换
"""

import os, sys, shutil

# ============ CONFIG ============
PT_FILE   = "best.pt"
IMG_SIZE  = 640
OPSET     = 11
WORK_DIR  = "/home/hafeizhou/Desktop/x5_work"
# ===============================


def do_clean():
    """清理旧模型和中间产物"""
    print("=" * 50)
    print("🧹 开始清理旧模型文件...")
    print("=" * 50)

    files_to_remove = [
        "best.pt",
        "best.onnx",
        "yolo_config.yaml",
        "preprocess.py",
    ]
    dirs_to_remove = [
        "model_output",
        "calibration_data",
        "calibration_images",
        "yolov5",
    ]

    for f in files_to_remove:
        path = os.path.join(WORK_DIR, f)
        if os.path.isfile(path):
            os.remove(path)
            print(f"  ✓ 已删除: {f}")
        else:
            print(f"  - 跳过（不存在）: {f}")

    for d in dirs_to_remove:
        path = os.path.join(WORK_DIR, d)
        if os.path.isdir(path):
            shutil.rmtree(path)
            print(f"  ✓ 已删除目录: {d}/")
        else:
            print(f"  - 跳过（不存在）: {d}/")

    # 清 html 报告
    for f in os.listdir(WORK_DIR):
        if f.endswith(".html"):
            os.remove(os.path.join(WORK_DIR, f))
            print(f"  ✓ 已删除: {f}")

    print("=" * 50)
    print("✅ 清理完毕！")
    print(f"   当前目录: {WORK_DIR}")
    print(f"   剩余文件: {os.listdir(WORK_DIR)}")
    print("=" * 50)


def main():
    # --- 检查命令行参数 ---
    if "--clean-only" in sys.argv:
        do_clean()
        return

    if "--clean" in sys.argv:
        do_clean()

    yolov5_dir = os.path.join(WORK_DIR, "yolov5")

    # Step 0: clone yolov5 if needed
    if not os.path.isdir(yolov5_dir):
        print("[0/4] Cloning yolov5 from GitHub...")
        # set git proxy (7890)
        os.system("git config --global http.proxy http://192.168.192.1:7890")
        os.system("git config --global https.proxy http://192.168.192.1:7890")
        ret = os.system(f"cd {WORK_DIR} && git clone https://github.com/ultralytics/yolov5.git")
        if ret != 0:
            print("ERROR: git clone failed!"); sys.exit(1)

    # install deps (CPU only)
    os.system(f"pip install -r {yolov5_dir}/requirements.txt "
              "-i https://pypi.tuna.tsinghua.edu.cn/simple "
              "--trusted-host pypi.tuna.tsinghua.edu.cn 2>/dev/null")

    # Step 1: copy best.pt
    pt_src = os.path.join(WORK_DIR, PT_FILE)
    if not os.path.isfile(pt_src):
        print(f"ERROR: {pt_src} not found! Put your best.pt in {WORK_DIR} first.")
        sys.exit(1)
    pt_dst = os.path.join(yolov5_dir, PT_FILE)
    shutil.copy(pt_src, pt_dst)
    print(f"[1/4] Copied {PT_FILE}")

    # Step 2: export ONNX
    print(f"[2/4] Exporting ONNX (imgsz={IMG_SIZE}, opset={OPSET})...")
    cwd = os.getcwd(); os.chdir(yolov5_dir)
    ret = os.system(
        f"python3 export.py --weights {PT_FILE} --include onnx "
        f"--opset {OPSET} --imgsz {IMG_SIZE} {IMG_SIZE} --batch-size 1"
    )
    os.chdir(cwd)
    if ret != 0:
        print("ERROR: Export failed!"); sys.exit(1)

    # Step 3: move result
    onnx_src = os.path.join(yolov5_dir, PT_FILE.replace(".pt", ".onnx"))
    onnx_dst = os.path.join(WORK_DIR, "best.onnx")
    shutil.move(onnx_src, onnx_dst)
    print(f"[3/4] best.onnx saved!")
    print(f"[4/4] DONE! Next: docker run, hb_mapper checker")


if __name__ == "__main__":
    main()
