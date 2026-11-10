# X News · D 影像刊

## Build brief / direction anchor

Chosen explicitly by the owner: “选四吧” (2026-11-06, Asia/Shanghai). The direction anchor is `.dir-d` in `design-previews/2026-11-06-xnews-ux/index.html`, not the recommended A. This implementation carries D into the real static site; it does not copy the preview shell or mock editorial titles.

Chinese overseas-discovery reader for 向阳乔木 and Chinese creators. Morning scan (5–15 minutes), then read one piece deeply. Functional contract: identify useful recent stories within three seconds; open a complete article; switch 乔木改写 / 原文 without losing reading position; reach the original and full RSS in one action; readable light/dark. Default design dials: visual variance 6, motion 4, density 6.

## Visual theme & assets

Bright, high-contrast visual journal. Real source covers are large; text-only stories become typography compositions based on stored author/name/title, never invented photographs or factual claims. Chronological DOM/order and existing article titles are preserved. Cover emphasis is a layout choice, not an invented editorial ranking. Header belongs to the same paper, with no left sidebar. Footer is a thin rule with RSS and About.

Only source `original.media` images/posters and thumbnails deterministically tied to the existing YouTube URL are allowed. Keep all original media and source/related links. Failed covers become typographic surfaces; original media always has a source-link fallback. Videos/audio never autoplay. Do not describe available video excerpts as complete transcripts.

## Palette / roles

- Paper `#fffefa`; ink `#1b1d18`; muted olive `#62685a`; rule `#d8dccf`.
- Editorial secondary surface `#eef0e5`; sage text-cover surface `#dce3cc`, ink `#293026`.
- Dark mode paper `#20241e`, text `#eef0e7`, secondary `#b7c1af`, rule `#4b5842`.
- Focus ring dark green `#315b3c` (light) / `#c0d9aa` (dark). No purple, glow, gradients or texture behind prose.

## Typography

Chinese body/UI: `-apple-system, BlinkMacSystemFont, PingFang SC, Hiragino Sans GB, Microsoft YaHei, Noto Sans SC, Noto Sans CJK SC, sans-serif`. No network fonts. Latin masthead pairs an original geometric X SVG with a tightly spaced Georgia News wordmark and an olive full stop; author/number cover typography also uses Georgia as an editorial counterpoint. The SVG mark is reused in the favicon. Latin-only optical tracking is allowed; Chinese tracking stays natural. No italics: Markdown emphasis stays semantic but is displayed upright. No negative Chinese tracking.

Masthead 52–62 px; card titles 21–32 px, weight 600; article title 29–48 px, line-height 1.4; prose 18 px desktop / 17 px mobile, line-height 1.95, max 42rem. Metadata >=12 px; touch controls >=44 px. Keep real long titles; no fabricated short headlines.

## Layout / components / depth

Max canvas 1320 px; desktop gutters 32 px, mobile 18 px. Base spacing 8 px; card gaps 20/24 px. Desktop asymmetric 12-column grid: the lead story spans 8 columns in the opening row, its neighboring story spans 4; subsequent stories each span 4. The lead headline precedes its image in both DOM and visual order, keeping it visible in the first screen. Filtered results have equal weight. Archive defaults to a text-only list; either list can switch between journal and quick-scan views. At tablet, two columns; mobile one. DOM/focus order stays chronological; do not use dense packing that changes reading order. Cards are editorial story containers, not arbitrary UI boxes. Nearly square corners (0–4 px); circular icon controls only where appropriate. Flat covers, thin full borders, no decorative left stripes. Three levels: paper, media/type card, full-viewport reader layer.

## Reader and navigation

Real anchor cards point at stable `/a/<id>` URLs. With JS, same-origin article HTML is progressively fetched into a full-screen dialog; loading/error/retry are local. Native `showModal` supplies focus containment, with fallback focus handling. Close/Escape/browser Back restore list scroll and originating focus; Forward reopens the sheet. Modified clicks remain ordinary links. Direct routes are independent full HTML documents and work without JS.

Without JS, semantic section links navigate both complete bodies. JS upgrades these to accessible manual-activation tabs and displays only one body, avoiding duplicated giant scroll. Each panel has a separate saved position; tab URL uses real `#rewrite` / `#original` fragments. Source and related links remain accessible outside the panels. Closing/switching pauses native media and unloads hidden embeds. Media failures never erase the article.

## Motion / states

Only intentional cover hover (180 ms, transform), restrained sheet appearance (180 ms), immediate pressed state. No drag/swipe simulation or spring theatrics. Keyboard and reduced-motion paths remain static. Hover transforms only for a fine pointer. Loading skeleton is shown only after an actual article request; retry preserves list context. Empty list / missing original / failed media / failed article fetch have a useful next action. Theme is persisted safely when storage is available.

## Donor DNA (not brand copying)

From Pinterest DESIGN.md: photography/content supplies depth rather than shadows; warm olive secondary text `#62625b` informs our `#62685a`; 8 px spacing rhythm; 16/24 px grid rhythm. From Sanity DESIGN.md: measured ~1440 px content canvas translated to 1320 px, 32/16 px gutters translated to 32/18, dramatic display/body scale, and 44 px touch controls. Deliberately reject Pinterest rounded-pin branding/red, and Sanity dark/neon/negative tracking. The selected D preview controls palette and layout over both donors.

