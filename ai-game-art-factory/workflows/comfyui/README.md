# ComfyUI：尚未执行

当前云机的 `127.0.0.1:8188/system_stats` 与 `/object_info` 均连接拒绝。没有安装 ComfyUI、下载模型，也没有把空壳 JSON 标成可运行工作流。

本次 A 实验调用可用的 image_gen 服务，以角色参考和 Blender 四姿势条带联合生成四个关键姿态。它没有 ControlNet 分通道控制，不暴露模型版本与种子，也未在 RTX 3060 Ti 上执行。因此不能据此宣称 ComfyUI 时序方案已验证，更不能承诺精确重生成或 8GB 显存性能。

Windows 下一步先在项目根目录运行 `python scripts/factory.py doctor --output reports/environment-windows.json`。如 ComfyUI 使用其他本地端口，可加 `--comfy-url http://127.0.0.1:端口`。探针只读取本机 API 能力，不排队生图、不扫描模型权重、不输出凭据。完整安装路径与启动命令需在用户的 Windows 机器确认。

有本地能力报告后，再选择已安装且许可适用的模型与节点，导出真实 API workflow。必须记录模型文件哈希、节点版本、workflow 哈希、固定 seed、参考图哈希、采样器、步数、CFG、去噪强度、结构控制权重与批次顺序。先比较同一个四关键姿态组，再做连续序列；不得逐帧独立随机生图后宣称时序通过。

8GB 环境优先单批、较小工作分辨率、顺序执行和已有模型；是否使用卸载/低显存参数须以实际版本支持和峰值显存测量为准。不得自动下载大型模型或升级软件。
