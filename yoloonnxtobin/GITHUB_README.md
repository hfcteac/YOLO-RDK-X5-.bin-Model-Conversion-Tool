# 🧠 YOLO → RDK X5 .bin 模型转换工具

[![Platform](https://img.shields.io/badge/platform-RDK%20X5-orange)](https://developer.d-robotics.cc/)
[![Python](https://img.shields.io/badge/python-3.10-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![Docker](https://img.shields.io/badge/docker-ai__toolchain__v1.2.8-blue)](https://hub.docker.com/r/openexplorer/ai_toolchain_ubuntu_20_x5_cpu)

> 🚀 将 YOLOv5/YOLOv8/YOLO11 等 PyTorch 模型一键转换为地平线 RDK X5（旭日5）开发板可运行的 `.bin` 格式。

---

## 📸 概览

```
best.pt  ──→  best.onnx (opset=11)  ──→  best.bin (BPU)  ──→  RDK X5 运行
              ↑ 模型验证                   ↑ 量化编译            ↑ 实测 FPS=40+
```

---

## ✨ 特性

| 特性 | 说明 |
|------|------|
| 🔄 **双路线支持** | YOLOv5 传统路线 + Ultralytics（v8/v10/v11）新路线 |
| 🐳 **Docker 开箱即用** | 无需手动装工具链，拉镜像即可 |
| ✅ **无板验证** | `hb_verifier` 在 PC 端仿真验证 .bin 正确性 |
| 📊 **性能报告** | 自动生成静态性能 HTML（FPS/延迟/带宽） |
| 📖 **详尽文档** | 13 个踩坑记录 + 完整指令 + Word 说明书 |

---

## ⚡ 快速开始

```bash
# 1. 拉 Docker 工具链（注意版本号不是 latest！）
docker pull openexplorer/ai_toolchain_ubuntu_20_x5_cpu:v1.2.8

# 2. PT → ONNX（YOLOv5 路线示例）
cd yolov5
python3 export.py --weights best.pt --include onnx --opset 11 --imgsz 640 640

# 3. 启动容器
docker run -it --rm -v $(pwd):/workspace openexplorer/ai_toolchain_ubuntu_20_x5_cpu:v1.2.8

# 4. 容器内转换 ONNX → .bin
cd /workspace
hb_mapper checker --model-type onnx --model best.onnx --march bayes-e
hb_mapper makertbin --config yolo_config.yaml --model-type onnx

# 5. 验证（无需板子）
cd model_output
hb_verifier -m model_quantized_model.onnx,model.bin -s True
# → Strict check PASSED ✅
```

---

## 📊 实测性能

| 指标 | 数值 |
|------|------|
| **芯片** | RDK X5（旭日5 / Sunrise5） |
| **模型** | YOLOv5s 640×640 |
| **预估 FPS** | **40.22** |
| **单帧延迟** | **24.9 ms** |
| **DDR 带宽** | 153 MB/frame |
| **算子运行位置** | 100% BPU（零 CPU 回退） |

---

## 📁 文件说明

| 文件 | 用途 |
|------|------|
| `README.md` | 📘 完整开发文档（含 YOLOv5 / Ultralytics 双路线） |
| `export_onnx.py` | 🐍 YOLOv5 一键转 ONNX 脚本（自动克隆 yolov5 仓库） |
| `convert_to_docx.ps1` | 🔧 一键生成 Word 说明书（Windows） |
| `YOLO转RDK_X5_bin完整指南.docx` | 📄 可打印的 Word 说明书（带目录/章节编号/版权） |

---

## 🧩 支持的模型

| 框架 | 版本 | 状态 |
|------|------|:--:|
| YOLOv5 | v5.0 ~ v7.0 | ✅ 已验证 |
| YOLOv8 | Ultralytics | ✅ |
| YOLOv10 | Ultralytics | ✅ |
| YOLO11 | Ultralytics | ✅ |
| YOLO12/13 | Ultralytics | ✅ |

---

## 🧹 换模型清理

> 🔴 **血泪教训：清理命令必须在宿主机执行，禁止在 Docker 容器内执行！**
> 容器内 `/workspace` 挂载了宿主机目录，容器里删 = 宿主机丢。先 `exit` 退出容器再清理。

换新 `best.pt` 后，**在宿主机**执行：

```bash
cd ~/Desktop/x5_work
rm -f best.pt best.onnx yolo_config.yaml preprocess.py *.html
rm -rf model_output/ calibration_data/ calibration_images/ yolov5/
```

> 详见 [README.md](./README.md)「换模型 / 清理旧文件」章节。

---

## 🐞 常见坑速查

| # | 症状 | 解法 |
|---|------|------|
| 1 | `latest` 标签不存在 | 拉 `v1.2.8` |
| 2 | opset=18 导致 checker 失败 | 装 `torch==1.13.1+cpu` |
| 3 | IR version 10 > 9 | `m.ir_version=7` |
| 4 | `input_shape` 用逗号报错 | 改用 `x`：`1x3x640x640` |
| 5 | `compiler_parameters` 报错 | `march` 放 `model_parameters` 下 |

> 完整踩坑清单见 [README.md](./README.md) 附录 B。

---

## 👤 作者

| | |
|---|---|
| **姓名** | 宋楠 |
| **职位** | 嵌入式工程师 |
| 📱 **电话** | 15840252139 |
| 🛰️ **公众号** | 周哈飞科技园 |
| 📺 **B站** | [科大楠哥](https://space.bilibili.com/) |

---

## 📄 许可证

© 2026 宋楠。本项目仅供学习交流使用，未经许可不得用于商业用途。

---

## 🔗 参考

- [地平线 X5 工具链文档](https://developer.d-robotics.cc/api/v1/fileData/x5_doc-v126cn/index.html)
- [RDK Model Zoo](https://github.com/D-Robotics/rdk_model_zoo)
- [Docker 镜像](https://hub.docker.com/r/openexplorer/ai_toolchain_ubuntu_20_x5_cpu)

---

<p align="center">
  <sub>Made with ❤️ by 宋楠 | 周哈飞科技园 | 科大楠哥</sub>
</p>
