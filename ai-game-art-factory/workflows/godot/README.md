# Godot 最小对比场景（美术未验收）

用 Godot 4 打开此目录 `project.godot`，运行场景。场景直接加载项目根目录 `exports/parts_experiment/` 的四条序列，按 JSON 中每帧 duration_ms 播放，每组显示 96×96 和 256×256 像素。攻击序列末端暂停后重播，暂不是无缝循环动画。

```powershell
godot --path workflows/godot -- --capture
```

从项目根目录运行，`--capture` 在真实图形窗口渲染后保存 `previews/parts_experiment/godot-actual-size.png`，然后退出。普通运行去掉 `-- --capture`。若命令不在 PATH，使用本机 Godot 可执行文件完整路径。

无窗口验证：

```sh
godot --headless --path workflows/godot --quit-after 10
```

必须看到 `ART_FACTORY_SCENE_READY clips=4 frames=52 dimensions=256x256; art=UNAPPROVED`；单凭 Godot 退出码 0 不足以证明脚本解析成功。Headless 默认 dummy 渲染器，本检查不生成游戏截图。

本云环境实测使用已有 Xorg dummy 驱动和 Mesa llvmpipe，无软件安装：

```sh
Xorg :99 -config /etc/X11/xorg.conf -logfile /tmp/art-factory-xorg.log -noreset -nolisten tcp
DISPLAY=:99 XDG_DATA_HOME=/tmp/art-factory-data XDG_CACHE_HOME=/tmp/art-factory-cache XDG_CONFIG_HOME=/tmp/art-factory-config godot --path workflows/godot --rendering-method gl_compatibility --audio-driver Dummy -- --capture
```

第一条须在独立会话运行；若 `:99` 已占用，不重复启动，也不要停止不是本任务启动的服务。第二条日志实际报告 Godot 4.6.3 / OpenGL 4.5 / Mesa llvmpipe，并成功保存 1024×720 viewport PNG。`XDG_DATA_HOME` 等指定可写目录，避免当前云容器默认用户目录不可写导致崩溃。这些 Linux 参数不是 Windows 的安装说明。

实际截图只证明导出序列在 Godot 内显示。画面仍存在接缝、肢体变形和持握遮挡问题，未通过美术验收。当前不是 Godot Skeleton2D 骨骼工程，而是渲染后的分层序列回放；骨骼动画由 Python 实验生成。
