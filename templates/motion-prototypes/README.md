# Harness² transition prototypes: notes

Both clips: 1920x1080, 30 fps, libx264 crf 18 yuv420p, AAC 192k, +faststart. Two-pass loudnorm (I=-16, TP=-1.5, LRA=11). Measured result: A = -15.9 LUFS, peak -1.3 dBFS; B = -16.0 LUFS, peak -1.5 dBFS.
Renderer: `build/clipX.html` exposes `window.seek(t)`, `DURATION` and `CUES`. `build/render.py` screenshots every frame in headless Chromium, and `build/make.sh A|B` runs the whole pipeline (frames, video, audio, loudnorm, mux, 0.5 s sheet). Randomness comes only from seeded PRNGs: mulberry32 in JS, numpy default_rng(1) for audio.

Sources: arXiv was blocked by the proxy (403), so the paper PDF was not fetched. Every paper image is a crop from the original video's own frames:
- title block: 0:15.0
- related-work sentence (before highlight): 0:36.0
- Figure 9 (before the red box draws in): 1:35.6

The surrounding "body text" on the physical pages is greeked bars, not invented text.

## Clip A: original 0:23.00 to 0:37.95 (15.3 s incl. 0.35 s tail)
The range runs past 0:36 so the full "比如斯坦福牵头做的 Meta-Harness" sentence and its highlight fit.

| t (s) | voice | technique |
|---|---|---|
| 0–1.7 | 最后告诉你明天就能怎么用 | Starts on the H02 end state: title box left, Harness² right, chip ①. Chip ② slides out from behind chip ① (pop). |
| 1.8–2.8 | (pause) | Paper as a physical sheet. The flat title box grows into a full page: soft shadow, -2° tilt, paper-noise texture. Camera pushes in to 1.1x on the page (whoosh + paper rustle). |
| 3.3–4.1 | 先说背景 | The page tucks into the bottom-left corner as a small tilted sheet and stays on screen. Chip ② exits right. Camera re-centres on header + chip ①. |
| 4.4–5.3 | agent 等于模型加 Harness | Continuous morph: "Harness²" travels and shrinks into the "Harness" of the formula, and "agent = 模型 +" wipes out from behind it. Chip ① flies to centre and morphs (rect to circle) into the 模型 circle with lock (whoosh, pop). |
| 6.3–7.4 | Harness 就是模型外面那一圈 | Dashed Harness ring grows outward from the circle edge with overshoot. Subtitle drops out of the header. |
| 7.85 / 8.45 / 8.87 / 9.23 | 提示词 / 记忆 / 技能 / 工具说明 | Each label is ejected from the circle onto the ring on its word (pop each). |
| 10.5–12.1 | 已经有不少工作在让 AI 自己改 Harness | Orange arc arrow draws around the ring (marker scratch). "AI 自己改" badge pops. The labels wobble one after another with orange borders ("being edited"). |
| 12.2–12.9 | (pause) | The same page object slides back in from the bottom-left corner while the diagram shifts right to 0.85x (whoosh). |
| 12.9–13.45 | 比如斯坦福… | 3D page turn (rotateY around the spine) from p1 to p7. Tag changes from p1 to §1 · p2 to §3.1 · p7. |
| 13.45–14.2 | …牵头做的 | Camera dives into the related-work sentence at 3.07x. Camera rotates +2° so the tilted page reads level (whoosh). |
| 14.0–14.85 | Meta-Harness | Marker sweep over "Meta-Harness (Lee et al., 2026b) searches harness code offline" (scratch). Hold to end. |

## Clip B: original 1:34.40 to 2:08.70 (34.8 s incl. tail)
Ends right after "一份只管这个行业的知识", before "论文发现…". This covers the 第二步 two-card build. Running to 2:13 would have cut the ablation sentence in half.

One big world canvas, left to right:
- Figure 9 page (x 0–1500)
- task station (~x 2000–3900)
- ① 跑原版 (~x 4400–6300)
- ② 提两份改法 (~x 8000–9900)

Camera moves are 0.75–0.95 s easeInOutCubic, with a zoom-out dip on the long travels. Directional motion blur is an SVG feGaussianBlur driven by camera velocity.

