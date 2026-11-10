# Markdown 统一渲染与排版 · 2026-11-07 (Asia/Shanghai)

用户截图对应 `clocktower-astra-detection` 的六列表格。源 JSON 是合法的多行 Markdown；旧改写渲染器不支持表格，将所有行并成了一个段落。基线改写 HTML 有 0 个 table，修复后有 1 个六列、五行数据的 table，原数值逐项不变。

- 所有改写/原文、独立文章、指纹阅读正文、标准 RSS 与 RSS v1 双版本统一使用现有固定版本的 markdown-it-py + nh3。原文基准 URL 仅负责相对地址解析，不再决定是否启用完整解析。支持表格/对齐、标题、嵌套列表、引用、围栏/缩进代码、行内代码、删除线及引用式链接；未引入浏览器端解析库或新依赖。
- 表格有表头层次、行间区分、数字等宽及局部横向滚动；桌面 Clocktower 表格宽度/内容均 672px。真实页面置于 320/390/768px iframe，首页及文章页面均无横向溢出；390px 表格宽 350px、内容 561px，键盘右移到 scrollLeft=211 可到末列。CaptureFlow 的五段代码保留空格/缩进，长行局部滚动。此为 Chrome 真实窄屏 CSS 验收，不是手机 Safari 实机验证。
- 媒体按解析后的完整段落定位，保留全篇引用定义及混合 HTML 容器。净化整个文档后，通过内部不可预测且最终移除的标记，结构化插入受控播放器/图片；不会用正文字符串替换或分片净化导致失真。标记无法消费时明确失败。按归一化锚点合并多图，保持原数组顺序。
- 安全回归涵盖危险 URL/HTML、title/alt 中字面标签、代码里的 HTML、净化后的稳定属性序列化、details 容器、畸形 HTML 吞标记和同段多媒体。来源 comments 不发布，原始脚本/事件不执行。
- 新增 15 项 Markdown 回归，覆盖截图原数据及网页/阅读正文/RSS 一致性。**完整 84 项通过：59 Python + 25 Node reader state**，记录在 `.qa-ui/markdown/tests.log`。官方解析/净化依据：[markdown-it-py](https://markdown-it-py.readthedocs.io/en/latest/using.html)、[nh3](https://nh3.readthedocs.io/en/latest/)。
- 已先合入 Grok Bot 最新内容提交 `b7c438e`；Anthropic 文稿及 15 张图的段落位置保留。本轮未修改 `content/articles/` 或 `src/media-manifest.json`。契约更新到 `content/SCHEMA.md`，RSS 协议仍为 v1。

**发布及线上回读（18:25–18:32 CST）：**源码/生成文件提交 `fa2781f86843` 已推送 GitHub 并执行 `npm run deploy`。正式 Nginx 发布头、服务器 current 均为 `fa2781f86843`，previous 保留 `b7c438ef3cba`。首页、索引、CSS、Clocktower/CaptureFlow/Anthropic 的独立文章与指纹正文、完整 RSS 共 10 个资源正常 HTTPS 回读且逐字节匹配。RSS 有 17 项，17 项均有 v1 双版本。证据 `.qa-ui/markdown/live-resources.json`。

正式 Chrome 从首页打开 Clocktower 阅读弹窗，改写与原文各有六列/六行（含表头）；版本切换、关闭返回、明暗主题均实测。截图 `.qa-ui/markdown/live-table.png`、`live-table-dark.png`。原主题已恢复。Umami property `31e0098c-6852-46b6-899c-11eed5ed16e1` 实时界面读回 18:30:01 的受控 `/__qa-markdown-20261107-fa2781f` 访问，入库已验证，证据 `umami-live.txt/png`。

**Grok Bot 同步（18:35–18:36 CST）：**已向负责内容的「乔布斯」发送本次发布 SHA 和 Markdown/媒体锚点/部署约定；观察到「已更新 例行任务」记录，18:36:11 回复确认原有「X News 海外发现更新」任务已同步。时间、选材、私聊交付保持；此次未新增任务、抓取、改稿或再次部署。

此次未创建临时 worktree；本地预览端口 33211 在交付前关闭。后续仅 QA 文档提交不改变已验收发布 `fa2781f86843`。

---

# Grok Bot 内容发布协作同步 · 2026-11-07 02:06 (Asia/Shanghai)

用户明确分工：Grok Bot 抓取和整理 X 内容，Codex 维护网站。已通过 Grok Bot 桌面应用向负责 X News 的「乔布斯」发送完整交接，并观察到「已更新 例行任务」记录及 02:05:56 的确认回复；不是仅写了待发送草稿。

- 原有「X News 海外发现更新」任务保持每日北京时间 08:00 前后 15 分钟、原选材要求，无重复新建。部署步骤已更新为：同步最新 main → 准备虚拟环境/requirements → 内容 JSON → npm test → 源内容和全部 public 一起 commit/push → 干净工作区 npm run deploy → 发布 SHA、首页、文章、read payload、RSS v1 双版本验收。Wrangler 只更新备用站、push 不等于上线已明确。
- **Grok Bot 回报，本站未独立进入其 Linux 环境执行：**工作目录 `/workspace/xnews`；既有 `qiaomu-hostinger` SSH 已成功连接；当前副本落后 15 个提交且无 `.venv`。后续执行必须先更新代码和安装固定依赖，不能直接从旧副本发布。当前内容试跑已接收新流程；本次同步没有新增或分享凭据。
- **本站独立复核：**正常 HTTPS 首页 200，Nginx，`X-XNews-Release=f52d330c8b27`，约 0.95 秒；SSH 读取 current 与 release 配置吻合。先前本机 curl 的 DNS 负缓存现已消退。
- 分工、无 SSH 时的提交交接和发布验收标准已写进 DEPLOYMENT.md，并推送 GitHub。当前任务仅同步流程和核验发布能力；Grok Bot 正在进行的内容试跑尚未完成本轮新稿上线，不能把任务配置确认当作新内容已发布。

---

# 首页与文章速度修复 · 2026-11-07 (Asia/Shanghai)

代码源提交 `1007d9ec74e147a870e86b235d62d3b246a2d499` 已推送 main。正式域名现为 DNS-only A → `76.13.103.27`，由已有 qiaomu-hostinger 的 Nginx 静态托管；公开 Cloudflare DoH 和 Hostinger/LA 的正常域名请求均确认新源。Worker `xnews` 保留为备用：`https://xnews.vista8.workers.dev`，版本 `31754947-3515-49f5-b5eb-a560fbc14b0b`。主站发布入口现为 `npm run deploy`，要求先提交测试后的生成文件，避免发布时重建使源码与产物失配。详见 DEPLOYMENT.md。

## 修复与证据

- 首页 CSS/JS 随文档交付，减少 2 次关键资源请求；无额外字体请求。首页文档 gzip 从 7,031 增至 20,204 字节（包含原本独立下载的代码），优化的是网络往返，不声称文档字节减少。
- 文章点击使用仅含正文的指纹化 `/read/` 文件，保留原文与改写、图片、视频、音频。Cursor 压缩负载 3,626→1,971 字节，CaptureFlow 10,494→8,869 字节。公开文章链接和 canonical 不变。阅读 payload 单独 noindex、不可变缓存，不含脚本。
- 低优先级预加载卡住时，点击最多等其 120ms，然后取消该请求并以高优先级请求正文，避免继承 8 秒预加载超时。停滞预加载回归测试约 137ms 完成；这不是线上所有文章的打开速度承诺。保持同时最多 2 个意图预加载、节流网络/省流量跳过、不预加载视频。
- **68 项通过：43 Python + 25 Node reader state。**日常筛选、返回焦点/滚动、原文切换、原始媒体和 RSS v1 协议仍受测试覆盖。生产内容未改写。`tests.log` 保存完整结果。
- **受控 Chrome 实验**：每个请求固定增加 700ms，两组首屏 FCP 为 1524→1004ms、1512→952ms；新版本没有外部 app CSS/JS 请求。证据 `browser-lab-runs.json`。这是实验室对照，不是用户群体 Core Web Vitals。
- **源站路由验证**：53 个已发布资源使用 HTTPS `--resolve` 逐字节匹配本地构建，另验真实 404/noindex/no-store、RSS MIME、压缩与缓存。源站本机客户端 3 次完整首页传输 0.956/1.301/1.042 秒；这些绕过 DNS 的数据不能冒充正常解析。旧线路同机请求曾 3.974 秒，另有 10–25 秒超时；网络有波动，不能把单样本差值当普遍提速比例。
- TLS 到期日 2027-02-04；Certbot 已切为 webroot，模拟续期通过，timer enabled/active，已有 Nginx reload hook。临时 DNS 凭据及过时配置键已删除。没有数据库、容器或应用进程变更。

## 正式客户端验收状态

01:50–01:52 CST：**正式 Chrome 验收通过**。首页显示 15 篇，无外部 app CSS/JS；搜索 CaptureFlow→打开正文→切换原文（1 个 table、5 个 pre）→返回，搜索值与卡片焦点恢复。Nginx 日志确认 Chrome 首页、指纹正文和 QA 404 请求均进入新源站，避免把浏览器旧缓存误当新线路。线上截图 `live-home.png`、`live-original.png`，结构化证据 `browser-live.json`。

**本次 Umami 入库已验证**：同一 property 的实时列表出现 `/__qa-speed-20261107-1007d9e`（01:50:47 CST），同时包含新首页与 CaptureFlow 访问。证据 `umami-live.txt/png`。保留旧 property 的显示名称「AI 大V电台」，未改历史数据。

`npm run deploy` 已真实执行，当前主站发布头为 `f52d330c8b27`，current 指向该 release，previous 为 `1007d9e`；两者 public 文件相同。最终源站 RSS、文章、正文、404 再次逐字节匹配。Certbot webroot 模拟续期已通过，临时 DNS 凭据清理完成。

**边界**：迁移时本地 DNS 曾缓存负响应。公共 Cloudflare/Google DoH、两台远端正常域名请求和本机 Chrome 已确认正常；最后一次本机 curl 仍被系统解析负缓存阻断，不把它算通过。浏览器 viewport 覆盖未实际生效（真实 DOM 仍为 1512px），因此名为 `live-mobile.png` 的尝试不是手机验收；本轮不声称新做了移动端或 Safari 实机验证。之前窄屏布局证据仍对应未改动的 CSS。临时 33208/33209/33210 预览服务已停止。

本轮只处理性能，保留既有设计、SEO/GEO、Umami property `31e0098c-6852-46b6-899c-11eed5ed16e1` 与站点入口；不新增 PWA、推广、支付或注册，不修改 RSS Reader 消费端。本次 Umami 新入库证据见上。完整原始记录位于忽略目录 `.qa-ui/speed-round2/`。未创建临时 worktree。

---

# 原文 README 排版与媒体核验 · 2026-11-06 (Asia/Shanghai)

在 `67bfaa3` 上修复 CaptureFlow 完整 README 被简化渲染器当作字面文本展示的问题，并核对 Cursor / 其他 X 视频地址。已发布；线上页面和 CaptureFlow RSS payload 已验证，完整 RSS 下载受网络限制。

- 为复杂来源增加可选 `original.markdown_base_url`；CaptureFlow 使用已保存的固定 GitHub commit。CommonMark + 表格解析后经 nh3 白名单净化，引用链接、嵌套列表、围栏代码、picture、表格、details 正常呈现；相对图片指向同一版本的 raw 文件，文档指向同一版本的 GitHub 页面。不改原文和中文改写内容。旧短帖维持原有渲染，三种输出（网站原文、标准 RSS、双版本 original.html）使用同一来源渲染器。依赖版本固定于 requirements.txt，按 README 在虚拟环境安装。
- RSS 双版本协议仍为 v1、字段不变；只更新 CaptureFlow 的原文 HTML（包含标准混合全文中的原文）。没有修改消费者代码或制造新转写。所有 15 篇的原文文字、中文正文和媒体 URL 与基线逐项比较一致；CaptureFlow 只新增渲染基准地址元数据。
- **媒体证据，约 21:16–21:23 CST：**四条 X 视频（Cursor/OpenAI/levelsio/tibo）的公开无 Referer Range 请求全部返回 `206`、`video/mp4`、1024 字节。带 `Referer: app://obsidian.md/` 的请求全部返回 `403`。Cursor 进一步分离变量：仅 `Origin: app://obsidian.md` 返回 `206`，仅 app Referer 返回 `403`；带本站 HTTPS Origin + Referer 同样 `403`。这证明此请求环境的 Referer 限制，不证明 URL 过期，也不能把未加载控件提示当作真实失败。现有地址保持不变，不引入代理。
- Cursor 全文件普通 GET 成功：1,513,678 字节，H.264 1280×720 + AAC，24.277333 秒；ffmpeg 完整解码无错误。SHA-256 `4b599c8c8536ba42cb83477cddc2213bc62f0df0da4a2e4ac7fd581e9d2f1ede`。网站 HTTP 头和 HTML meta 改为 `no-referrer`，以免外部视频请求携带本站 Referer；YouTube iframe 保留原有单独 referrerpolicy。
- **实际 Chrome 播放：**本地最终页面点击 Cursor 播放控件后，先读到 `currentTime=17.57714`、`readyState=4`、无错误，结束附近读到 `24.276238/24.277333`、`error=null`。证据 `.qa-ui/media-audit/cursor-browser-playback.json` 和 PNG。其他三条只验证了响应，不冒充实际播放测试。
- **验证：41 Python + 24 reader state = 65 项通过。**新增 5 项覆盖真实 README 结构、固定版本链接/图片、代码与嵌套列表、HTML/URL 净化、非法基准地址、页面 Referer 策略。Chrome 桌面实际看到 1 个表格、5 个代码块；390px 宽度页面 scrollWidth=390，长代码仅在代码块内部横向滚动。截图 `.qa-ui/media-audit/captureflow-desktop.png`、`captureflow-mobile.png`。未重复此前全站 39 项浏览器回归。
- 网络矩阵、原始响应头、视频取样与本机播放证据位于忽略目录 `.qa-ui/media-audit/`。原文安全处理依据 [markdown-it-py 安全文档](https://markdown-it-py.readthedocs.io/en/latest/security.html) 与 [nh3 API](https://nh3.readthedocs.io/en/latest/)。Nowledge Mem 续做检索因 localhost:14242 拒绝连接不可用，历史仅用于定位，本次结论以 Git、源文件、实际响应和浏览器为准。


发布记录（2026-11-06，Asia/Shanghai）：源提交 **`d909a82a025878b265f4d1832edb4587d221bc91`** 已推送 origin/main；Cloudflare Worker 版本 **`6cb9cfcb-403d-434b-a4cb-f3933e0190e9`**。正式 CaptureFlow/Cursor 两篇页面及新 CSS `/static/app.7ac82213fe25.css` 均回读并与本地文件逐字节一致，HTTP `Referrer-Policy: no-referrer` 正确。证据 `.qa-ui/media-audit/live-verification.json`。

RSS 终端两次有限请求均为 TLS 握手超时；Chrome 访问正式 `/feed.xml` 后能读取新 XML，提取出的 **完整 CaptureFlow `qiaomu:versions` JSON 与本地已发布对象完全一致**，确认原文包含真实 `<table>`、`<pre><code>`，不再出现转义的 `<picture>` 或引用定义字面文本，协议仍 v1。证据 `.qa-ui/media-audit/live-rss-browser.json` 含完整 payload 和比较结果。浏览器最后一次观察只载入 13 条且等待完整加载超时，因此**不声称本轮全部 15 条线上 feed 字节核验通过**；本地完整 15 条测试通过。阅读器可以重新同步 CaptureFlow 后验收新 HTML，本站没有修改其数据或代码。


消费端联调补证（2026-11-06，来源：RSS Reader 协调会话 `01a1b000-6035-7fa1-b646-4922a9526bea` 的验收回报，本会话未重复调用其 API）：主动刷新 RSS source 后，公开 `/api/entry/9a4a403830f1e9299441283ed7652940` 返回 CaptureFlow 原文 `content` 13,317 字符、1 个 table、5 个 pre，无混合的「乔木改写」标题；独立 `rewriteHtml` 为 7,445 字符。该消费端回读确认新排版已沿 RSS 链路送达，补足本站终端完整 feed 回读受网络限制时的交付证据。用户实际 Obsidian 文章的刷新显示仍由该会话继续验收，不能把 API 到达等同于其界面已完成刷新。

未创建临时 worktree。验证用的本机 33207 预览服务在交付前停止。

---

# RSS 双版本与嵌入媒体 · 2026-11-06 (Asia/Shanghai)

本次在主干 `2ef6797`（保留 PR #1 的性能、SEO 和 GEO 改动）上，为 RSS Reader 增加已发布原文/乔木改写的独立输出。已部署并完成线上 RSS 验证。

- 协议：`xmlns:qiaomu="https://qiaomu.ai/ns/rss/1.0"`；每条 `qiaomu:versions` 是 CDATA JSON，精确结构为 `{version:1, original:{title,url,lang,html}, rewrite:{title,markdown,html}}`，所有叶字段均为字符串。完整约定见 `content/SCHEMA.md`。
- 原文 HTML 只包含保存的原文文字、原文媒体、来源/相关链接和完整性说明；缺失文字明确提示，不用中文改写回填。改写 HTML 复用已发布渲染器与媒体位置/遗漏规则；Markdown 保留正文及对应媒体链接/图片。视频/音频使用原生 controls、preload=none，视频保留 poster；YouTube 使用 privacy-enhanced iframe，所有媒体带原始链接兜底，不生成转写。
- 测试先复现旧协议缺字段的问题，再通过：**36 Python + 24 reader state = 60 项**。新增 7 项回归覆盖实际全部 15 篇文章的隔离、精确字段、缺失/摘录提示、图片/视频/X 视频/音频/YouTube/未知类型、段落位置、遗漏说明及 JSON/CDATA/Markdown 转义。
- 独立兼容性比较：与修改前保存的 feed 对比，全部 15 条旧 RSS item 的每个标准字段、属性和完整 HTML 逐一相同。仅增加命名空间、版本字段并更新频道构建时间。未修改文章 JSON、网页、媒体文件、CSS/JS、SEO 或缓存策略。原始证据位于忽略目录 `.qa-ui/rss-versions/legacy-feed.xml` 与 `local-contract.json`。
- 验证边界：本次是 RSS 传输格式改动；浏览器界面未变化，未重复视觉回归。HTML 内嵌媒体标签与属性已验证；第三方媒体真实播放、外站净化后的显示及阅读器历史记录修复由消费端另行验收。


发布证据（2026-11-06 17:10–17:11 Asia/Shanghai）：

- 发布源提交：`97e346bf434b65dec724a91dba67731f1ae0d5a1`，已推送 `origin/main`；Cloudflare Worker `xnews` 版本：`dbcf9bbf-6647-4b39-bf61-95017293c4ce`。使用既有 OAuth：`env -u CLOUDFLARE_API_TOKEN wrangler deploy`；本次只上传一个修改的静态文件 `/feed.xml`。
- 正式 `https://xnews.qiaomu.ai/feed.xml` 与带 `?versions=97e346b` 的请求均成功，响应与提交的本地 feed 字节完全相同。SHA-256：`79e249e6056d486a88e4824619018470dc3b0a44c13f319e51562faac1daef43`。两次线上解析均确认 15 条、version=1、original 四字段和 rewrite 三字段（含必需 html）。HTTP 头、完整 feed 与校验记录分别保存于 `.qa-ui/rss-versions/live*-headers.txt`、`live*-feed.xml`、`live*-contract.json`。
- 消费端联调样例：DeepSeek 条目的完整实际 JSON 位于 `.qa-ui/rss-versions/example-deepseek.json`（从与线上一致的 feed 提取）；原文标题 `DeepSeek Super Agent and why the harness matters`，来源 `https://www.youtube.com/watch?v=OrcsMi2-IcM`，两份 HTML 均含 `https://www.youtube-nocookie.com/embed/OrcsMi2-IcM`，原文保留「视频原文摘录，非完整逐字稿」提示。协议与联调约定一致，没有额外字段或后续 AI 改写。
- 本会话未创建临时 worktree；只使用主工作区 `/Users/joe/Documents/ChatGPT/qiaomu-xnews` 的 `main`。

---

# Performance and search release · 2026-11-06 (Asia/Shanghai)

Scope explicitly requested: optimize and publish **xnews.qiaomu.ai** loading speed, SEO and GEO; separately register its RSS in 乔木精选. Coordinated with the UI release chat and started editing only after it became idle and the checkout was clean at `4ed2ec3` (UI/content base `ddff8be`, 15 articles).

## Changes and evidence

- Fingerprinted CSS/JS under `/static/` and content-addressed media use one-year immutable browser caching. HTML uses short freshness windows (home/archive 60 seconds, articles 300 seconds); RSS 300 seconds. Old `/app.css` and `/app.js` remain for compatibility. Keep older fingerprinted assets while old HTML may still reference them.
- Hover/keyboard intent prefetches at most two same-origin article requests concurrently and shares the response with the reader. No bulk article or media preloading; save-data/2G skip speculative requests. Failed/mismatched responses never enter the cache; explicit reading still works.
- Build generates `robots.txt`, an 18-URL canonical sitemap (15 articles + home/archive/about), Article/WebPage/WebSite/publisher JSON-LD, article source references and sharing images. 404 is noindex with no misleading canonical. No invented `lastmod` or modification timestamps. Publisher/original-author roles and date meaning are visible in the article/about page; original content and media are unchanged.
- Before: public robots/sitemap returned 404; CSS/JS used `max-age=0, must-revalidate`. Terminal sample TTFB: home 0.517s, article 0.760s; browser observed ~1.54s CSS/JS fetches and a reader still loading after 5 seconds. Browser before runs did not yield a stable aggregate; they must not be presented as field Core Web Vitals.
- Controlled Chrome comparison (600ms added article latency, 850ms hover lead, 3 runs each): baseline click-to-article 824/817/826ms; intent prefetch 34/35/41ms. This isolates the prefetch benefit, not a population-wide speed claim. `.qa-ui/speed-seo/performance-lab.json` contains raw results.
- Verification: 29 Python + 24 reader state tests passed; 39 real Chrome checks passed on identical candidate sources, including desktop/mobile layout and accessibility. Desktop reader screenshot inspected. Original `content/` and `articles.json` unchanged. Wrangler dry run passed.

## Search documentation checked

Reviewed 2026-11-06: [Cloudflare asset headers](https://developers.cloudflare.com/workers/static-assets/headers/), [Google Article markup](https://developers.google.com/search/docs/appearance/structured-data/article), [Google AI search foundations](https://developers.google.com/search/docs/appearance/ai-features), [OpenAI crawler distinctions](https://developers.openai.com/api/docs/bots). Scope is live/code/rendered inventory of this small site; no Search Console property, indexing, rankings, real-user performance distributions or AI citations were available. Sitemap publication and valid markup are not evidence of search-engine processing. Search/AI citation outcomes require later platform data; do not fabricate a universal GEO score.

Published code `c4b889730693e6d6ae35f1f3bd7487f8e67526d4` as Cloudflare Worker version **`3a041cd7-1201-4179-ba5c-806019d0b056`**, 2026-11-06 around 16:49 Asia/Shanghai. Source review: [PR #1](https://github.com/joeseesun/xnews/pull/1). Used the documented OAuth deployment command `env -u CLOUDFLARE_API_TOKEN wrangler deploy`.

Final live HTTP verification: across the bounded runs, **23 unique routes matched local bytes exactly** (all 18 indexable HTML pages, RSS, robots, sitemap, CSS and JS). `public/_headers` is deployment configuration, not a public route. Fingerprinted assets returned one-year immutable caching; home/article returned their configured short TTLs; an unknown path returned genuine HTTP 404 with noindex. Raw evidence: `.qa-ui/production-speed-seo.json`, `.qa-ui/live-inventory.json`, and saved responses. The sitemap timed out in the later batch but had already matched in the earlier batch; never treat a timeout as a passing request. LA server normal curl independently returned the expected homepage and cache headers. Python urllib from that server returned 403; this alone does not establish that named verified search crawlers are blocked.

**Verification limits:** production browser navigation remained intermittently stuck before HTML arrived (empty title, zero cards/scripts, only the document request pending), and local curl also intermittently timed out. No stable post-release cold-load aggregate or successful post-release live browser walkthrough was obtained. Local Chrome checks on the identical deployed sources passed (39); screenshots of desktop and 320px reader were inspected. Cache/prefetch gains are implemented and headers are live, but this release does not claim to fix every geographic network path or prove field Core Web Vitals. Recheck cold navigation and repeat-view resource transfer sizes on a stable connection; then observe actual traffic/search data over 7–14 days before attributing any outcome to this change.

Umami retains exactly one unchanged script/property on every page; preceding UI release ingestion was independently verified earlier the same day (record below). This follow-up did not obtain a new ingestion event because browser navigation failed, so ingestion is not newly re-certified. No network/privacy settings or access controls were changed.

RSS integration in the separate reader is verified live: `xnews` enabled, optIn false, autoRewrite false, status ok, **15 entries**. Rollback baseline: Cloudflare Worker version `2d8c75ee-d16b-46cd-bbfe-d39da9236a2b`. No temporary worktree created.

---

# Production release · 2026-11-06

User authorized publication with “上线啊”. Release baseline: `801d1918e00d3ddba9865793e0b144d4daa524a6`; remote main matched before staging. This release includes the completed brand/interaction refinement below, the explicit Cloudflare account ID verified against the qiaomu.ai zone, and restoration of the domain’s existing Umami property `31e0098c-6852-46b6-899c-11eed5ed16e1`.

Umami is restricted to `xnews.qiaomu.ai`; search/query strings and fragments are excluded, so typing filters and switching versions do not generate duplicate pageviews or transmit search terms. Local preview traffic is excluded. All generated HTML pages have exactly one validated tracking script. The existing dashboard label still reads “AI 大V电台”; its configured domain is xnews.qiaomu.ai and no property, ownership or stored data was changed.

Release regression: **26 Python + 21 DOM/state tests passed**. The 39 Chrome checks and visual QA from the preceding implementation remain recorded below. Publishing uses the existing Wrangler OAuth identity: the shell API token is valid for the domain but lacks Worker access and must not shadow OAuth (`env -u CLOUDFLARE_API_TOKEN wrangler deploy`). No credentials are committed.

During publication, remote main advanced to `71944ac` with CaptureFlow and checkwash articles, source licences and a media asset. That commit was merged intact; only conflicting generated home/archive/RSS files were regenerated from the combined sources. The final corpus is **15 articles**, and all 47 regression tests passed again. Discovery tests now derive the article count from the content index rather than assuming 13. The initial 13-article upload (`46b917e0-768b-4583-8acb-ba3a11323d6c`) is superseded by the integrated release recorded below. Final deployment: **`2d8c75ee-d16b-46cd-bbfe-d39da9236a2b`**, source **`ddff8be`**, published to **https://xnews.qiaomu.ai/**. Main was pushed successfully after integrating `71944ac`. Production Chrome verification passed: 15-article homepage, search, CaptureFlow reader, original-version switch, return preserving query/focus, and reset.

**Umami ingestion verified:** the real-browser QA visit to the intentional 404 path `/__qa-release-20261106-ddff8be` appeared in this exact property at **2026-11-06 16:43:53 Asia/Shanghai**, alongside homepage and article visits. Search terms/fragments were absent as configured. Local screenshots: `.qa-ui/production-live-ddff8be.png`, `.qa-ui/umami-release-ddff8be.png`. Structured evidence: `qa/production-release.json`.

**Verification limit:** bulk terminal HTTP comparison could not finish: urllib returned 403/connection closures and curl timed out. Do not interpret this as a successful byte-for-byte public-asset comparison, or conflate it with the successful real Chrome site/interaction checks. No production routing or security policy was weakened. Safari/iOS, screen-reader and actual media playback remain unverified.

**Next-chat handoff:** this checkout is ready for the separately authorized speed/SEO/GEO work after the documentation commit. Use the final remote main as the base, preserve both newly merged stories, and use `env -u CLOUDFLARE_API_TOKEN wrangler deploy` with the existing OAuth at `/Users/joe/Library/Preferences/.wrangler/config/default.toml`. The inherited shell token is DNS-scoped and shadows the working OAuth; do not copy tokens into files. No temporary worktree was created. Temporary speed candidates from another chat were not included. All earlier “local only” statements below describe the pre-release stage.

---

# Local brand and interaction refinement · 2026-11-06 (Asia/Shanghai)

Current scope: the homepage → search/filter → full article → original/rewrite → return flow, archive scan mode, and shared header/theme. Stack remains Python-generated static HTML, plain CSS and vanilla JS. Conventions inspected: `DESIGN.md`, `README.md`, `QA.md`, source schema and existing tests; no repository AGENTS.md or CLAUDE.md was present. Earlier handoffs below are historical and do not authorize a release in this chat.

## Completed outcome

- Original geometric X mark + serif News wordmark + matching favicon; consistent masthead spacing and quieter metadata. Reused the existing paper/olive palette and system fonts.
- Lead headline precedes its cover; desktop opening spread stays asymmetric, later rows have three equal columns. Visible 1440px lead title moved from roughly 940px down the old page to 484px in the new page. All real titles, source images and chronological ordering remain intact.
- Search, text/video filters, URL-backed state, recoverable empty state and a text-only scan mode. Archive defaults to scan mode. Mobile keeps the archive navigation entry visible.
- Approximate Chinese reading time (excludes video duration); per-version reading progress; keyboard Space activation; arrow focus preserves scroll. Close/Back/Forward preserve query, layout, focus and reading positions.
- Rem typography, wrapping controls, image outlines, deliberate light/dark contrast surfaces, reduced-motion handling and instantaneous theme swaps.

## Interface coverage

| Domain | Evidence inspected | Result |
| --- | --- | --- |
| Accessibility | `src/site.js`, native buttons/links/progress, keyboard article flow, axe audits on desktop light/dark, article, 320px home/reader | No automated WCAG violations in five inspected states; VoiceOver not verified |
| Layout | `src/site.css`, actual Chrome screenshots and geometry at 320/390/768/1440/1920px, equivalent 200% zoom viewport, 200% root font size | No tested page/reader horizontal overflow; native browser zoom and RTL mirror not verified |
| Writing | `scripts/build.py` discovery/reader copy, empty/loading/error/retry states, source/kind labels | Actions and recovery paths explicit; duplicate X Article label removed; editorial JSON unchanged |
| Typography | Wordmark, cover author names, headlines, prose and metadata in `src/site.css` | Chinese tracking preserved; Latin optical tracking scoped; rem text sizes and numeric alignment |
| Colors | Source tokens, actual rendered light/dark screenshots and axe contrast checks | Primary text 16.84:1 light / 13.70:1 dark; secondary 5.71:1 / 8.45:1; input boundaries 3.73:1 / 5.00:1 |
| UI polish | SVG mark/icons, image outlines, selected controls, hover/focus styles, reduced motion and theme switch | Consistent states in inspected views; no native Safari/real touch-device verification |

## Resolved findings and design changes

| Severity | Domain | Location | Before | After | Why |
| --- | --- | --- | --- | --- | --- |
| HIGH | Accessibility | `src/site.js:237` | Tab anchors had manual ARIA roles but Space did not activate them | Space activates the focused version; arrow keys use preventScroll focus | Complete the expected keyboard tab interaction and preserve reading context |
| MEDIUM | Layout | `scripts/build.py:433`; `src/site.css:88` | Oversized opening cover pushed its title near the bottom of the first desktop screen | Title-first opening story, shorter cover, single-row span | Readers can identify the lead story immediately |
| MEDIUM | Layout | `src/site.css:250` | Archive entry disappeared on mobile | Visible archive entry with wrapping header | Preserve the same navigation path across widths |
| MEDIUM | Typography | `src/site.css:20`; `src/site.css:174` | Fixed pixel typography and fixed-height bar | Rem typography and a flexible, wrapping reader bar | Respect text enlargement without losing controls |
| LOW | Writing | `scripts/build.py:467` | Repeated “X Article” source/type label | Single source/type description | Reduce redundant metadata |

The new wordmark, discovery tools and darker card surfaces are requested product improvements, not retroactive claims that the prior aesthetic was inherently wrong.

## Verification and reproduction

- `npm test`: **25 Python tests + 21 reader DOM/state tests passed**. Covers all 13 static article routes, full Chinese/original/media RSS, source locks, no-JS structure, retry/races, history/focus and the new discovery behavior.
- `XNEWS_BROWSER_CHANNEL=chrome npm run test:browser`: **39 real Chrome checks passed** on Chrome 157. Tests start/stop their own loopback server. Includes combined filters, reset/focus, theme persistence, separate reading offsets, Escape/Forward, progress to 100%, responsive geometry, archive default, fetch-failure retry and no-JS fallback.
- Browser evidence: `.qa-ui/verification.json`, `.qa-ui/accessibility.json` and `.qa-ui/*.png`; generated locally and gitignored, never deployed. Screenshots were visually inspected for desktop light/dark, mobile, scan mode and the 320px reader.
- `node --check src/site.js`, `python3 -m py_compile scripts/build.py`, `git diff --check` passed. `content/` and `public/articles.json` have no diff. RSS article contents are unchanged; only the build timestamp is regenerated.
- Color ratios above were calculated using WCAG relative luminance from the declared opaque token pairs; automated browser contrast checks supplement those calculations.
- Not verified: VoiceOver, Safari/iOS native behavior, RTL, native browser-chrome zoom, external video/audio playback. Browser UI tests block off-origin requests; this is not a playback validation. No production deployment or remote push was performed.

Verdict: **Approve for the inspected local homepage/archive/reader surfaces.** Unverified assistive-technology/platform behavior remains explicitly outside that verdict. Local preview: `npm run preview -- --port 33205`. Changes are in the main checkout `/Users/joe/Documents/ChatGPT/qiaomu-xnews`; no temporary worktree or task branch was created.

---

# D 影像刊 · latest refinement handoff

## Accepted release gate (2026-11-06, 中国标准时间)

- Actual site, same port as previous QA: **http://127.0.0.1:33205/**
- **Local-only mobile fixture: http://127.0.0.1:33205/__qa/mobile**
- Fixture file: `qa/mobile.html`, outside deployed `public/`. It uses six genuine iframes: homepage + article at 320, 390, 768px. Article selector switches between Amjad long article, DeepSeek original, Cursor rewrite video, Karpathy rewrite image and Levelsio portrait video. Each frame is unscaled, loads the actual same-origin route and site CSS/JS, and scrolls independently. Optional overflow readout measures its real DOM; it is not an automated screenshot or a mobile device test. Test browser history on the normal top-level page, not joint iframe history.
- Server restarted on the **same 33205 port** for the local fixture route; refresh old pages. New live route returned HTTP 200. The fixture route exists only in `scripts/preview.py`; Cloudflare assets remain `directory = "public"`.
- **Parent final browser QA accepted release at 08:49 中国标准时间.** Desktop 1920×1113 and actual homepage + Cursor article iframes at 320/390/768px passed: no overflow, true local source images loaded, tabs/source/return accessible. The executor also read the supplied desktop screenshot; it did not perform an independent browser run.
- **Explicit playback limitation:** manual browser playback was attempted, but `video.twimg.com` returned HTTP 403. The unavailable message and original-source fallback worked. This is NOT playback success. The 403 will not be bypassed; videos stay external and all Chinese/original media retain source fallback.
- Accepted desktop screenshot (local evidence, not uploaded to the repository): `/cursor/stores/user/grok-bot/agents/788adcbb-338e-4d41-a21e-0b95169edd01/assets/5e991953af660a352c6f1a633b2b0401f64333344942b4e0ac897e828076edc9.png`.
- Source publication and Worker `xnews` deployment are explicitly authorized. This document records the accepted pre-publication checks; actual commit/version/live verification is reported after release.

## Public media investigation

Normal unauthenticated curl only: no browser automation, cookies, tokens, alternate blocked endpoint or access-control circumvention. All seven stored image/poster URLs returned HTTP 200 `image/jpeg`, then passed image decoding/format verification. Original bytes were copied unchanged; no generated replacement news imagery or screenshot substitute. Total **339920 bytes (~332 KiB)**, largest 107280 bytes. Provenance, original HTTPS URLs, dimensions and SHA-256 live in `src/media-manifest.json`; raw read-only investigation scratch is ignored at `.media-qa/`.

| Local rendering asset | Dimensions | Bytes | Upstream result |
|---|---:|---:|---|
| `/media/karpathy-hackertube-image-cca841bfb0.jpg` | 1200 × 697 | 107280 | 200 image/jpeg |
| `/media/levelsio-300-month-expenses-image-6e1d7a11c2.jpg` | 1199 × 592 | 43818 | 200 image/jpeg |
| `/media/levelsio-bf1942-web-poster-fdbc2233d7.jpg` | 675 × 1200 | 64351 | 200 image/jpeg |
| `/media/deepseek-super-agent-harness-poster-32294b3993.jpg` | 640 × 480 | 43712 | 200 image/jpeg |
| `/media/cursor-live-apps-poster-d4045da567.jpg` | 1200 × 675 | 21347 | 200 image/jpeg |
| `/media/openai-gpt6-cyber-poster-d795be1590.jpg` | 1200 × 675 | 47191 | 200 image/jpeg |
| `/media/tibo-dropbox-launch-video-poster-839d50e043.jpg` | 480 × 360 | 12221 | 200 image/jpeg |

- All four native video source URLs (Cursor, OpenAI, Levelsio BF1942, Tibo) accepted a bounded normal `Range: bytes=0-0` GET: HTTP 206 `video/mp4`, one byte each. Cursor advertised 1513678 total bytes. No full video was downloaded or bundled.
- The public `youtube-nocookie.com/embed/OrcsMi2-IcM` HEAD returned HTTP 200 `text/html`. **This only checks an HTTP response, not playback, embedding success or browser reachability.**
- Earlier curl availability does not establish browser playback: final manual browser video requests returned HTTP 403. No access-control bypass or retry through another endpoint was attempted. Local images remove that external image hop. Videos remain external with visible original-open fallback, no autoplay, `preload=none` for native media, and honest error/buffering recovery. Cross-origin iframe loading cannot reliably establish player state; no false claim that a loaded iframe equals playable video.

## Layout, metadata and media behavior

- Text-card type-cover minimum 125→90px, compact card gaps/padding, regular title cap 27→23px / featured 38→34px. Text cards size to content instead of stretching; card footer no longer pushes to the bottom of a blank flexible body. Featured cover can absorb residual height while its text stays naturally sized; mobile restores fixed aspect-ratio sizing.
- Primary nav 14→15px desktop / 14px mobile; card dates/authors and article metadata 12→14px. Source actions, source footer, recovery labels and captions enlarged; narrow low-priority actions stay at 13px. Full titles/content are retained.
- Real images and native posters use durable `/media/...` URLs **only in HTML rendering**. Original media objects remain exact, including URL/poster/alt, and RSS uses upstream URLs, never relative `/media/` paths.
- On native media error the player is hidden, its true cached poster is available, the accurate cannot-play message and source link remain. After a user play request stalls for ten seconds, a conditional recovery message appears without claiming permanent failure; playing/pause clears it. No timer is armed by an idle unopened player.

## User-added multimodal and editorial requirements

- Reusable project prompt: **`content/EDITORIAL_PROMPT.md`**; stable byte-for-byte reviewed addon: **`content/EDITORIAL_ADDON.md`**. Schema: `content/SCHEMA.md`. Both instruct full-text/media coverage, stable source media IDs, ordered references, precise placement only when supported, a labeled source-media block otherwise, explicit omissions, no fabricated transcript/caption, no autoplay, full RSS and acceptance tests.
- Backfilled all 13 articles with `rewrite_media`: **7 source attachments included, 0 omitted; 6 media-free stories remain empty.** Existing original/source objects were not changed. Unknown placement remains `after_body` + `source_metadata_only`, not invented semantic precision. UI rewrite and RSS Chinese sections share one renderer/plan; source media is deduplicated within each section. Both tabs now pause/unload on hide/close.
- Integrated the provided anti-AI editorial addon into the prompt, above generic style templates. **Audited all 13 against stored originals and changed only the authorized Chinese `title/dek/body_md`.** Restored full Amjad/Victor long-form evidence and limits rather than turning them into summaries. Complete per-article coverage/corrections and the checked Sarah sample are in **`content/EDITORIAL_QA.md`**. Research files remain unmodified.
- DeepSeek: removed invented 30-task count, fixed podcast/interview attribution, fixed “enabled = 30% fewer” comparison base, restored prototype/non-official status, 17.5× range, 6.4→1.6s, worker/mode/benchmark/security limits. Levelsio: fixed annual service denominators vs monthly costs, Photo AI exclusion, all six savings entries and missing Sume/.io values. Sarah uses only the checked proposed title/dek/body. Removed editor-added fake contrasts, questions and grand endings throughout.
- **Evidence gap, not external disproof:** Anthropic/OpenAI/Cursor/Vercel/Schedules contained detailed additions not supported by the stored short source text. Those were removed rather than assumed true from a `related_url`; we did not reopen/retain the full linked articles in this round. Current Chinese fully covers the saved announcement, not an unseen article/transcript.
- Unchanged protected fields: `id/date/published_at/tags/source/original`, deep-compared to the pre-round snapshots and locked by SHA-256 in `qa/editorial-source-lock.json`. All seven media IDs/reference order/evidence levels stay intact through the subsequent copy edit. Generated index titles/deks and RSS Chinese text intentionally update to the corrected fields.
- Remaining metadata flag: Victor's existing `source.title_en` says ARR while stored original says annualized gross revenue. Chinese is corrected to 年化总收入; source metadata was not silently changed. Parent can decide a separate metadata correction.

## Passed checks (non-visual)

- `npm test`: current build of 13 articles, **25 Python source/static/RSS/editorial/HTTP tests + 17 reader DOM/state/parser tests = 42 passed**.
- JS syntax for source/generated assets; Python compilation; `git diff --check` pass.
- Real HTTP fixture and all thirteen clean article routes return 200; seven JPEGs return 200 with matching bytes / correct content type. Unknown local route remains 404. Fixture exclusion from public assets checked.
- Full Chinese and stored original texts, stable links/GUIDs, media URLs and fallbacks verified in RSS; native audio and semantic paragraph placement covered by explicitly synthetic unit fixtures (there is no invented audio article in the deployed content).
- Coverage, duplicate/unknown/missing references, explicit omission, unique paragraph anchors and ordered same-anchor media tests pass. Hash tests preserve original/source/media/IDs/dates. Reader history, independent scroll, focus, hidden iframe unloading and rewrite/original native pause pass with new media in both tabs. Native stalled/error recovery is tested as DOM state, not real playback.

## Accepted scope and publication checks

1. Parent completed the requested final desktop and actual narrow-iframe checks above; no further browser QA is requested as a release prerequisite.
2. Keep the explicit video HTTP 403 / no-success limitation, no autoplay, source fallback and no-bypass policy.
3. Run the full tests/build and original/source/ID/tag/date preservation checks, then one cohesive normal commit/push to `joeseesun/xnews` main and deploy the existing Worker `xnews`.
4. Verify the live homepage, stable article routes, actual local JPEG asset, corrected Sarah sample and valid full Chinese/original/media RSS. Verify `/__qa/mobile` is not publicly deployed. Do not make unrelated editorial, DNS or routing changes.
5. Original curl response checks and the 08:44 pre-release verification snapshot remain historical network/static evidence, not claims of browser playback.

## This round's files

Exact source/support/media paths (including all 13 content JSONs and seven local JPEGs) are listed in `qa/refinement-manifest.txt`. New support files: prompt, editorial ledger, media manifest, local fixture, source lock, HTTP/editorial tests. Changed sources: build/preview, CSS/JS, build/reader tests, schema, README, DESIGN, QA, ignore rules. Generated current output: homepage/archive/articles, app CSS/JS, full RSS and article index; other existing static output regenerated normally. Pre-existing dirty Phase-3 implementation and `design-previews/` were retained; no reset/stash/rebase/remote writes.

---

# Historical initial implementation handoff (superseded where the latest round differs)


## Preview / release gate

- Local implementation: http://127.0.0.1:33205/
- Long article: http://127.0.0.1:33205/a/amasad-managed-cloud-agents
- Original deep link: http://127.0.0.1:33205/a/deepseek-super-agent-harness#original
- Restart: `npm run preview -- --port 0` prints a new local URL. Current preview is a read-only Python static server with clean-route support; production still uses existing Cloudflare assets configuration.
- **Pending parent visual pass. No browser automation, screenshots, visual verification, production deploy, git commit or push was performed by this executor.**

## Implemented

Selected D anchor is `.dir-d` in the existing four-direction preview; design decisions are in `DESIGN.md`. Bright paper, high-contrast media/type composition, asymmetric responsive grid, no sidebar, quiet RSS/Archive/About chrome, persisted optional dark mode. Covers use stored source media/posters, never generated news imagery or mock headlines. The actual stored titles are used, including the correct Levelsio website-cost title (not the old preview's “生活成本”).

Cards remain real `/a/<id>` anchors. JS progressively opens full HTML in a full-viewport dialog; modified clicks and standalone routes remain native. Browser Back/Forward and Close/Escape return to the list's recorded scroll/focus. Request cancellation, stale-response guards, loading/error/retry, standalone fallback and original link are present. Tabs are accessible manual-activation controls with deep-link fragments and separate saved positions. Without JS both complete bodies and semantic section links remain in the document. Hidden/closing media is paused; iframe sources are unloaded and restored without autoplay. Lazy media has original-link recovery. DeepSeek's saved video text is explicitly an excerpt, not a complete transcript, in the reader and RSS.

## Concurrent routine / preservation

At task start only `design-previews/` was untracked. During implementation the daily routine landed commit `3008be3` and added five stories (Cursor Apps, GPT-6 Cyber, Anthropic vault, Tibo video, Rauch Schedules), bringing the current total to **13**. No reset, checkout, stash, rebase or content rewrite was used. Builds always loaded current filesystem content. All eight pre-existing content JSON SHA-256 values stayed identical; `git diff --exit-code -- content/articles public/articles.json` passed against the fresh daily HEAD.

Important integration detail: the daily routine ran while the presentation generator was being changed. Current HEAD already contains regenerated home/archive and five new article pages using the D templates; these therefore do not all appear as dirty files now. Do not interpret their absence from `git diff` as missing D work, and do not roll back the routine's fresh content. Review the whole current generated site before the later cohesive commit/deploy. This executor made no remote changes.

Every old RSS item's title, link, GUID, publication date, author, rewrite, stored original and media is preserved exactly; the only per-item addition is the explicit DeepSeek availability note. Full RSS tests cover all 13 current stories. Feed build time is regenerated normally. No content JSON, article IDs, URLs or source/related links were deliberately altered.

## Passed checks (non-visual)

- `npm test`: build of 13 stories; **11 Python build/content/RSS/static tests + 14 DOM/state/parser tests** passed.
- `node --check src/site.js` / generated JS; Python compilation passed.
- Actual local HTTP smoke: `/`, `/archive`, `/about`, CSS, JS, RSS, articles JSON and all 13 clean `/a/id` routes returned 200. Unknown article returned custom 404.
- HTML5 parse of all generated HTML: no parse errors. CSS syntax parsed without runtime stylesheet errors.
- State tests cover real-link interception, original/rewrite independent offsets, tab/permalink hash, Back/Forward, close/focus restoration, cache, Escape/focus loop, modified clicks, error/retry, aborted late responses, media errors/pause/unload, direct hash routes, blocked storage, wrong-article rejection and missing native-dialog fallback.
- Source CSS/JS equal their generated assets, so subsequent routine builds retain D instead of reverting it. RSS handles CDATA/ampersands and image/video/audio paths. Responsive/reduced-motion CSS checks passed. None of this is claimed as visual/layout geometry verification.

## Parent visual checklist / blocking release gate

1. Desktop 1440 and 1920: lead title visible early, intentional media emphasis, no awkward grid holes/huge stretches, full stored titles, correct chronological keyboard order.
2. Mobile 320/390 and tablet 768: masthead/nav wrapping, single-column cards, no horizontal page overflow, touch targets, reader bars/tabs and source actions fit.
3. Open Amjad's long article from mid-list; read/scroll both panels, switch repeatedly, close/Escape/Back; confirm list scroll/focus. Forward should restore the reader. Test browser refresh/direct URL and independent page link with `#original`.
4. Light and dark: contrast, selected tabs, text-cover colors, image captions. Disable JS and open direct article URLs; both complete sections and source links must remain usable.
5. Actual media: manual-only video/audio, portrait media proportions, Youtube load, failed network/image fallback, no playback continuing behind a hidden panel/closed reader. Check Safari/mobile scroll lock and native dialog focus with real browser behavior.
6. If needed refine only a few high-impact visual issues, then rerun `npm test`. Deploy/push only after this parent visual pass. No claim is made that production currently reflects these local changes.

## Exact worktree file manifest

Tracked files currently changed relative to the concurrent daily HEAD:
- `.gitignore`
- `package.json`
- `public/404.html`
- `public/a/amasad-managed-cloud-agents.html`
- `public/a/deepseek-super-agent-harness.html`
- `public/a/karpathy-hackertube.html`
- `public/a/levelsio-300-month-expenses.html`
- `public/a/levelsio-bf1942-web.html`
- `public/a/rauchg-vercel-security-review.html`
- `public/a/sarah-guo-personal-software.html`
- `public/a/victor-slash-supersmb.html`
- `public/about.html`
- `public/app.css`
- `public/app.js`
- `public/feed.xml`
- `scripts/build.py`

New implementation/support files:
- `DESIGN.md`
- `QA.md`
- `package-lock.json`
- `scripts/preview.py`
- `src/site.css`
- `src/site.js`
- `tests/test_build.py`
- `tests/reader-state.test.cjs`

Generated/verified current output files (some already part of concurrent daily HEAD):
- `public/index.html`
- `public/archive.html`
- `public/about.html`
- `public/404.html`
- `public/app.css`
- `public/app.js`
- `public/feed.xml`
- `public/articles.json`
- `public/a/amasad-managed-cloud-agents.html`
- `public/a/anthropic-vault-claude.html`
- `public/a/cursor-live-apps.html`
- `public/a/deepseek-super-agent-harness.html`
- `public/a/karpathy-hackertube.html`
- `public/a/levelsio-300-month-expenses.html`
- `public/a/levelsio-bf1942-web.html`
- `public/a/openai-gpt6-cyber.html`
- `public/a/rauchg-agent-schedules.html`
- `public/a/rauchg-vercel-security-review.html`
- `public/a/sarah-guo-personal-software.html`
- `public/a/tibo-dropbox-launch-video.html`
- `public/a/victor-slash-supersmb.html`

The pre-existing `design-previews/` directory is retained, not rewritten in Phase 3. `src/worker.js`, `wrangler.toml`, the content schema and all content JSON remain untouched by this executor.
