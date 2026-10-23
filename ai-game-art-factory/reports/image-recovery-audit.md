# 既有图片恢复审计

审计时间（UTC）：2026-10-23T09:47:03.857674+00:00

本审计没有重新生成、转换或修改任何图片。逐文件读取字节、计算SHA-256，并用Pillow验证文件结构与逐帧解码。

## 汇总

- 本任务文件：342份，其中图像工具原始文件4份、项目内338份。去重后276个SHA-256。
- 原仓库预存图：22份，单列，不算本任务生成。
- 共364份图片全部解码成功，共解码415帧；损坏文件0份。
- 四份生成记录的输出与引用文件均真实存在；没有已知结果仅存在于工具返回值中。
- 可访问的/tmp目录中未发现图片；/tmp/codex-daemon-1000权限拒绝，未检查，不能作全目录不存在图片的断言。

## 图像工具原始结果与项目副本

| 原始真实路径 | 字节 | 尺寸 | 项目内字节相同副本 |
|---|---:|---|---|
| `/workspace/generated_images/exec-53b844e8-4cc3-4884-a2bc-c453c19dad83.png` | 1505754 | 1254×1254 | `/workspace/my_pic/ai-game-art-factory/assets/characters/warrior-parts-v001.png` |
| `/workspace/generated_images/exec-8adf1967-3d2b-42d0-b0d8-a4b6623bfd95.png` | 1752163 | 1536×1024 | `/workspace/my_pic/ai-game-art-factory/assets/references/warrior-concept-v001.png` |
| `/workspace/generated_images/exec-900c8469-9b09-405a-bc3d-af9c457e9f99.png` | 1469829 | 2169×725 | `/workspace/my_pic/ai-game-art-factory/assets/characters/route_a/joint-keyposes-v001.png` |
| `/workspace/generated_images/exec-c62dfd82-b54e-4010-bcd5-f737288c1721.png` | 1757660 | 1536×1024 | `/workspace/my_pic/ai-game-art-factory/assets/references/warrior-concept-v002.png` |

## 全量文件明细

