# AI 美术流水线架构

本项目当前是用于选择生产路线的最小实验工具集。核心资产尚未通过美术验收，因此架构围绕可追溯输入、独立脚本、可查看结果和明确阶段门建立，不建设 Web 管理平台，也不把实验输出自动升级为最终游戏素材。

## 范围和模块边界

```text
Style Profile + 原画/部件/武器版本 + 人工审核状态
                         |
         +---------------+----------------+
         |               |                |
  A: Blender 引导   B: 二维关键点     C: Blender 投影
    + 联合重绘         + 部件             + 部件
         |               |                |
         +---------- 诊断导出 ------------+
                         |
       PNG 分层 + Sprite Sheet + JSON + 预览
                         |
        技术检查 / AI 视觉意见 / 人工美术验收
                         |
           Godot 实际尺寸验证与阶段报告
```

Python CLI 是统一调度入口；每个实验仍保留可以单独运行的脚本，便于定位问题。配置描述风格和目标，原画/部件保存美术内容，驱动数据保存动作，武器保存自己的握点和偏移。不得把角色身份、特定锤子像素坐标和通用驱动逻辑混为一体。

| 模块 | 当前证据与边界 |
|---|---|
| CLI | `scripts/factory.py`：doctor、structure、experiment、review、test、godot-check；只支持当前 256 像素 tower_defense 实验，不伪装成通用生产系统 |
| 环境 | `scripts/doctor.py` 及云端实跑 JSON；Windows 状态尚未核实 |
| 风格 | `profiles/tower_defense.yaml` 已版本化；状态 `experimental_unapproved` |
| 结构 | `workflows/blender/structure_probe.py` 生成真实 Armature/锚点、4 诊断关键姿势、双视角和引导通道 |
| A 生成记录 | `reports/generation-*.json` 保存提示词、输入/输出和已知限制；当前没有可执行的 ComfyUI 生产图 |
| B/C 部件实验 | `scripts/parts_experiment.py`、`templates/rig/parts-layout.json`；同一图集和两类驱动比较 |
| 导出 | `exports/parts_experiment/`：组合帧、body/weapon/front_hand 层、sheet 和 animation.json |
| 验证 | `reports/structure/qa.json`、`reports/parts-experiment.json`；覆盖范围必须随报告说明 |
| 引擎 | `workflows/godot/` 读取真实导出 PNG 和 JSON；已用 Xorg dummy + llvmpipe 渲染，真实 viewport 图见 `previews/parts_experiment/godot-actual-size.png` |

图像生成服务若不暴露底层版本与 seed，记录 `not_exposed`/`null`，只承诺保存现有源文件可重复合成，不承诺重新请求可产生逐像素相同原画。

## 坐标、握持和遮挡契约

世界坐标：+X 为右、−Y 为前、+Z 为上；像素坐标：左上原点、x 向右、y 向下。最终画布 256×256，`CharacterRoot`/`FootAnchor` 目标像素为 `[128,232]`。Blender 投影到画布后使用恒定偏移，禁止逐帧自动 fit-to-box，因为它会隐藏比例和脚底漂移。

名称契约保存在 `templates/rig/structure-coordinate-contract.json`：

- `CharacterRoot`：全角色的稳定根，不跟随单帧包围盒移动。
- `Skeleton / 2D Rig`：驱动层；同一动作可绑定不同已确认部件，但比例映射须验证。
- `LeftHandAnchor`、`RightHandAnchor`：解剖学左右手，不随画面镜像偷偷互换。
- `WeaponSocket`：持武器手的挂点。`WeaponGripOffset`：武器局部握柄位置相对于挂点的偏移与朝向。
- `FootAnchor`：脚底基准。它的数字稳定不能代替脚掌像素实际接地检查。
- `DrawOrder / Occlusion`：全局深度和局部交织遮挡分别处理。

武器世界变换概念为 `HandTransform × GripCorrection × inverse(WeaponLocalGripTransform)`。独立检查应把武器图像中的实际握点经最终仿射变换后投到像素空间，再与手挂点比较；不能仅令两个报告字段相等就认为测到了误差。

手部建议至少具有 `rear_palm → shaft → front_fingers` 的局部分层，护腕和衣袖单独承接。当前实验的 `body → weapon → front_hand` 三层仅验证分层重组，尚未表达所有手指交织。相机深度可帮助远近排序，但一个整体深度值不能解决武器穿过手掌或跨躯干的遮挡。

## 版本、元数据和可复现性

每次生成/构建应记录：