| t (s) | voice | technique |
|---|---|---|
| 0–2.5 | 我们拿论文里的这个例子走一遍 | Figure 9 as a physical page (-1.2° tilt, shadow, texture, greeked body text). Slow push from 1.0x to 1.05x. |
| 2.6–3.4 | 任务是帮制片人对账 | Camera dives into Figure 9's TASK box at 2.35x. A red outline draws around it (whoosh + scratch). |
| 3.45–4.6 | | The TASK box lifts off the paper (shadow, scale-up), then flies right and morphs (crop crossfades into the redrawn card) while the camera travels to the task station (whoosh, blur). The Figure-9 minimap slides in bottom-left from the page's direction, and the HUD progress chips drop in. |
| 4.4–7.0 | 排期表、人员名单、预算表…制作计划和备忘录 | File icons pop on each word, the arrow draws, then the deliverable pops. |
| 8.86 / 11.2 | Gemini 3.5 Flash / OpenCode | 干活 and Harness pills pop. |
| 12.15–13.0 | 第一步… | HUD ① lights and the camera travels to the ① 跑原版 station sign (whoosh). |
| 14.3–15.2 | 得了 43.1 分 | Number roll from 0.0 to 43.1 (12 ticks). |
| 16.25 | 整条流水线谁都看不到 | Lock drops in, then 流水线 / 看不到. |
| 17.95 | Claude Opus 4.8 | Opus card slides in from the right (pop). |
| 20.35–21.1 | 手里只有这次的执行记录 | Camera pulls back to 0.85x and the execution-log terminal rises into view. Lines type in (key ticks). |
| 21.97 | 几份文件里的数字从来没对过 | Red marker band over the 3 reads, bracket, "✗ 几份文件里的数字从来没对过" (scratch + pop). Minimap highlights failure note 1. |
| 24.07 | 交付物写完也没再打开检查 | Same treatment for the 2 writes. Minimap highlights note 2. |
| 26.85–27.8 | 第二步，它同时提两份改法 | HUD ① turns "done" and ② lights. Camera travels right to the ② station. The heading wipes in, and the minimap highlights IMPROVED HARNESS. |
| 28.5–29.3 | 分工不同 | One card grows, then splits into two (pop). |
| 29.65 / 30.5 | 一份只管通用的做事方法 | 通用 header pops. Minimap highlights guardrails.md + verify_outputs.py, and those two real Figure-9 crops fly out of the minimap into the 通用 card. |
| 32.65 / 33.35 | 一份只管这个行业的知识 | 行业 header pops. The SKILL.md crop flies from the minimap into the 行业 card. |

## Sound design (all synthesized in `build/audio.py`, no samples)
- **Voice:** original audio cut from v.mp4 at the same timestamps, normalized to about -16 LUFS.
- **Music bed:** warm additive pad (detuned, 1-pole low-pass), soft 8th-note arpeggio with a dotted-8th echo, sine bass. Fmaj7–Dm7–Bbmaj7–C7 at 84 bpm. Set to -28 LUFS after ducking. Ducking is -7 dB while voice is active (60 ms attack, 450 ms release).
- **SFX:** whole SFX track at about -24 LU relative to the voice.

SFX palette:
- **whoosh:** noise through a sweeping state-variable band-pass, with stereo pan sweep. Used on camera moves; a softer variant is used on small moves.
- **pop:** pitch-dropping sine blip, 120 ms. Used on card, label, ✗ and pill arrivals.
- **tick:** 2.6 kHz blip. Used on the number roll. A noise "key" click variant is used for log typing.
- **scratch:** band-passed noise with stroke amplitude modulation. Used on marker highlights, the red outline draw and the AI-edit arc.
- **paper:** hiss plus random crackle. Used on the page lift and the page turn.

## Rules check
- All UI text is ≥ 28 px: captions 44, HUD 30, tags 30, minimap label 28, smallest card text 28.
- Exceptions are paper crops only: Figure 9 / title / sentence crops while zoomed into, the minimap thumbnail, and the Figure-9 file crops inside the ② cards (about 0.78x native, so their body text is ~14 px). Those crops are illustrative; their 28 px labels carry the meaning.
- Self-check: 3 render rounds with 0.5 s contact sheets (`sheetA.png` / `sheetB.png`). Fixed:
  - meta text wrapping
  - formula wipe overlapping the moving "Harness"
  - empty half-screen at 先说背景 (camera re-centre added)
  - motion blur too strong during the sentence zoom
  - task card text overflowing on the right
  - station sign colliding with the HUD in the pulled-back framing
  - ② cards overlapping the minimap label
  - crops overlapping the card headers