| 实际路径 | 位置分类 | 字节 | 尺寸 | 模式 | 帧数 | 解码 |
|---|---|---:|---|---|---:|---|
| `/workspace/generated_images/exec-53b844e8-4cc3-4884-a2bc-c453c19dad83.png` | image_tool_original | 1505754 | 1254×1254 | RGBA | 1 | passed |
| `/workspace/generated_images/exec-8adf1967-3d2b-42d0-b0d8-a4b6623bfd95.png` | image_tool_original | 1752163 | 1536×1024 | RGB | 1 | passed |
| `/workspace/generated_images/exec-900c8469-9b09-405a-bc3d-af9c457e9f99.png` | image_tool_original | 1469829 | 2169×725 | RGBA | 1 | passed |
| `/workspace/generated_images/exec-c62dfd82-b54e-4010-bcd5-f737288c1721.png` | image_tool_original | 1757660 | 1536×1024 | RGB | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/assets/characters/route_a/joint-keyposes-v001.png` | project / assets | 1469829 | 2169×725 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/assets/characters/warrior-parts-v001.png` | project / assets | 1505754 | 1254×1254 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/assets/references/warrior-concept-v001.png` | project / assets | 1752163 | 1536×1024 | RGB | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/assets/references/warrior-concept-v002.png` | project / assets | 1757660 | 1536×1024 | RGB | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/assets/weapons/hammer_a.png` | project / assets | 81867 | 313×348 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/assets/weapons/hammer_b.png` | project / assets | 90286 | 287×342 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_000.png` | project / exports | 38360 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_000_body.png` | project / exports | 34067 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_000_front_hand.png` | project / exports | 943 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_000_weapon.png` | project / exports | 6920 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_001.png` | project / exports | 36926 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_001_body.png` | project / exports | 33535 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_001_front_hand.png` | project / exports | 956 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_001_weapon.png` | project / exports | 6131 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_002.png` | project / exports | 35880 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_002_body.png` | project / exports | 33153 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_002_front_hand.png` | project / exports | 956 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_002_weapon.png` | project / exports | 5803 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_003.png` | project / exports | 36267 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_003_body.png` | project / exports | 33212 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_003_front_hand.png` | project / exports | 949 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_003_weapon.png` | project / exports | 5891 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_004.png` | project / exports | 38531 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_004_body.png` | project / exports | 34109 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_004_front_hand.png` | project / exports | 956 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_004_weapon.png` | project / exports | 6124 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_005.png` | project / exports | 32687 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_005_body.png` | project / exports | 32252 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_005_front_hand.png` | project / exports | 945 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_005_weapon.png` | project / exports | 4102 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_006.png` | project / exports | 32660 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_006_body.png` | project / exports | 31599 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_006_front_hand.png` | project / exports | 961 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_006_weapon.png` | project / exports | 3606 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_007.png` | project / exports | 34517 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_007_body.png` | project / exports | 31401 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_007_front_hand.png` | project / exports | 973 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_007_weapon.png` | project / exports | 4628 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_008.png` | project / exports | 37044 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_008_body.png` | project / exports | 31034 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_008_front_hand.png` | project / exports | 961 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_008_weapon.png` | project / exports | 7233 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_009.png` | project / exports | 33717 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_009_body.png` | project / exports | 31522 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_009_front_hand.png` | project / exports | 963 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_009_weapon.png` | project / exports | 3521 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_010.png` | project / exports | 31933 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_010_body.png` | project / exports | 31875 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_010_front_hand.png` | project / exports | 940 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_010_weapon.png` | project / exports | 2336 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_011.png` | project / exports | 32444 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_011_body.png` | project / exports | 32334 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_011_front_hand.png` | project / exports | 969 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_011_weapon.png` | project / exports | 3583 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_012.png` | project / exports | 36243 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_012_body.png` | project / exports | 33579 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_012_front_hand.png` | project / exports | 959 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/attack_012_weapon.png` | project / exports | 6923 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_a/sheet.png` | project / exports | 218833 | 3328×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_000.png` | project / exports | 39008 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_000_body.png` | project / exports | 34067 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_000_front_hand.png` | project / exports | 943 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_000_weapon.png` | project / exports | 7492 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_001.png` | project / exports | 37699 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_001_body.png` | project / exports | 33535 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_001_front_hand.png` | project / exports | 956 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_001_weapon.png` | project / exports | 6652 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_002.png` | project / exports | 36556 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_002_body.png` | project / exports | 33153 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_002_front_hand.png` | project / exports | 956 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_002_weapon.png` | project / exports | 6349 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_003.png` | project / exports | 36875 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_003_body.png` | project / exports | 33212 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_003_front_hand.png` | project / exports | 949 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_003_weapon.png` | project / exports | 6318 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_004.png` | project / exports | 39111 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_004_body.png` | project / exports | 34109 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_004_front_hand.png` | project / exports | 956 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_004_weapon.png` | project / exports | 6508 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_005.png` | project / exports | 32743 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_005_body.png` | project / exports | 32252 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_005_front_hand.png` | project / exports | 945 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_005_weapon.png` | project / exports | 4382 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_006.png` | project / exports | 32794 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_006_body.png` | project / exports | 31599 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_006_front_hand.png` | project / exports | 961 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_006_weapon.png` | project / exports | 3812 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_007.png` | project / exports | 34780 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_007_body.png` | project / exports | 31401 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_007_front_hand.png` | project / exports | 973 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_007_weapon.png` | project / exports | 4916 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_008.png` | project / exports | 37422 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_008_body.png` | project / exports | 31034 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_008_front_hand.png` | project / exports | 961 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_008_weapon.png` | project / exports | 7716 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_009.png` | project / exports | 33948 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_009_body.png` | project / exports | 31522 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_009_front_hand.png` | project / exports | 963 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_009_weapon.png` | project / exports | 3796 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_010.png` | project / exports | 31980 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_010_body.png` | project / exports | 31875 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_010_front_hand.png` | project / exports | 940 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_010_weapon.png` | project / exports | 2392 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_011.png` | project / exports | 32437 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_011_body.png` | project / exports | 32334 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_011_front_hand.png` | project / exports | 969 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_011_weapon.png` | project / exports | 3756 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_012.png` | project / exports | 36886 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_012_body.png` | project / exports | 33579 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_012_front_hand.png` | project / exports | 959 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/attack_012_weapon.png` | project / exports | 7483 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/B_hammer_b/sheet.png` | project / exports | 222804 | 3328×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_000.png` | project / exports | 32721 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_000_body.png` | project / exports | 30457 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_000_front_hand.png` | project / exports | 938 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_000_weapon.png` | project / exports | 6336 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_001.png` | project / exports | 31816 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_001_body.png` | project / exports | 29990 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_001_front_hand.png` | project / exports | 958 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_001_weapon.png` | project / exports | 5627 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_002.png` | project / exports | 31203 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_002_body.png` | project / exports | 29683 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_002_front_hand.png` | project / exports | 957 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_002_weapon.png` | project / exports | 5673 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_003.png` | project / exports | 32902 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_003_body.png` | project / exports | 29782 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_003_front_hand.png` | project / exports | 942 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_003_weapon.png` | project / exports | 5819 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_004.png` | project / exports | 34818 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_004_body.png` | project / exports | 30082 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_004_front_hand.png` | project / exports | 936 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_004_weapon.png` | project / exports | 6108 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_005.png` | project / exports | 31297 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_005_body.png` | project / exports | 30045 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_005_front_hand.png` | project / exports | 963 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_005_weapon.png` | project / exports | 2286 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_006.png` | project / exports | 30652 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_006_body.png` | project / exports | 30113 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_006_front_hand.png` | project / exports | 914 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_006_weapon.png` | project / exports | 843 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_007.png` | project / exports | 32546 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_007_body.png` | project / exports | 30667 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_007_front_hand.png` | project / exports | 958 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_007_weapon.png` | project / exports | 2483 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_008.png` | project / exports | 36850 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_008_body.png` | project / exports | 31397 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_008_front_hand.png` | project / exports | 961 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_008_weapon.png` | project / exports | 6388 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_009.png` | project / exports | 34381 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_009_body.png` | project / exports | 31283 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_009_front_hand.png` | project / exports | 962 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_009_weapon.png` | project / exports | 3664 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_010.png` | project / exports | 33275 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_010_body.png` | project / exports | 31138 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_010_front_hand.png` | project / exports | 968 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_010_weapon.png` | project / exports | 2724 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_011.png` | project / exports | 33574 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_011_body.png` | project / exports | 31002 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_011_front_hand.png` | project / exports | 923 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_011_weapon.png` | project / exports | 3695 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_012.png` | project / exports | 35394 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_012_body.png` | project / exports | 30897 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_012_front_hand.png` | project / exports | 964 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/attack_012_weapon.png` | project / exports | 6403 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_a/sheet.png` | project / exports | 144080 | 3328×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_000.png` | project / exports | 33307 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_000_body.png` | project / exports | 30457 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_000_front_hand.png` | project / exports | 938 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_000_weapon.png` | project / exports | 6887 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_001.png` | project / exports | 32492 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_001_body.png` | project / exports | 29990 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_001_front_hand.png` | project / exports | 958 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_001_weapon.png` | project / exports | 6249 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_002.png` | project / exports | 31784 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_002_body.png` | project / exports | 29683 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_002_front_hand.png` | project / exports | 957 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_002_weapon.png` | project / exports | 6196 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_003.png` | project / exports | 33191 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_003_body.png` | project / exports | 29782 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_003_front_hand.png` | project / exports | 942 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_003_weapon.png` | project / exports | 6195 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_004.png` | project / exports | 35161 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_004_body.png` | project / exports | 30082 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_004_front_hand.png` | project / exports | 936 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_004_weapon.png` | project / exports | 6424 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_005.png` | project / exports | 31439 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_005_body.png` | project / exports | 30045 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_005_front_hand.png` | project / exports | 963 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_005_weapon.png` | project / exports | 2417 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_006.png` | project / exports | 30680 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_006_body.png` | project / exports | 30113 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_006_front_hand.png` | project / exports | 914 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_006_weapon.png` | project / exports | 853 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_007.png` | project / exports | 32631 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_007_body.png` | project / exports | 30667 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_007_front_hand.png` | project / exports | 958 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_007_weapon.png` | project / exports | 2619 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_008.png` | project / exports | 37259 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_008_body.png` | project / exports | 31397 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_008_front_hand.png` | project / exports | 961 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_008_weapon.png` | project / exports | 6753 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_009.png` | project / exports | 34679 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_009_body.png` | project / exports | 31283 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_009_front_hand.png` | project / exports | 962 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_009_weapon.png` | project / exports | 3928 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_010.png` | project / exports | 33505 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_010_body.png` | project / exports | 31138 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_010_front_hand.png` | project / exports | 968 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_010_weapon.png` | project / exports | 2964 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_011.png` | project / exports | 33784 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_011_body.png` | project / exports | 31002 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_011_front_hand.png` | project / exports | 923 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_011_weapon.png` | project / exports | 3938 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_012.png` | project / exports | 35878 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_012_body.png` | project / exports | 30897 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_012_front_hand.png` | project / exports | 964 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/attack_012_weapon.png` | project / exports | 6851 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/C_hammer_b/sheet.png` | project / exports | 147498 | 3328×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/parts/cape.png` | project / exports | 72337 | 280×279 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/parts/hammer_a.png` | project / exports | 81867 | 313×348 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/parts/hammer_b.png` | project / exports | 90286 | 287×342 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/parts/head.png` | project / exports | 115533 | 269×291 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/parts/left_forearm.png` | project / exports | 68408 | 311×290 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/parts/left_hand.png` | project / exports | 55504 | 271×252 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/parts/left_shin_boot.png` | project / exports | 94270 | 314×382 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/parts/left_thigh.png` | project / exports | 81349 | 313×252 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/parts/left_upper_arm.png` | project / exports | 102650 | 314×294 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/parts/pelvis.png` | project / exports | 127842 | 308×277 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/parts/right_forearm.png` | project / exports | 67038 | 271×294 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/parts/right_hand.png` | project / exports | 55999 | 313×252 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/parts/right_shin_boot.png` | project / exports | 94359 | 313×381 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/parts/right_thigh.png` | project / exports | 79821 | 297×252 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/parts/right_upper_arm.png` | project / exports | 85336 | 305×293 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/parts_experiment/parts/torso.png` | project / exports | 174513 | 330×309 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/route_a/key_00.png` | project / exports | 43874 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/route_a/key_01.png` | project / exports | 44478 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/route_a/key_02.png` | project / exports | 45791 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/route_a/key_03.png` | project / exports | 41781 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/exports/route_a/sheet.png` | project / exports | 174079 | 1024×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/parts_experiment/B_hammer_a-contact.png` | project / previews | 77814 | 1024×296 | RGB | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/parts_experiment/B_hammer_a.webp` | project / previews | 327418 | 256×256 | RGBA | 13 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/parts_experiment/B_hammer_b-contact.png` | project / previews | 79212 | 1024×296 | RGB | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/parts_experiment/B_hammer_b.webp` | project / previews | 332302 | 256×256 | RGBA | 13 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/parts_experiment/C_hammer_a-contact.png` | project / previews | 65687 | 1024×296 | RGB | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/parts_experiment/C_hammer_a.webp` | project / previews | 269194 | 256×256 | RGBA | 13 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/parts_experiment/C_hammer_b-contact.png` | project / previews | 66736 | 1024×296 | RGB | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/parts_experiment/C_hammer_b.webp` | project / previews | 272648 | 256×256 | RGBA | 13 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/parts_experiment/actual-size-comparison.png` | project / previews | 106435 | 900×610 | RGB | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/parts_experiment/before-layout-contact.png` | project / previews | 74752 | 1024×296 | RGB | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/parts_experiment/before-layout.png` | project / previews | 102585 | 900×610 | RGB | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/parts_experiment/godot-actual-size.png` | project / previews | 128501 | 1024×720 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/route-comparison.png` | project / previews | 370571 | 1200×1110 | RGB | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/route_a/contact-sheet.png` | project / previews | 146340 | 1056×380 | RGB | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/route_a/diagnostic-keyposes.apng` | project / previews | 173992 | 256×256 | RGBA | 4 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/static-review.png` | project / previews | 654564 | 1160×820 | RGB | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/contact-sheet.png` | project / previews | 125743 | 1080×1240 | RGB | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_block/attack_00_depth.png` | project / previews | 36349 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_block/attack_00_flat.png` | project / previews | 41572 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_block/attack_00_normal.png` | project / previews | 49971 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_block/attack_00_pose.png` | project / previews | 2861 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_block/attack_00_silhouette.png` | project / previews | 31294 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_block/attack_01_depth.png` | project / previews | 38424 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_block/attack_01_flat.png` | project / previews | 43230 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_block/attack_01_normal.png` | project / previews | 52107 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_block/attack_01_pose.png` | project / previews | 3235 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_block/attack_01_silhouette.png` | project / previews | 31949 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_block/attack_02_depth.png` | project / previews | 36943 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_block/attack_02_flat.png` | project / previews | 41710 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_block/attack_02_normal.png` | project / previews | 51158 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_block/attack_02_pose.png` | project / previews | 3073 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_block/attack_02_silhouette.png` | project / previews | 31322 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_block/attack_03_depth.png` | project / previews | 36709 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_block/attack_03_flat.png` | project / previews | 41780 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_block/attack_03_normal.png` | project / previews | 50390 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_block/attack_03_pose.png` | project / previews | 2891 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_block/attack_03_silhouette.png` | project / previews | 31423 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_crescent/attack_00_depth.png` | project / previews | 36417 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_crescent/attack_00_flat.png` | project / previews | 41525 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_crescent/attack_00_normal.png` | project / previews | 50529 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_crescent/attack_00_pose.png` | project / previews | 2861 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_crescent/attack_00_silhouette.png` | project / previews | 31351 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_crescent/attack_01_depth.png` | project / previews | 38190 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_crescent/attack_01_flat.png` | project / previews | 43110 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_crescent/attack_01_normal.png` | project / previews | 52708 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_crescent/attack_01_pose.png` | project / previews | 3235 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_crescent/attack_01_silhouette.png` | project / previews | 32003 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_crescent/attack_02_depth.png` | project / previews | 36866 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_crescent/attack_02_flat.png` | project / previews | 41450 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_crescent/attack_02_normal.png` | project / previews | 51504 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_crescent/attack_02_pose.png` | project / previews | 3073 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_crescent/attack_02_silhouette.png` | project / previews | 31279 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_crescent/attack_03_depth.png` | project / previews | 36693 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_crescent/attack_03_flat.png` | project / previews | 41589 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_crescent/attack_03_normal.png` | project / previews | 50871 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_crescent/attack_03_pose.png` | project / previews | 2891 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_left/hammer_crescent/attack_03_silhouette.png` | project / previews | 31368 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_block/attack_00_depth.png` | project / previews | 36064 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_block/attack_00_flat.png` | project / previews | 41155 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_block/attack_00_normal.png` | project / previews | 48592 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_block/attack_00_pose.png` | project / previews | 2743 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_block/attack_00_silhouette.png` | project / previews | 30811 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_block/attack_01_depth.png` | project / previews | 37782 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_block/attack_01_flat.png` | project / previews | 42686 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_block/attack_01_normal.png` | project / previews | 51236 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_block/attack_01_pose.png` | project / previews | 2915 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_block/attack_01_silhouette.png` | project / previews | 31843 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_block/attack_02_depth.png` | project / previews | 36297 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_block/attack_02_flat.png` | project / previews | 40676 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_block/attack_02_normal.png` | project / previews | 48201 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_block/attack_02_pose.png` | project / previews | 2909 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_block/attack_02_silhouette.png` | project / previews | 30592 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_block/attack_03_depth.png` | project / previews | 36140 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_block/attack_03_flat.png` | project / previews | 41071 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_block/attack_03_normal.png` | project / previews | 48058 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_block/attack_03_pose.png` | project / previews | 2834 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_block/attack_03_silhouette.png` | project / previews | 31033 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_crescent/attack_00_depth.png` | project / previews | 36069 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_crescent/attack_00_flat.png` | project / previews | 41036 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_crescent/attack_00_normal.png` | project / previews | 49387 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_crescent/attack_00_pose.png` | project / previews | 2743 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_crescent/attack_00_silhouette.png` | project / previews | 30849 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_crescent/attack_01_depth.png` | project / previews | 37733 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_crescent/attack_01_flat.png` | project / previews | 42566 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_crescent/attack_01_normal.png` | project / previews | 51824 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_crescent/attack_01_pose.png` | project / previews | 2915 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_crescent/attack_01_silhouette.png` | project / previews | 31727 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_crescent/attack_02_depth.png` | project / previews | 36176 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_crescent/attack_02_flat.png` | project / previews | 40586 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_crescent/attack_02_normal.png` | project / previews | 48970 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_crescent/attack_02_pose.png` | project / previews | 2909 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_crescent/attack_02_silhouette.png` | project / previews | 30780 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_crescent/attack_03_depth.png` | project / previews | 36174 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_crescent/attack_03_flat.png` | project / previews | 41149 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_crescent/attack_03_normal.png` | project / previews | 49174 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_crescent/attack_03_pose.png` | project / previews | 2834 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/front_right/hammer_crescent/attack_03_silhouette.png` | project / previews | 31081 | 256×256 | RGBA | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/guide-channels.png` | project / previews | 94461 | 1360×650 | RGB | 1 | passed |
| `/workspace/my_pic/ai-game-art-factory/previews/structure/route-a-guide-strip.png` | project / previews | 25941 | 1024×256 | RGBA | 1 | passed |
| `/workspace/my_pic/webp/OBOKOZU.jpg` | preexisting_repository | 11654 | 200×300 | RGB | 1 | passed |
| `/workspace/my_pic/webp/hanime.jpg` | preexisting_repository | 49057 | 268×394 | P | 1 | passed |
| `/workspace/my_pic/webp/jabletv-apk.png` | preexisting_repository | 9918 | 250×250 | RGBA | 1 | passed |
| `/workspace/my_pic/webp/pp.png` | preexisting_repository | 8711 | 832×798 | RGBA | 1 | passed |
| `/workspace/my_pic/webp/三上悠亜.jpg` | preexisting_repository | 249810 | 1200×1600 | RGB | 1 | passed |
| `/workspace/my_pic/webp/伊藤舞雪.jpg` | preexisting_repository | 534974 | 1128×1504 | RGB | 1 | passed |
| `/workspace/my_pic/webp/安齋拉拉.webp` | preexisting_repository | 57042 | 853×1280 | RGB | 1 | passed |
| `/workspace/my_pic/webp/明日花綺羅.webp` | preexisting_repository | 220524 | 1080×1350 | RGB | 1 | passed |
| `/workspace/my_pic/webp/桃乃木香奈.webp` | preexisting_repository | 97556 | 1080×1620 | RGB | 1 | passed |
| `/workspace/my_pic/webp/桥本有菜.webp` | preexisting_repository | 72368 | 1080×1536 | RGB | 1 | passed |
| `/workspace/my_pic/webp/楓可憐.webp` | preexisting_repository | 64906 | 961×1408 | RGB | 1 | passed |
| `/workspace/my_pic/webp/楪可憐.jpg` | preexisting_repository | 41253 | 499×747 | RGB | 1 | passed |
| `/workspace/my_pic/webp/樞木葵.jfif` | preexisting_repository | 1302551 | 2880×3840 | RGB | 1 | passed |
| `/workspace/my_pic/webp/櫻空桃.webp` | preexisting_repository | 135908 | 1080×1440 | RGB | 1 | passed |
| `/workspace/my_pic/webp/河北彩花.jfif` | preexisting_repository | 315936 | 1364×2046 | RGB | 1 | passed |
| `/workspace/my_pic/webp/河合明日菜.webp` | preexisting_repository | 60336 | 1080×1620 | RGB | 1 | passed |
| `/workspace/my_pic/webp/涼森玲夢.webp` | preexisting_repository | 135220 | 1080×1667 | RGB | 1 | passed |
| `/workspace/my_pic/webp/深田詠美.webp` | preexisting_repository | 130716 | 874×1240 | RGB | 1 | passed |
| `/workspace/my_pic/webp/神宫寺奈绪.webp` | preexisting_repository | 54936 | 768×1024 | RGB | 1 | passed |
| `/workspace/my_pic/webp/葵.webp` | preexisting_repository | 117252 | 1080×1622 | RGB | 1 | passed |
| `/workspace/my_pic/webp/鈴村愛里.webp` | preexisting_repository | 130676 | 1080×1618 | RGB | 1 | passed |
| `/workspace/my_pic/webp/高橋聖子.webp` | preexisting_repository | 44766 | 1080×1620 | RGB | 1 | passed |

完整SHA-256、真实路径和扫描限制见同目录 `image-recovery-audit.json`。Git归档与推送不属于此只读审计的执行范围。
