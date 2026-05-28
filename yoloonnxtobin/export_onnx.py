"""
YOLOv5 .pt -> ONNX for Horizon X5 RDK
Run in Ubuntu 22.04 host (NOT in Docker)
"""

import os, sys, shutil

# ============ CONFIG ============
PT_FILE   = "best.pt"
IMG_SIZE  = 640
OPSET     = 11
WORK_DIR  = "/home/hafeizhou/Desktop/x5_work"
# ===============================

def main():
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
