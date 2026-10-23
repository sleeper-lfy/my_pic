# 公开原生动作检查

本目录是来源明确的动作数据验证，不是持锤动作或成品角色美术验收。

## 主动作参照：MakeHuman walk1.bvh

官方MakeHuman仓库固定提交`a8bc2d54ff0ac92e78ff71431b1023eda42bf482`的随附CC0资产。原文件`assets/public_references/makehuman/walk1.bvh`，SHA-256为`e6b30b03133b5f54799e62962d3d6c2393771c15fd5a5a2be434358fc332b6bc`。

Blender实际导入14帧、75个骨骼（含由BVH偏移表达的连接骨及手指/面部链），原始帧间隔0.041667秒。`walk1-native-skeleton.json`保留每帧全部骨骼世界坐标及层级。预览只显示27根与行走直接相关的骨骼，包含肩胯连接，保证图可读；没有擅自重画关节位置。

- `previews/public_motion/walk1-native-skeleton.webp`：14帧原生骨架的前向与45°投影，583ms诊断循环。
- `previews/public_motion/walk1-native-skeleton-contact.png`：第1/5/10/14帧对照。

原生世界骨长最大变化约3.22×10⁻⁶源单位，坐标均有限。不是重定向到新的MakeHuman default骨架，更没有皮肤跟随、单手锤攻击或足底锁定通过的结论。步态中可见的起伏与跨步是源动作内容，未做逐帧包围盒归一化或改关节来美化。

## 附属传输测试：Khronos RiggedFigure

官方Khronos样例仓库固定提交`15cd02d304e54cb42a4db4eefe719f76190f4b68`，作者Cesium，©2017，CC BY4.0。原始GLB及许可、README、哈希在`assets/public_references/riggedfigure/`。

实际导入19骨、370顶点、1条原生1.25秒动作；渲染24个原生时间样本，没有重做动作或改皮肤权重。新增了诊断用黏土材质、灯光和相机，因此渲染是注明改动的派生成果。顶点权重和接近1，无未加权顶点，必需的双臂/双腿/颈部骨骼存在，世界骨长最大变化约1.21×10⁻⁷源单位。

实际查看后确认，该源模型是立方体头和极低模四肢，**排除为人体素体美术参照**。它仅证明已有公开skin/clip可被当前Blender正确导入和播放；不放入正常人体的主推荐。

- `previews/public_motion/riggedfigure-transfer-only-contact.png`：明确标记BOX SAMPLE / NOT ANATOMY REFERENCE。
- `previews/public_motion/riggedfigure-native.webp`：原生采样播放，末帧附80ms诊断停留。
- `workflows/blender/public_motion_probe.blend`：保存的原生skin/clip可检查场景。

## 复跑

项目根目录：

```sh
blender --background --factory-startup --threads 2 --python workflows/blender/public_motion_probe.py
python workflows/blender/public_motion_review.py
```

第一步约30秒CPU渲染，输出24张512×512 RGBA及原生骨架数据；第二步由已产生的数据生成接触表、WebP并逐帧解码核验。`review.json`记录28个图片/动画文件的尺寸、帧数、字节数和SHA-256。人形美术和持握验收未通过，不能由这些技术检查自动批准。
