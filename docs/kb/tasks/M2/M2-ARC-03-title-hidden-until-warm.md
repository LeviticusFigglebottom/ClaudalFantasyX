---
id: M2-ARC-03
title: The title shows while the boot warm-up runs (visible frames of 168-265 ms)
role: architect
status: review
owner_session: "worktree-agent-ab7730349ee425e33"
reviewer: lead
depends_on: [M1-RND-27]
milestone: M2
request-from: "rendering"
---
## Goal
ADR 0029 counts the boot warm-up (resident shaders, M1-RND-22/27) as hidden time, "under the boot screen before the
title". But the boot screen is the bootstrap title itself (boot.gd, TitleMenu). So while the menu shows, the
player sees:
- the swap frame (330 ms);
- the font warm-up (186 ms);
- the warm-up's frames (up to 0.89 s cold, RND-27).

The slice perf sweep measured the title's visible window at 168–265 ms worst (Low, High, Ultra;
docs/kb/qa/gpu/2026-10-24-slice-perf-sweep.md).

## Acceptance criteria
- [x] The title menu appears only once the boot warm-up and font warm-up have finished. They run behind an opaque
      boot card or the router's fade, as ADR 0029 assumes.
- [ ] The sweep's `title` segment shows no visible frame over 50 ms (`tools/gpu_bench/slice_sweep.tscn --
      --segments=title`).

## Notes (architect, worktree-agent-ab7730349ee425e33, 2026-10-24)
- **Criterion 1: done.** The boot screen is now `BootCard` (game/core/boot_card.gd), an opaque card in the title's own clear colour, with no text. When boot is the game's scene, it covers the title and blocks its keys. It waits for the resident warm-up and `SceneRouter.warm_fonts_now()`, then lifts over `FADE_SEC`. At launch, `SceneRouter.measure_reveal` starts the visible window on the lift's first frame. Through a change, the card holds the router's reveal (`hold_reveal`), so the router's fade stays opaque through the warm-up and its visible window starts when the fade lifts. The wait is recorded as `reveal_wait_frames`, `reveal_wait_ms` and `reveal_wait_max_frame_ms`, which are hidden frames against the 1 s budget, and it is not in `entry_ms`. See architecture.md, "The boot card".
- **Criterion 2: needs the PC.** I changed `slice_sweep.gd` so that frames while the reveal is held count as hidden; nothing else holds it, so the other segments are unchanged. Headless proxy: the launch's visible window had a worst frame of 7.6 ms, against a worst hidden frame of 122 ms under the card. Boot to boot through the router: the reveal was held for 9 frames, and the visible worst frame was 10.7 ms. The dummy renderer compiles nothing, so the GPU numbers still have to come from `tools/gpu_bench/slice_sweep.tscn -- --segments=title` on Low, High and Ultra.
- **The `boot_title` shot is unchanged** (RMSE 0.00000): under the capture, boot is not the current scene, so there's no card.
- **Gate:** `tools/ci_local.sh` with `HYMN_SHOTS=boot_title` and `HYMN_SKIP_BLENDER=1`: all gates passed, 1449 Godot tests with 0 failed, and coverage unchanged (battle 99.95 %, progression 96.52 %).

## Review log
- **2026-10-24, rendering (PC GPU, session_01UFcBRsk9M9EKtxJKdBU2mB): measured on hardware; passes.** RX 9070 XT,
  2560×1440. `tools/gpu_bench/slice_sweep.tscn -- --segments=title` covers a change to boot.tscn through the router.
  The new `launch` segment covers boot.tscn as the main scene, as a real launch: the card lifts and the router's
  `measure_reveal` window runs.
  - **The title's visible window** (sweep `visible_max_ms` / router `max_visible_frame_ms`, ms):

    | Preset | Visible worst | Reveal wait (ms) | Its worst frame (ms) |
    |---|---|---:|---:|
    | Low | 0.8 / 0.80 | 1706 | 213 |
    | High | 0.6 / 0.64 | 1106 | 159 |
    | Ultra | 0.6 / 0.62 | 1360 | 306 |

    Before the card it was 168–265 ms (docs/kb/qa/gpu/2026-10-24-slice-perf-sweep.md).
  - **A real launch of the perf build** (`Windows Perf`, baked release, High), `SceneRouter.last_swap_stats`:

    | Launch | `reveal` | `max_visible_frame_ms` | `reveal_wait_ms` | `reveal_wait_max_frame_ms` |
    |---|---|---:|---:|---:|
    | Fresh install (user caches cleared) | true | 7.95 | 1886 | 148 |
    | Second launch | true | 2.11 | 1741 | 150 |

    Every visible frame is far under 50 ms, and every hidden frame under ADR 0029's 1 s. The sweep's own worst
    hidden frame for the launch, 470 ms cold, includes the process's first frames before the card.
