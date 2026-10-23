# 公开人体骨架与动作资源核查

本次先核查真实公开来源和许可，再选择小文件做结构验证。没有下载大型动画包、安装软件或再次生成角色图片。检查通过当前云端的 HTTPS 正常校验执行；访问失败的站点没有绕过网络策略。

## 优先采用：MakeHuman 官方随附数据

官方项目：[makehumancommunity/makehuman](https://github.com/makehumancommunity/makehuman)。

[LICENSE.md](https://github.com/makehumancommunity/makehuman/blob/master/LICENSE.md) 明确区分：应用程序代码为 AGPL；随附图形资产为 CC0 1.0，包含 base mesh、proxies、targets、textures、clothes、poses/expressions，生成输出由使用者处理。社区另行上传的第三方素材不自动继承这个许可。完整资产许可见 [LICENSE.ASSETS.md](https://github.com/makehumancommunity/makehuman/blob/master/LICENSE.ASSETS.md)。

| 资源 | 已读取实证 | 用途与限制 |
|---|---|---|
| [default.mhskel](https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/rigs/default.mhskel) | 117,790 bytes；自身写明 `license: CC0`、version110；description 指明详细手指、脚趾与面部骨 | 与官方连续素体和原生权重一起导入，替换原先自行拼凑的人体结构 |
| [tpose.bvh](https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/poses/tpose.bvh) | 44,727 bytes；**1帧**；Frame Time0.041667；root/pelvis.R/upperleg01.R 等原生骨名 | 标准T姿态，校核骨轴、左右和重定向基准；不能称作动画 |
| [tpose.meta](https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/poses/tpose.meta) | 明确 `license CC0`，描述为 mocap/retargeting 标准T-pose | 应连同来源与许可归档 |
| [benchmark.bvh](https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/poses/benchmark.bvh) | 42,269 bytes；**1帧**；原生骨名 | 官方极端蒙皮测试姿态，验证肩、肘、腿的连续形体；不能当作持锤攻击 |
| [benchmark.meta](https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/poses/benchmark.meta) | 明确 `license CC0`；描述“test the rigging in extreme condition” | 绑定压力测试有来源依据 |
| [walk1.bvh](https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/animations/walks/walk1.bvh) | 42,516 bytes；**14帧**；Frame Time0.041667，约24fps；骨名Root/Spine1等旧命名 | 可做公开多帧动作基准，但必须建立旧骨架到新default骨架的映射、轴向和单位校验；不是持锤动作 |
| [dance1.bvh](https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/animations/walks/dance1.bvh) | 14,028 bytes；**仅1帧** | 文件名虽带dance，不能报告为完整舞蹈动画 |
| [zombieWalk1.bvh](https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/animations/zombie/zombieWalk1.bvh) | 79,657 bytes；31帧；Frame Time0.041667 | 可下载的旧多帧数据，但僵尸步态不适合正常战士基线，暂不选用 |

这些URL读取均返回HTTP200，不要求登录。旧walk文件的官方提交历史显示最后修改在2016-02；它适合作为稳定测试资料，不能宣传为近期维护的商业动作库。T姿态与benchmark的版权元数据标记2020。必须分别记录文件实际哈希和所取仓库提交，不只记录可变的master URL。

旧BVH与default.mhskel不是因为同出MakeHuman就能无条件套用。BVH存在不同rotation order、ROOT/局部平移通道及坐标约定；导入时应校核静止姿态后再处理运动。公开动作进入项目后，先查看骨架连贯性与足底接触，不能只看导入成功。

## 备选：Khronos 官方 glTF 测试角色

[RiggedFigure 官方说明](https://github.com/KhronosGroup/glTF-Sample-Assets/tree/main/Models/RiggedFigure) / [直接GLB](https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/RiggedFigure/glTF-Binary/RiggedFigure.glb)。

已读取官方README与glTF JSON：Cesium ©2017，CC BY4.0；1个mesh、19个skin joints、1条动画、57个动画通道；主体仅370个顶点，buffer22,184 bytes。时间采样范围到1.25秒。它适合验证导入、皮肤与骨骼动画基本链路，形体细节有限，不优先作为用户要求的高质量人体素体。该许可允许修改及分享，需保留作者、出处、许可链接并说明修改。下载不要求登录；未下载整个资产库。

[CesiumMan](https://github.com/KhronosGroup/glTF-Sample-Assets/tree/main/Models/CesiumMan)也是19骨动画人形，主版权CC BY4.0，但说明同时包含Cesium标志的单独商标条款，当前不优先选择。

[BrainStem](https://github.com/KhronosGroup/glTF-Sample-Assets/tree/main/Models/BrainStem)是机器人，且许可为Poser EULA，不是人体素体或明确CC0/CC-BY替代，排除。

Khronos仓库网页可访问，RiggedFigure路径显示2026年仍有元数据维护；这不代表模型或动作已达到最终游戏美术标准。

## Quaternius：授权信息存在冲突，当前不导入或公开再分发

官网和itch下载页被当前云端代理返回403。官方GitHub站点源码可正常读取，且仓库的[CNAME](https://raw.githubusercontent.com/Quaternius/quaternius.github.io/master/CNAME)明确是`quaternius.com`，所以可用于核实公开说明，而非从第三方镜像猜测许可。

- [Universal Animation Library 页面源码](https://github.com/Quaternius/quaternius.github.io/blob/master/packs/universalanimationlibrary.html)：说明120+动作、通用人形rig、FBX/GLB/Blend、兼容Godot/Unity/Unreal，页面仍写CC0及商业使用；同时区分免费部分与收费Source版本，不能假设所有120+动作和blend文件均免费。
- [当前license.html](https://github.com/Quaternius/quaternius.github.io/blob/master/license.html)：2026-08-28更新为**Quaternius Asset License v1.0**，允许产品内商业使用，但禁止原始或修改后的素材作为独立资产再次分发。

两页面当前内容不一致。没有取得特定下载包内的确切许可证前，不能仅凭旧pack页面的CC0字样把模型或动作提交到公开仓库。当前未取得下载包、未确认登录流程，也未声称资源可直接再分发。若后续使用，需要核对具体版本随附许可及取得日期，或向作者确认；不能用旧印象代替审查。

## CMU 动捕库

`https://mocap.cs.cmu.edu/`与HTTP入口在当前环境被网络策略返回403。未核对当前网页条款、具体文件和retarget骨架，所以不采用未核实的社区副本，也不把“公开可见”当成允许再分发。

## 本轮选择边界

建议用MakeHuman连续素体、原生骨架、原生权重建立正常人体基线；先做T姿态与benchmark的绑定校验，再用walk1的实际多帧骨骼做动作参照或经过验证的重定向。当前尚未取得一个许可清晰、无需账号、可直接复用的完整单手锤动作。

持锤验证应另行在正常人体骨架上设计并审查动作，明确标记“依据公开人体/骨架自行制作”，不能把walk或单帧benchmark命名成已验证的攻击动画。手指包柄、肩肘弯曲和重心必须看实际渲染，不能以骨骼数量、文件存在或零挂点误差替代人体结构验收。

## 后续实际执行结果

已固定官方提交取得RiggedFigure GLB、许可及MakeHuman walk1.bvh小文件，并执行现有Blender导入。walk1的14帧/75骨原生数据已生成可看的骨架动画和前方/45°接触表，未强行重定向。RiggedFigure的24个原生动画采样也已渲染，但目视确认是方头极低模测试人，已明确排除为人体美术参照，仅保留skin传输兼容性记录。详见`reports/public_motion/README.md`与`review.json`。整个过程未安装软件或下载大型模型/动作包。
