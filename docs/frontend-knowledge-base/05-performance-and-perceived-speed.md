# 05. Performance and Perceived Speed ("Intuitive Performance")

## 1. Human time thresholds

| Threshold | Meaning | Source |
|---|---|---|
| **~16 ms/frame** | 60 fps animation reads as smooth; budget ≈ 10 ms of your own work per frame | web.dev RAIL (A/B) |
| **0.1 s (100 ms)** | Feels instantaneous; the outcome feels caused by the user (direct manipulation). No special feedback needed except the result. | Nielsen, [Response Time Limits](https://www.nngroup.com/articles/response-times-3-important-limits/) and [Website Response Times](https://www.nngroup.com/articles/website-response-times/); web.dev notes basis in Michotte (1962): up to ~100 ms perceived as causal, 100-200 ms mixed, >200 ms not (B) |
| **1 s** | Flow of thought uninterrupted; users notice the delay and lose the "direct" feel. Show that something is happening if longer. | Nielsen (B) |
| **10 s** | Limit for keeping attention; give percent-done and a way to cancel; users will switch tasks and need to reorient. | Nielsen; RAIL says users "frustrated and likely to abandon" (B) |

Nielsen: "A 10-second delay will often make users leave a site immediately," and repeated few-second delays make less-committed users give up (commercial claim like "lose half your sales" is NN/g opinion; treat as illustrative **(judgment)**).

## 2. Core Web Vitals (Google; measured at the 75th percentile of page loads, segmented by mobile/desktop)

| Metric | Measures | Good | Poor |
|---|---|---|---|
| **LCP** Largest Contentful Paint | Loading: when main content likely loaded | ≤ 2.5 s | > 4.0 s |
| **INP** Interaction to Next Paint | Responsiveness to input | ≤ 200 ms | > 500 ms |
| **CLS** Cumulative Layout Shift | Visual stability | ≤ 0.1 | > 0.25 |

Sources: [web.dev thresholds](https://web.dev/articles/defining-core-web-vitals-thresholds), [web.dev vitals](https://web.dev/articles/vitals). A page passes only when all three meet targets at p75. web.dev also states the research basis (Michotte) for the 100 ms idea behind interactivity thresholds. Metrics evolve; re-check before use.

RAIL guidance (older but useful model): respond within 100 ms (process input events within 50 ms); animate at 60 fps; use idle time (work in chunks of ≤ 50 ms); load and become interactive in ≤ 5 s on mid-range mobile over slow 3G for first load, ≤ 2 s for subsequent loads.

## 3. Perceived performance research (loading feedback)

| Study | Design | Result | Limits |
|---|---|---|---|
| **Feedback preferences and impressions of waiting** (Human Factors, [doi](https://doi.org/10.1177/0018720809345684)) | Three experiments with static, sequential dots, constant-rate and variable-rate progress bars | Users preferred feedback with more information, but simpler displays made waits seem more reasonable. **A constant-rate progress bar did best on both** (informative without raising arousal). Consistent with the attentional gate theory of timing. | Student participants; simulated task |
| **Partitioning progress indicators** (J. Korean Inst. Ind. Eng., [doi](https://doi.org/10.7232/jkiie.2018.44.4.297)) | 30 young adults; bars vs spinners; 4/10/20 s | Perceived wait fell as partitions increased; bars preferred to spinners; excessive partitioning caused eye fatigue and annoyance; partitioning didn't affect satisfaction. | Small, young sample |
| **OutSystems case study** (Utrecht Univ. thesis, [repo](http://dspace.library.uu.nl/handle/1874/405560)) | Five feedback types in a platform's loading moment | **Progress bar** most satisfying (clear temporal info, more perceived control); experienced users valued skeleton structure; proposed skeleton + progress bar. | Thesis, single product |
| **Skeleton screens vs spinners** (ECCE 2018, [ACM](https://dl.acm.org/doi/10.1145/3232078.3232086)) | Fictional news site | Skeleton scored higher on perceived speed and ease of navigation; spinner users were faster to find the article; **no statistically significant differences**. | Small, null result |
| **Six loading strategies, 5 s fixed** (IHC 2025, [doi](https://doi.org/10.5753/ihc_estendido.2025.13255)) | 21 participants, mostly under 35 and technology professionals | **Skeleton** best (48% judged it fast, 1-3 s); **blank page** worst (52.4% slow or very slow) despite identical real time; cyclic (spinner, skeleton) beat determinate bars; combining techniques did not help. | Exploratory, n=21, young tech sample; conflicts with progress-bar results above |

**Synthesis (judgment):** Results disagree because durations, tasks, and participants differ. Robust points: (1) never leave a blank screen; (2) give feedback for anything >~100-300 ms; (3) for waits of several seconds or more, determinate progress helps users judge when to wait vs. act; (4) skeletons help when you know the layout and the wait is short-to-moderate; (5) avoid stacking indicators; (6) keep indicator motion calm.

## 4. Engineering patterns that produce intuitive speed

### Loading
- **Ship less JavaScript.** Code split by route; defer non-critical scripts; avoid hydrating static content (islands/server components).
- **Optimize the LCP element:** prioritize hero image (`fetchpriority="high"`, `<link rel=preload>`), responsive images (`srcset`, `sizes`), modern formats (AVIF/WebP), correct dimensions.
- **Fonts:** subset, self-host, `font-display: swap` or `optional`, preload critical weights, size-adjust fallback fonts to limit CLS.
- **Server:** CDN and caching, HTTP/2 or 3, compression (Brotli), streaming HTML, early hints.
- **Stable layout:** set `width`/`height` or `aspect-ratio`; reserve slots for ads, embeds, and banners; never insert content above existing content after load; animate with `transform`.

### Responsiveness (INP)
- Keep main-thread tasks under ~50 ms; split long tasks; yield (`scheduler.yield`, `requestIdleCallback`); move heavy work to Web Workers.
- Debounce expensive handlers; virtualize long lists; avoid layout thrashing; prefer CSS for animations.
- **Optimistic UI:** reflect the action immediately, reconcile with the server; show failure and offer retry.
- **Immediate acknowledgment:** pressed states within 100 ms; disable buttons during submit with a visible "Saving…" and prevent double submission.

### Perceived speed
- **Skeletons that match final layout** (same dimensions, no content shift).
- **Progress with real information** for operations >~1-2 s; **percent or steps** for >10 s with cancel.
- **Prefetch likely next routes** on hover or viewport; cache; stale-while-revalidate.
- **Progressive rendering:** show headline and text first, then images; lazy-load below the fold.
- **Preserve state** on navigation (scroll, form data, filters).
- **Motion:** 100-200 ms feedback, 200-400 ms transitions; ease-out in; reduced-motion variant. Motion that blocks input feels slow.

### Resilience (performance when things go wrong)
- Offline/slow-network states, retries with backoff, timeouts with clear messages, saved drafts.
- Test on a mid-range Android device with throttled CPU and slow 4G, since median devices not developer laptops define experience. **(judgment, consistent with RAIL's mid-range mobile target)**

## 5. Measure it

| What | Tool |
|---|---|
| Lab | Lighthouse, WebPageTest, Chrome DevTools Performance panel |
| Field (real users) | Chrome UX Report (CrUX), `web-vitals` JS library, RUM tools |
| Interaction latency | DevTools INP debugging, Long Animation Frames API |
| CI budgets | Lighthouse CI, bundle-size limits |
| Perception | Task tests with time estimates; think-aloud; satisfaction (SUS/UEQ) |

Use field data for decisions: lab scores don't equal p75 user experience.

## 6. Accessibility and performance meet

- Fast does not equal accessible: announce loading and results via live regions; maintain focus; don't remove focus on content swaps.
- Respect `prefers-reduced-motion` and `prefers-reduced-data` where supported.
- Timeouts need warnings and extensions (WCAG 2.2.1).
- Large text, zoom, and forced-colors modes must not trigger layout shift or clipping.

## Refresh note (2026-11-13)

Core Web Vitals thresholds are unchanged (LCP 2.5 s, INP 200 ms, CLS 0.1 at p75). Chrome added experimental soft-navigation variants to CrUX and plans to include them from May 2027; in the latest CrUX release 56.3% of origins had good stable vitals. See [master guide, 11.2](../FRONTEND-MASTER-GUIDE.md#112-core-web-vitals-refreshed-2026-11-13-thresholds-unchanged).
