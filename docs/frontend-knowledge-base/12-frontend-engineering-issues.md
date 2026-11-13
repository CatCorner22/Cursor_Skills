# 12. Frontend Engineering Issues: Rendering, State, Security, Privacy, SEO, Testing, Budgets

Researched 2026-11-11. Mostly standards and official docs (grade A/C); few controlled studies exist for this area. **(judgment)** = inference. **(not researched)** = unverified.

## 1. Rendering strategies (SSR, SSG, ISR, CSR, hydration, RSC)

| Strategy | Verified trade-off (web.dev) | Best for **(judgment)** |
|---|---|---|
| **Static rendering (SSG)** | HTML built at build time; consistently fast TTFB, fast FCP, low TBT/INP **if** client JS is limited; deployable to CDN edge caches. Cannot personalize per request. | Marketing, docs, blogs |
| **Server-side rendering (SSR)** | HTML per request; fast FCP and less client JS, but server compute cost and higher TTFB; synchronous `renderToString()` can be slow; streaming APIs get HTML out sooner. Doing a lot of client work after SSR HTML still hurts TBT/INP. | Personalized/dynamic pages that need SEO |
| **Client-side rendering (CSR)** | Low TTFB but content waits for JS; JS tends to **grow with the app**, hurting INP; HTML created on the client is invisible to the preload scanner, hurting LCP; tasks aren't automatically chunked. | Logged-in app shells where SEO is irrelevant |
| **Hydration** | SSR + client JS to make it interactive; improves FCP but can add TBT/INP until scripts run. | |
| **ISR / streaming / RSC** | See note below. | |

