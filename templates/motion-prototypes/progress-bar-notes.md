# Section progress bar: notes

## Layout used in previews
The original frame is scaled to 94.07% (1806x1016) and placed at (57,64). The top 64px band holds the bar on the
same paper colour (#FAFAF5), so there is no seam. Overlaying on the full-size frame does not work cleanly: the hook
title "Google 新论文" (y≈30) and the source tag (y≈30–60) both sit in the top 64px. After scaling, the source
tag lands at y≈95–120 and the ①②③④ chips at y≈150–195, both clear of the bar.

## Component: progress-bar.html
- `progress-bar.html?variant=1|2|3`. You can also set `window.BAR_CONFIG = {sections:[{num,name,start}], total, margin, anim, teaserSec, v3Accordion}` before the script runs.
- `await window.barReady`, then call `window.seek(t, {animScale, teaser})`. The bar state is a pure function of t, with no CSS transitions or timers.
  - `animScale`: stretches the transition and teaser windows. Set it to the playback rate when you preview a sped-up timeline (the previews use 17.32).
  - `teaser`: turns the "下一节" teaser on or off for the last `teaserSec` seconds of a section (default 2s).
- Section change: 0.42s easeOutBack, with slight overshoot.
- Size: 1920x64. Screenshot `#bar` for each frame (see render_bar.py).

## Variants
- V1 分段胶囊条: segment widths follow section duration, with 6px gaps. Finished segments are solid #D4552A. The current segment fills up to a glowing head. An ink pill ("05" in Inter + name at 26px bold) follows the head. On a section change its width morphs with overshoot and the old label hands off to the new one. Teaser: a ghost label "下一节 05 走一遍例子 →" appears beside the pill, and the next segment warms.
- V2 章节标签条: 8 labels in equal cells (Inter 20px numbers, 26px names). An ink pill slides between labels as a magic move: the leading edge moves first and the trailing edge follows. A white copy of the labels is clipped to the pill, so the text inverts exactly where the pill passes over it. A 2px hairline fills continuously, mapped per cell. Teaser: a dashed outline on the next label, and that label darkens.
- V3 编辑感目录尺: a hairline ruler with Latin Modern Roman Demi numerals, in the same LaTeX face as the paper tables. Minor-tick density shows section length. The active numeral grows and turns Stanford red, and its name (Noto Serif CJK, 27px bold) unfolds to the right. A red played line and dot move continuously. The band has a faint noise texture that fades out toward the bottom. Teaser: a red ring pulses on the next major tick.
  - `v3Accordion:true` turns on the original accordion version, where the active slot widens and the rest reflow. It is off by default because on every section change the playhead jumped backwards by about 150px as the previous name collapsed.

## Render pipeline
render_bar.py renders 900 bar PNGs with Playwright (Chromium from /opt/pw-browsers). base.mp4 is built as follows:
- Part A (0–18s): the full video with setpts/17.32 and fps=30, frame-sampled with no blending.
- Part B (18–30s): 1:26–1:38 at real speed, audio loudnorm to -16 LUFS (measured -15.7).
- Both parts are scaled and padded, then concatenated.

The bar frames are overlaid on base.mp4, and drawtext adds the corner label (V#, plus 17× 快进 or 1× 原速).