## Could not do / weaknesses
- Could not fetch the arXiv PDF (proxy 403). Paper imagery is re-cropped from the original video, so the TASK-box dive upscales a ~250 px crop 2.35x and is visibly soft. The figure, title and sentence crops are at most about 1400 px wide.
- Greeked bars stand in for unreadable body text on the physical pages. That is honest, but less convincing than the real page.
- No human listening pass was possible. SFX and music levels were set numerically (LUFS / peak), so check on headphones and a phone speaker. Sample peak after AAC is -1.3 dBFS on A, just above the -1.5 TP target.
- Clip A's page turn is quick (0.55 s), and the turning sheet's back side is hidden rather than drawn.
- Panel ① at 1x leaves the lower third empty until the log is revealed at 20.4 s.
- The flying Figure-9 crops in ② are screen-space overlays. They are only valid because the camera is static there.

---
# v2 (clipA_v2.mp4, clipB_v2.mp4)
Sources: build/clipA_v2.html, build/clipB_v2.html. Rebuild with `bash build/make.sh A _v2 -2.0` and `bash build/make.sh B _v2 -1.8`.
Music and SFX are unchanged; the same synth with the same seed.

- **Real paper pages, no grey placeholder bars.** Source is `<work>/paper/harness2_2610.14224.pdf` (download it yourself from arXiv; not included in this repo), rendered with pdftoppm.
  - p1 and p7 at 300 dpi; p12 at 300 dpi for the page.
  - Figure 9 additionally at 720 dpi (vector figure, 4500x2280 px) as an overlay exactly on its page position.
  - The Google wordmark on p1 is painted over with white paper colour (300 dpi px x 240–505, y 160–262). The arXiv side stamp is left as is.
- **Clip A:**
  - The flat H02 title box is now a window onto the real p1 (title, authors, affiliations), and it unfolds into the full A4 page (600x848).
  - p7 is the real Related Work page.
  - The marker covers the exact span "Meta-Harness (Lee et al., 2026b) searches harness code offline": pdftotext -bbox x 204.7–496.8 pt, y 601.8–616.0 pt.
  - Sentence dive is 3.69x, so the page is shown at about 0.89x of 300 dpi. That makes it sharp, with ~37 px text on screen.
- **Clip B:**
  - Figure 9 sits on the real p12 page: figure, caption and the start of §5 Related Work.
  - The TASK-box dive (2.35x) and the lifted TASK piece use the 720 dpi render, about 0.73x native on screen, so both are sharp.
  - The minimap and the guardrails / verify_outputs / SKILL.md crops that fly into the ② cards also come from the 720 dpi render.
- **Clip B framing:**
  - Task card enlarged: 1760x460, title 72 px, file row 56 px, pills 46 px. Framed at 1.06x, so content fills ~97% of the width and ~61% of the height.
  - Step ① re-laid out with taller cards (600 and 940 wide, 430 tall) and framed at 1.1x. Cards now reach y≈780, which fills the old empty lower third from 13–20 s.
  - The pull-back to the log is unchanged (0.85x).
  - The opening camera sits 135–150 px lower on the page so the figure sits higher.
- **Clip A page turn:**
  - 0.8 s, 12.75–13.55 s.
  - The back of the sheet is drawn: off-white #f6f3ec, 13% mirrored show-through of p1, paper texture, spine shading. It lands as the left page of an open spread.
  - Timeline after it shifted ~0.15 s: zoom 13.55–14.25, marker 14.15–14.95, hold to 15.6 s.
- **Loudness (ebur128 true peak after AAC):**
  - A: loudnorm TP=-2.0, giving -15.9 LUFS and -1.9 dBTP.
  - B: loudnorm TP=-1.8, giving -16.0 LUFS and -1.7 dBTP.
- **Self-check:** 2 rounds of 0.5 s sheets (sheetA_v2.png, sheetB_v2.png), plus single-frame checks of the page turn and the sentence zoom.

Remaining weaknesses:
- At full sentence zoom, the real page's surrounding lines are visible behind the caption bar and the top-right tag. It is busier than v1, but it is real paper.
- In clip B's opening, the paper's own Figure 9 caption and the §5 heading sit just above our caption bar.
- The back of the turned page slides mostly off-screen left after landing.
