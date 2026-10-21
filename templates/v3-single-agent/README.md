# v3 单 agent 模板（Harness² v3.1）——待补

这个目录对应 SKILL.md 里的 `templates/v3-single-agent/`：Harness² v3.1 的整套代码（风格卡 A「暖白讲解」）。
**首个公开版本里还没有放进来**，打包时这些文件不在本地磁盘上。待补文件：

| 文件 | 作用 |
|---|---|
| `core.js` | 镜头 / 插值 / 运动模糊（12–16 份等权采样） |
| `overlay.js` | 顶部章节进度条 V3「目录尺」+ 字幕 + 头像 |
| `main.js` | 场景调度，`window.render(t)` 纯函数入口 |
| `scene.html` | 渲染页面 |
| `build_data.py` | 从 script.txt + timeline.json 生成场景数据 |
| `dumpcues.py` | 从场景代码导出音效时间点 cues.json |
| `audio.py` | 人声 + numpy 合成背景音乐 / 音效 + ducking + loudnorm |
| `render.py` / `render_all.sh` | Playwright 逐帧渲染，8 段并行 |
| `finish.sh` | concat + 混音 + mux + faststart |
| `selfcheck.py` | 全片抽帧扫 JS 报错 |
| `occ.py` | 遮挡 / 空屏检查 |
| `b1_hook_paper_example.js` | 示例：钩子 + 钻进论文（Harness² 那一期） |
| `b4_big_canvas_example.js` | 示例：大画布运镜「走一遍例子」（Harness² 那一期） |

在补齐之前，可以直接用 `templates/v4-multi-agent/`（风格卡 ④，多 agent 按章并行），它包含渲染、音频、拼接的完整链路；
进度条组件见 `templates/motion-prototypes/progress-bar.html` + `render_bar.py`。
