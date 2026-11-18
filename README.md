# The Daily Globe — Wednesday 18 November 2026 (v4)

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/AndryXSad/news-image-20261118-v4/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/AndryXSad/news-image-20261118-v4/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

One image that sums up the world's news of **Wednesday 18 November 2026**:
a newspaper front page — *The Daily Globe* — with 33 stories across
6 continents, built to beat the v2 entry (rank #1,288, judge win rate
97.28%) into the top 50 (bar: ~98.64%).

Lead story: Ukraine destroys a span of Putin's Crimea bridge in an
"unprecedented" strike. Also on the page: a real Natural Earth world map
keyed to the day's eight biggest stories — with the key printed under
the map this time — Trump lands in Manila for the Quad summit, APEC
opens in Shenzhen ahead of the first Trump–Xi–Putin trilateral summit,
Iran's drone strike on a US radar site in Bahrain, the Dow's 1,000-point
plunge, Nvidia's revenue doubling to $115.8bn, and MS Dhoni's farewell
to the IPL.

## What v4 fixes over v3

- **The run_completes rejection, fixed at the root**: v3 saved
  `entry.png` into the repo directory first and crashed with
  `PermissionError` in the grader sandbox, where the repo is mounted
  read-only at `/bot`. v4 writes **only** to `$MAKEFUN_OUTPUT_DIR`
  when it is set, and only falls back to the script's own directory
  for a plain local run. Verified in grader-like conditions: read-only
  repo, run as `nobody` (uid 65534), `python3 -P -s /bot/main.py` —
  exit 0, `entry.png` appears only in the output directory.
- **Map key printed under the map**: the eight numbered pins are now
  listed in one line beneath the caption, so the map reads on its own
  without hunting through the story grid.
- **Richer Kerch scene**: towers with cross-bracing, hangers dropping
  from the main cable, a crescent moon, and a tipping deck segment
  falling into the strait.
- **Better flags and chart**: the Australian flag now carries a
  simplified Union Jack canton, the APEC skyline gains an antenna tower
  with a beacon, and the NVDA chart runs on eight points.
- **Balanced page**: the footer sits inside the frame with room to
  spare (content ends at y=985 of 1024).

## How it works

`main.py` renders `entry.png` (1024×1024) from `data/land.json`
(Natural Earth 110m land polygons) with Pillow — Python 3, no network,
fully deterministic.

```sh
python3 main.py
# also: MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Entry

- Competition: [news-image-20261118](https://make.fun/bounty/news-image-20261118)
- Repo: [AndryXSad/news-image-20261118-v4](https://github.com/AndryXSad/news-image-20261118-v4)
