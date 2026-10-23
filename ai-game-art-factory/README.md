# AI Game Art Factory — 持锤战士路线实验

**用户已否决上一轮人形结果。当前转为公开素体与原生骨架基线，旧二维关节点插值不再作为默认路线。**

失败原因见 [人形结构审计](docs/failed-human-form-audit.md)。新入口为 `python scripts/factory.py reference-baseline`，保留公开素材原始比例、真实骨骼层级和蒙皮；资源来源和许可记录在 `assets/public_references/`。旧 `structure` / `experiment` 默认阻止执行，只有明确 `--legacy-diagnostic` 才能重现历史失败。

先看 [静态样板](previews/static-review.png)、[A/B/C 对照](previews/route-comparison.png) 与 [Godot 实际截图](previews/parts_experiment/godot-actual-size.png)。三条路线都有真实实验产物，同时保留失败证据；没有以简单几何体或技术通过代替成品质量。

- [使用说明](docs/使用说明.md)
- [持锤战士验证报告](docs/持锤战士验证报告.md)
- [技术路线对比](docs/技术路线对比报告.md)
- [流水线架构](docs/AI美术流水线架构.md)
- [美术风格规范](docs/美术风格规范.md)
- [环境调查](docs/环境调查.md)

项目根目录运行 `python scripts/factory.py --help`。原有仓库内容不属于此实验资产。此目录不包含第三方游戏素材、下载的模型权重或未授权的 Spine 运行库；生成记录、输入引用及资产哈希位于 `reports/`。图像服务未提供可固定的模型版本和种子，该限制已记录。
