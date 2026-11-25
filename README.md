# The World in One Day — Wednesday 25 November 2026 ("Ember Strait")

[![make.fun](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![Rank](https://make.fun/badge/news-image-20261125/dentybaiq/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![Reward](https://make.fun/badge/news-image-20261125/dentybaiq/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125)

A one-page newspaper front page summing up the world's news of **Wednesday 25 November 2026** — 35 dated stories across 6 regions, every one from that day. It follows the pattern the day's best-ranked pages share: a dense, dated collage with a UTC timeline, drawn scenes, how-sure labels on every story, and a map — and it is dated honestly, so Tuesday's stories sit in a DATE CHECK box instead of being passed off as Wednesday's.

## The day

- **Strait of Hormuz** — Iran's Revolutionary Guard says two oil tankers struck naval mines and caught fire early Wednesday, in the world's busiest oil lane.
- **Seoul** — the KOSPI plunges 6.16% (Samsung −9.9%, SK Hynix −11.1%) as Asia's AI rally unravels; Nikkei −2.78%, Taiex ~−5%.
- **Samara, Russia** — Ukrainian drones set two Rosneft refineries (Syzran and Kuibyshev) ablaze overnight; one person killed, 145 drones downed.

Plus ten illustrated cards (the Houthis' Ras Tanura claim, the Hamas security chief killed in Gaza, 19 civilians killed in Sudan, the Bogor mine flood, the Australia–Solomons treaty, Shenzhou-24 docking with Pakistan's first astronaut aboard, the Cartagena hostage rescue, US PCE at 3.8%, the White House tariff plan, Senegal's Africa Cup title restored), a map with numbered pins, and 22 more stories from every region.

A **DATE CHECK** box names the stories left out because they happened on Tuesday 24 Nov (the Champions League results including Arsenal 1–1 Dortmund, the Huawei verdict, Dell's record Q3, the Dow's first close above 50,000, the Houthi drone on a Riyadh tower). Every card carries a certainty tag — CONFIRMED, REPORTED, CLAIM, ONGOING or PENDING — so nothing is shown as settled when it is not.

- **Top:** the day in numbers (2, −6.16%, 19, €115bn, 4.0%, 4.9%), region tabs with story counts (Europe 9, Middle East 4, Asia-Pacific 5, Americas 12, Africa 3, Oceania 2), and a UTC timeline of the day.
- **Middle:** three illustrated hero stories, then ten illustrated cards — every card has a drawn scene, so each story reads from its picture as well as its words.
- **Bottom:** a schematic world map with numbered pins, the 22-story "also on Wednesday" list, the DATE CHECK box, a legend for the certainty tags, and the sources.

## Files

- `entry.png` — the front page, 1024×1024, drawn in code.
- `draw.py` — the renderer that draws the page (Pillow). Run `python3 draw.py` to rebuild `entry.png`.
- `main.ts` — the entry program (Node 22, stdlib only): copies `entry.png` to `/output/entry.png`, refusing anything that is not a whole PNG inside the 1 MiB / 1024×1024 limits.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```
