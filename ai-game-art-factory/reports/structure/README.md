# Blender 结构与投影实测

状态：**结构技术检查通过；不属于角色美术成品，也未通过人工美术验收。**

实际运行 Blender 4.3.2 的后台 Python 接口，Cycles CPU，4 个线程、4 samples。未安装插件、模型或外部素材。当前发行版不含 OpenImageDenoise，首次运行失败后关闭了对纯色引导图没有必要的降噪，并重新成功执行；这不是降低成品美术质量，因为本实验只生产结构通道。

## 已生成

- 两个真正独立的前方 45° 正交视角，不使用左右镜像替代。
- 待机、蓄力、击出、收势 4 个**诊断关键姿势**，时间分别为 0 / 0.15 / 0.31 / 0.60 秒。
- 两个不同锤头体积的结构代理，共 16 组姿势/方向/武器组合。
- 每组提供 flat、pose、world-space normal、depth、silhouette，合计 80 张 256×256 RGBA PNG。
- `projection.json`：每个关节的世界位置、二维像素坐标、相机深度、远近排序及实际网格握点测量。
- `../../workflows/blender/structure_probe.blend`：包含真实 Armature、关键帧、命名锚点、固定相机和结构网格的可检查快照。
- `../../previews/structure/contact-sheet.png`、`guide-channels.png`：已实际查看的结构接触表。

## 自动检查证据

`qa.json` 验证 80 张图的存在性、RGBA/尺寸、非空与边界未裁切；16 组的左右上臂长度 0.43、前臂长度 0.40 均固定。锤柄网格局部握点经实际 `matrix_world` 变换后与手掌对象中心比较，最大误差约 5.96×10⁻⁸ 场景单位。每个视角内的脚底锚点漂移为 0 像素。

法线和深度 PNG 使用 Raw 色彩变换；normal 为世界法线从 [-1,1] 映射到 [0,1] 的 8-bit 数据，depth 为相机距离 7–11 映射到白–黑。它们只作为当前实验的引导/观察通道；连接具体 ControlNet/预处理器前必须核对其期望的相机法线、深度方向和归一化约定，不能直接假定兼容。

## 已观察的局限

几何体没有服饰设计，手掌只是体积，没有手指包覆握柄；所以握点误差为零**不代表持握美术合格**。四个关键姿势用于检验投影跨度、遮挡变化和轨迹，不能用来宣称完整流畅攻击动画已经完成。没有重心转移、躯干扭转、脚步、打击停顿或辅助动作，必须在美术样板认可后另做动画设计。

`hammer_crescent` 是一个尺寸不同的椭球锤头体积代理，不是完成的月牙锤造型。两个武器复用了原始身体姿势，证明结构挂点可复用，未证明美术资源可直接运行时换装。

右前视角中挥出的武器与前臂发生较大缩短，说明 C 路线需要按透视缩短变形或换图。全局深度排序只能确定部件整体前后，无法表达手指/握柄交织遮挡；必须增加手背、握柄、前景手指等局部分层。A 路线仅完成结构输入，尚未执行受控 AI 时序重绘，不能评定其帧间一致性。

## 复现

在 `ai-game-art-factory` 目录执行：

```sh
blender --background --threads 4 --python workflows/blender/structure_probe.py
python scripts/doctor.py --output reports/environment-cloud.json
python workflows/blender/summarize_probe.py
```

其中 doctor 是独立环境检查，并非渲染所需。Windows 使用实际 Blender 可执行文件路径，例如 PowerShell 的 `& "...\blender.exe" --background --threads 4 --python workflows/blender/structure_probe.py`；不要未经探查就假定安装路径。

参数 `-- --output-root <项目根目录> --samples 4` 可覆盖输出根目录。脚本仅依赖 Blender 自带 Python；接触表与验证脚本另外需要 Pillow。输出文件哈希见 `manifest.json`，实际日志见 `blender.log`。