Source: [web.dev, Rendering on the Web](https://web.dev/articles/rendering-on-the-web), [web.dev, Client-side rendering](https://web.dev/articles/client-side-rendering-of-html-and-interactivity), [web.dev, Optimize TTFB](https://web.dev/articles/optimize-ttfb) (all C+, Google-authored reference). TTFB is **not** a Core Web Vital; a higher-TTFB server-rendered page can still beat a CSR page on FCP/LCP.

**ISR and React Server Components:** the web.dev pages above describe SSR/static/CSR/hydration; I did **not** fetch primary docs for ISR (Next.js) or RSC internals this session. Secondary description: RSCs are async server functions returning JSX; the React team suggests E2E tests as the primary way to test them (per [Storybook blog](https://storybook.js.org/blog/component-testing-rscs/), C/D). Check the Next.js and React docs directly before relying on details.

**Decision aid (judgment):** default to static; add server rendering where content is dynamic and SEO matters; use client rendering for behind-login interactivity; budget JS regardless.

## 2. State management

| Principle | Source | Grade |
|---|---|---|
| React's own guidance: group related state; avoid contradictory, redundant, duplicated, deeply nested state; store IDs not objects for selection; do not copy props into state unless intentional. Goal: "make state easy to update without introducing mistakes." | [react.dev, Choosing the State Structure](https://react.dev/learn/choosing-the-state-structure) | C+ (official docs) |
| Classify state before reaching for a library **(judgment)**: UI state (local), server cache (fetch/cache lib), URL state (router), form state (form lib), global app state (rare). | | |

Not researched: Redux/Zustand/Jotai/TanStack Query comparisons; signals. Treat library rankings as opinion.

## 3. Forms and validation

UX evidence lives in [03](03-cognitive-load-and-frustration.md) and [06](06-input-reading-and-forms.md) (inline validation study, labels, errors). Engineering notes **(judgment)**: validate on the server always; mirror rules on the client for feedback; keep native input types and `autocomplete`; preserve input after errors; disabled-submit pitfalls in 06. Form-library comparison (React Hook Form, Formik, native) was **not researched**.

WCAG tie-ins: 3.3.1 Error Identification (A), 3.3.2 Labels or Instructions (A), 3.3.3 Error Suggestion (AA), 3.3.4 Error Prevention for legal/financial/data (AA), 3.3.7 Redundant Entry (A), 3.3.8 Accessible Authentication (AA), 4.1.3 Status Messages (AA) for announcing validation results.

## 4. Security basics for frontends

| Topic | Verified guidance | Source | Grade |
|---|---|---|---|
| XSS main defense | **Output encoding** (treat untrusted data as text, context-specific) and **sanitization**; frameworks escape by default. | [OWASP XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html), [MDN XSS](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/XSS) | C+ |
| Escape hatches | React `dangerouslySetInnerHTML` disables encoding (MDN says so); also Angular `bypassSecurityTrustAs*`, Lit `unsafeHTML`. Unvalidated URLs (`javascript:`) remain a risk; OWASP says React 19 blocks `javascript:` URLs in `src`/`href` but that does not replace app-level URL validation. | OWASP | C+ |
| Sanitizing HTML | If you must render HTML, sanitize at render time with an allowlist (DOMPurify is the library named by the WSO2 guide). | [WSO2 React guide](https://security.docs.wso2.com/en/latest/security-guidelines/secure-engineering-guidelines/secure-coding-guidlines/general-recommendations-for-react-secure-coding/) | D (vendor guide) |
| CSP | A **backup** if encoding fails, not the primary defense. Recommended: **strict CSP** with nonce or hash; disables inline handlers and `eval()`; `object-src 'none'`, `base-uri 'none'`; `strict-dynamic` for chained scripts. Send as an HTTP header on all responses. | [MDN CSP guide](https://developer.mozilla.org/en-US/docs/Web/Security/Practical_implementation_guides/CSP), [OWASP CSP](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html) | C+ |
| Trusted Types | CSP directive `require-trusted-types-for 'script'` makes DOM XSS sinks reject plain strings; does not sanitize by itself. | OWASP XSS sheet | C+ |
| Cookie attributes | Limit XSS *impact* but do not stop execution. | OWASP | C+ |

Auth UX: WCAG 3.3.8 forbids requiring memorization/transcription/puzzles unless an alternative or mechanism exists; allow paste and password managers; WebAIM's screen reader survey found CAPTCHA "by far the most problematic barrier" ([WebAIM #10](https://webaim.org/blog/screen-reader-user-survey-10-results/), B- self-selected sample of 1,539). Passkey and session-handling details: **not researched**.

## 5. Privacy and consent UX (GDPR / ePrivacy / CCPA-CPRA)

I am not a lawyer; confirm with counsel. See also [01](01-legal-and-compliance.md) for US dark-pattern enforcement.

| Finding | Source | Grade |
|---|---|---|
| In experiments with 80,000+ users on a German site, consent-banner **position, choice type, and nudging** strongly changed outcomes: bottom-left banners drew more interaction; a binary choice got more acceptance than per-category choices; highlighted or pre-selected "accept" increased consent. With privacy-by-default opt-in, <0.1% allowed cookies for all purposes. | [Utz et al., CCS 2019](https://dl.acm.org/doi/10.1145/3319535.3354212) | B (peer-reviewed; one German site) |
| Crawl of ~11K shopping sites: 1,818 dark-pattern instances on 1,254 sites (~11.1%), 15 types / 7 categories; a lower bound; 183 sites deceptive; 22 third parties sold dark patterns as a service. | [Mathur et al. 2019](https://arxiv.org/html/1907.07032v2) | A- |
| EDPB Cookie Banner Taskforce (Jan 2023): most authorities treat a missing reject option on the first layer as not valid consent; a reject **link** buried in text without visual support does not give valid consent; withdrawing consent must be as easy as giving it; colors/contrast judged case by case. | [EDPB report](https://www.edpb.europa.eu/system/files/documents/2023-01/edpb_20230118_report_cookie_banner_taskforce_en.pdf) | A (regulator work, not legislation) |
| CNIL (France) ordered publishers to change banners where rejection was harder than acceptance (reject as a small link; accept repeated; reject worded obscurely). | [CNIL](https://www.cnil.fr/en/dark-patterns-cookie-banners-cnil-issues-formal-notice-website-publishers) | A |
| EDPB Guidelines 03/2022 on deceptive design patterns (social media platforms), version 2.0, exist. I saw only the title page. | [EDPB](https://www.edpb.europa.eu/documents/guideline/guidelines-032022-on-deceptive-design-patterns-in-social-media-platform_en) | A (title only) |
| California: businesses must honor opt-out preference signals; Global Privacy Control (an HTTP header / JS property) qualifies; comply no later than 15 business days; conflicts with site-specific settings resolve in favor of the signal; consent prompts must avoid dark patterns. | [California Privacy Protection Agency overview (2026)](https://privacy.ca.gov/wp-content/uploads/sites/357/2026/07/20260806_07_02.pdf) | A |
| GPC: no European regulator has explicitly ruled it has GDPR effect (per the GPC explainer; some commentators argue it does). | [GPC explainer](https://w3c.github.io/gpc/explainer.html) | C+ |

**Engineering checklist (judgment from the above):** reject as prominent as accept on the first layer; no pre-ticked boxes; no cookies before consent where required; easy withdrawal link; detect and honor `Sec-GPC: 1` for California visitors; document your analytics tags; test banners with real users.

## 6. SEO for frontend engineers

| Fact | Source | Grade |
|---|---|---|
| Google crawls, renders (headless Chromium), and indexes; JS pages queue for rendering and may wait; pages blocked by robots.txt are not rendered. | [Google JS SEO basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics) | C+ |
| Dynamic rendering is "a workaround and not a long-term solution"; Google recommends SSR, static rendering, or hydration. | [Google dynamic rendering](https://developers.google.com/search/docs/crawling-indexing/javascript/dynamic-rendering) | C+ |
| Google says useful, original, people-first content likely influences search presence more than other tips; says it has no preferred word count; says changing dates or deleting content to look "fresh" will not help. | [Google SEO starter](https://developers.google.com/search/docs/fundamentals/seo-starter-guide), [helpful content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) | C+ |
| Other search engines may ignore JavaScript. | Google dynamic rendering page | C+ |

I did **not** verify how much Core Web Vitals influence ranking (a search summary claimed they are "ranking factors"; my fetched excerpts did not show it). Treat as unverified; page experience matters for users regardless.

## 7. Testing

| Idea | Source | Grade |
|---|---|---|
| Test pyramid: tests of different granularity; the higher the level, the fewer tests; beware the "ice-cream cone" (too many slow UI tests). Fowler calls the pyramid "overly simplistic" but a useful rule of thumb. Arrange-Act-Assert structure. | [Fowler, Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html) | C+ |
| Frontend three tiers (one SitePoint tutorial): unit (pure logic), integration (components with mocked boundaries; "most test value"), E2E (hydration, streaming, critical journeys; 10-100x slower, more flaky). Single-author claim; plausible. | [SitePoint](https://www.sitepoint.com/testing-react-server-components-vitest-async-boundaries-mock/) | D |
| "Testing trophy" (Kent C. Dodds) emphasizes confidence per cost; I saw only a search-summary mention, not the source. | | unverified |
| Add: automated a11y (axe) in component and E2E tests; visual regression (see [10](10-design-systems-and-tokens.md)); manual screen reader and keyboard passes. Automated tools find a minority of WCAG criteria (Deque 16 of 50) even if a larger share of issue volume. | Deque / Springer in [10](10-design-systems-and-tokens.md) | B- / A- |

## 8. Performance budgets, bundles, and compatibility

| Fact | Source | Grade |
|---|---|---|
| A budget is limits on metrics (page weight, load time on a network, request count). web.dev starter defaults: under 5 s Time to Interactive and under **170 KB** critical-path resources (compressed/minified) on a baseline mobile device and 3G; example budgets per page type. **These are old defaults; re-derive for your audience** **(judgment)**. | [web.dev Performance budgets 101](https://web.dev/articles/performance-budgets-101) | C |
| Lighthouse CLI supports budgets by resource size/count per type (document, font, image, media, script, stylesheet, third-party, total). webpack warns at 250 KB by default for assets/entrypoints (uncompressed). `bundlesize` and Lighthouse CI can fail pull requests on regressions. | [web.dev, budgets in build tools](https://web.dev/articles/incorporate-performance-budgets-into-your-build-tools) | C |
| Core Web Vitals thresholds already in [05](05-performance-and-perceived-speed.md). | | |
| Experimentation evidence: at Bing, a 10 ms server improvement "more than pays for" an engineer's annual cost (Kohavi et al.; vendor-scale claim). | [Seven Rules of Thumb](https://exp-platform.com/Documents/2014-08-27ExperimentersRulesOfthumbKDD.pdf) | B (peer-reviewed KDD, one company) |

Browser compatibility, analytics ethics, tech debt, error-boundary patterns, and Tailwind/CSS-in-JS trade-offs: **not researched this session**. Use MDN compat tables and caniuse; adopt "Baseline" as a decision aid after verifying its definition on web.dev.

## 9. Error handling UX (judgment, anchored in Nielsen heuristics)

Plain language, specific cause, a way forward, preserve user input, never blame the user; log with context for support. Heuristic text: [NN/g](https://www.nngroup.com/articles/ten-usability-heuristics/).

## 10. Analytics ethics (partially researched)

Verified only through the consent material above: nudged consent changes data you collect, so analytics from consent-gated users are a **biased sample**, and A/B tests need trustworthy instrumentation ([13](13-ux-research-methods-and-measurement.md)). Broader ethics (fingerprinting, dark analytics, retention) not researched.

## Refresh note (2026-11-13)

The vitals-and-ranking question is resolved to Google's wording: good vitals "aligns with what our core ranking systems seek to reward"; no weight is stated. Treat any ranking effect as modest and unquantified.
