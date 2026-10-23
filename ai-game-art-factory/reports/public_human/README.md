# MakeHuman 公开人体结构基线

来源为官方仓库固定 commit 下的 CC0 数据，详情见 `assets/public_references/makehuman/SOURCE.json` 与许可文件。没有安装 MakeHuman 程序，也没有引入其 AGPL 源码。

实跑路径：
```sh
blender --background --factory-startup --threads 2 --python workflows/blender/public_human_baseline.py
python workflows/blender/public_human_review.py
```

使用原始 body 面构建连续网格，保留源顶点索引；使用原生163骨、父子层级、原生权重和 Blender Armature modifier。源权重总和存在0.954–1.063范围的误差，逐顶点按比例归一化，不自动重绘蒙皮权重。只有 body 面参与渲染；helper/joint/tights/skirt/genital/eye/teeth等辅助面排除。

`previews/public_human/contact-sheet.png` 是真实渲染的多视角人体和原生骨架投影覆盖。`right-hand-readable.png` 为手部细节。`workflows/blender/public_human_baseline.blend` 可检查真实网格、163骨父子关系、vertex groups、Armature modifier与测试Action。

肘部测试是自行指定原生骨局部旋转的蒙皮诊断：33帧检查固定骨长和真实网格位移，渲染其中5个采样姿态；不是下载的动作，不是完整攻击动画。`authored-elbow-skin-test.webp` 明确为五姿态诊断播放。官方tpose/benchmark BVH是单帧姿态，当前脚本未应用这些BVH；不得据此声称其重定向已通过。骨轴roll使用原生plane的几何法线定义，未证明与MakeHuman原生BVH旋转约定完全一致。

本基线仍是正常比例的人体参照，未修改成3.5头身战士，也未做2D最终美术、握锤或战斗动作验收。
