[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

[![rank](https://make.fun/badge/news-image-20261126/afif-3/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

# The World Today - 26 November 2026 in one image

A newspaper front page that sums up Thursday, 26 November 2026,
rendered entirely in code with Pillow. No image assets, no network,
fully deterministic: the same code always draws the same page.

## Run

    python3 main.py

Writes `out/entry.png` (1600 x 2240). The committed `entry.png` at the
repository root is that exact render.

## Layout

- `main.py` - entrypoint and page composition (masthead, lead story,
  story grid, markets band, ticker, footer)
- `content.py` - the day's editorial content, cross-checked on the day
  against Reuters, One Turn's day report and the Daily Summary of World
- `render.py` - drawing toolkit: font resolution with fallbacks, text
  wrapping, tracked kickers, hand-drawn icons and charts

## The day it sums up

Lead: the US proposes new tariffs on 14 trading partners. Also on the
page: Houthi strikes on Saudi ports and the Ras Tanura refinery, the
Cairo ring-road tanker fire (31 dead), EU leaders clashing over a
45bn euro Ukraine loan, the AI sell-off pushing the Nasdaq toward a
bear market, and the first Pakistani astronaut boarding China's
Tiangong station - plus a six-item ticker of the day's other stories.