| 字段 | 用途 |
|---|---|
| `schema_version`、profile id/version/hash | 防止配置结构变化被静默误读 |
| character/weapon id、asset version、源文件 SHA-256 | 确认使用哪个设计、哪次修订 |
| tool version、脚本 hash | 区分变换实现变化与美术内容变化 |
| workflow、model id/hash、seed、参数 | 推理可追溯；未暴露字段明确为空 |
| reference hash、parents/dependencies | 确认参考和衍生关系 |
| direction、action、frame dimensions、duration | 避免导出与播放解释不同 |
| root、foot、hand、grip、pivot、draw order | 支持引擎重组和自动检查 |
| technical / AI visual / human review | 不混淆三类验收 |

当前生成日志与结构清单已保存部分这些信息；将目标元数据表列出，不代表所有适配器均已实现。未来接入 ComfyUI 时，应保存 API 格式工作流及自定义节点版本，清理凭据后归档。禁止把用户密钥写入配置、日志或图像元数据。

## 增量构建边界

采用文件哈希组成依赖 DAG。缓存键应由**实际相关输入**计算：

```text
profile ──┬─ approved character view/parts ── motion/mapping ── body frames
          └─ weapon source + grip ────────── motion/mapping ── weapon frames
body frames + weapon frames + local occlusion/hand variant ── composite
composite + timing/export settings ── sheet/JSON/preview/Godot validation
```

修改 hammer B 的外观，理论上只失效 hammer B 图层及其组合/预览，不能无理由重新生成角色原画。若柄径、重量或遮挡改变，则与它相关的手型/动作补帧是合理依赖，不能为追求复用跳过必要重绘。

当前角色部件仍来自同一图集，两个武器已分别提取为 `assets/weapons/hammer_a.png`、`hammer_b.png` 可独立修改。CLI 已按 route/weapon clip 的输入 hash 与输出 hash 决定复用，状态写入 `reports/build-state.json`；B 的依赖不含 Blender 投影，C 则包含投影文件。单独修改 hammer B 应只触发 B/C 的 hammer B clip。

这仍是 clip 级缓存：重新渲染受影响 clip 时也会重新计算其身体层，不能声称已经实现单独 body-frame 节点的细粒度 DAG；原始图集修改也会使相关 clip 失效。`body_cache_key` 字段本身不能证明避免了身体计算。正式管线再把确认后的各部件和驱动节点拆开，保持本节 DAG 的依赖关系，而不是现在扩张复杂系统。

缓存命中必须同时确认依赖 hash、输出文件存在及输出 hash；输入未变但输出缺失/损坏不能跳过。写入新产物应使用临时文件和完成标记，避免失败任务留下半成品被当作有效缓存。真实缓存测试应比较第二次运行的执行节点、产物 hash 和时间戳，并验证修改一把武器后的失效集合。

## 阶段门和审批

建议状态：`candidate → ai_reviewed → human_approved`，另有 `rejected`。审批记录应绑定确切资产 hash、profile version、方向和 reviewer/date/comments。资产或风格变化会使旧审批失效。当前 `approval.static_art=pending`、`production_animation_enabled=false`，不能由脚本根据技术检查自动改成 true。

本次允许的小规模压力测试不代表放开正式生产：front_left 单动作、4 关键姿势的诊断用来发现路线风险。另一方向、待机/防御完整生产，以及批量角色扩展，仍在静态样板确认之后。

## 验证接口与失败策略

技术检查应返回机器可读问题列表：`check_id`、严重程度、clip/frame、observed/expected 和相关文件。检查失败必须保留非零退出码；警告与未执行项单列，不把零条检查或未发现文件当作通过。

核心回归场景是实际风险：删除一帧、破坏 Alpha、修改 duration、移动握点、把部件移出画布、改变脚底像素或损坏分层重组，检查必须失败。只检测文件存在或只核对自己写入的数值不够。轮廓/颜色/面积变化可定位可疑帧，但不能直接判定美术好坏。

Godot 验证读取实际导出，检查帧数、时序、96 像素显示、透明边缘和背景适配。headless dummy renderer 成功只证明加载/逻辑；只有实际渲染后采集的 viewport 图才能标为 Godot 截图。预览 WebP 循环便于审查，不意味着游戏内攻击动作也必须循环。

## 后续扩展边界

暗黑国风和 2.5D 宠物先新增独立 profile、风格样板和视角规则，共用导出、哈希、QA、Godot 接口。不要假定本战士的头身比例、阴影等级、关节或动画节奏可直接迁移。只有某条路线在本次样板上获得证据后，才封装对应稳定适配器；未验证工具接口不写成“已支持”。