## Boundaries / observable acceptance

Do not edit content JSON, IDs, source URLs, GUIDs, publish dates or existing Markdown. Generate from the latest filesystem inputs. Preserve full RSS rewrite + stored original + media, not summaries. No crawler work. No production deployment, push or commit until the parent finishes visual QA. Test: local build; every article/static route; RSS item count/links/full body/media; JSON hashes; JS state/race/error tests; HTML/CSS/JS syntax. Parent must visually inspect desktop, mobile, dark, full-sheet history/focus/scroll, media loading and no-JS routes. No screenshot or browser pass is claimed by this executor.


## Refinement after parent desktop QA · 2026-11-06

- Keep D's asymmetric editorial composition. Text cards now align to their content rather than stretching to a neighboring grid row; type-cover minimum drops from 125px to 90px. Card titles cap at 23px (featured 34px); compact gaps and natural footer spacing replace auto-pushed blank bodies. The featured source image can occupy residual height while its text body stays content-sized. Mobile resets cover flex sizing to its natural aspect ratio.
- Primary navigation is 15px desktop / 14px narrow; dates/authors/source actions and article metadata are 14px desktop, with narrow low-priority actions at 13px. Keep full real titles, Chinese system fonts, focus states and reduced motion; no line clamp or fake replacement covers.
- Seven real public JPEG images/posters returned normal curl HTTP 200 and were preserved byte-for-byte in `public/media/` (339920 bytes total). `src/media-manifest.json` is a rendering-only source-to-local map with provenance and hashes. Source JSON and RSS retain upstream HTTPS image/poster URLs. No video/audio binary is bundled.
- Chinese reading flow now includes source media through ordered `rewrite_media` references, not only the original tab. Stable IDs come from explicit source IDs or a deterministic type/URL hash. Known paragraph placement is checked for a unique full Markdown block; unknown positions are honestly labeled after-body source-media blocks. Per-section deduplication and explicit omission reasons prevent silent loss. Both tabs pause native media and unload hidden embeds.
- Native media errors expose an accurate cannot-play message, true local poster and source link. User-requested playback stalled for ten seconds gets a non-final recovery notice, cleared by actual playing/pause; no autoplay. Cross-origin iframe load cannot prove playable video, so its original-open fallback remains permanent.
- Editorial fidelity now takes priority over generic style. `content/EDITORIAL_PROMPT.md` integrates the anti-template research; `content/EDITORIAL_QA.md` records the authorized title/dek/body edits for all 13 current stories. Original/source/media/IDs/dates/tags stay locked; no imagined transcript, caption or scene description.
- `qa/mobile.html`, served only by the loopback preview at `/__qa/mobile`, loads actual same-origin pages in 320/390/768px iframes. It lives outside Cloudflare's `public/` assets. No viewport simulation or injected site CSS. New screenshots and actual playback remain a parent QA/release gate, not an executor claim.


## Brand and discovery refinement · 2026-11-06

Current direction: a restrained, carefully typeset reading journal. Retain the original olive/paper palette, source imagery, chronological story order and full article content. No network font dependency. The explicit request to improve the logo supersedes the former sans-serif masthead choice.

- Wordmark: a vector X with a separated crossing, Georgia News lettering, an olive terminal dot, and a Chinese descriptor separated by a fine vertical rule. The dot changes with the theme; the favicon shares the X silhouette. Brand and Latin author names have optical tracking; Chinese prose never has negative tracking.
- Hierarchy: distinct masthead / issue intro / discovery toolbar / article spread. Lead title is above its cover. Metadata is quieter than headlines, reading-time estimates replace repeated generic labels, and full titles remain visible. Text-only covers use stored author names and chronological numbers; these numbers are not ratings or issue numbers.
- Scan mode: native links in chronological order, with no large cover art. Archive opens in scan mode to serve a different task from the journal homepage. Search covers title, dek, author/handle and stored tags; terms combine with AND. Type filters distinguish stories with video from text/image stories, without implying a full transcript.
- Shareable state: `q`, `type`, `view` query parameters initialize discovery. Search/filter/layout changes replace the current list history entry; opening an article pushes one entry. Back/close restores the same filters, scroll and focused link; Forward reopens the article. Unknown parameter values fall back to defaults. No-JS pages retain all article links and omit nonfunctional search controls.
- Reading: native progress element reflects the active version, independent saved offsets survive switching, keyboard arrows move focus without moving the scroller, and Space activates the selected tab. Progress listeners and observers are disposed when the sheet closes/replaces its article.
- Dark mode: ink cards use a dedicated deep surface rather than reversing to bright white; text uses a separate contrast token. Input boundaries, selected controls and focus rings have distinct semantic tokens. Theme swaps suppress transitions.
- Detail: 1.5px line icons, aligned numeric counters, explicit hover/focus/pressed states, source image outlines and small squared corners. Motion respects reduced-motion preferences. Text sizes use rem; bars and control groups can wrap when text is enlarged. All original article JSON and RSS article bodies stay unchanged.
