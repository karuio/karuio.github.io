#!/usr/bin/env python3
"""Build 研究员长文 static site from content/articles/*.json → public/.

Adapted from joeseesun/xnews (MIT). Branding, sector filters and the
researcher directory are local additions; keep the upstream license notice.
"""
from __future__ import annotations

import html
import hashlib
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from email.utils import format_datetime
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "articles"
PUBLIC = ROOT / "public"
sys.path.insert(0, str(ROOT / 'scripts'))
from search_metadata import metadata, discovery_files
from source_markdown import render_source_markdown, render_markdown, paragraph_end, normalize_paragraph

SITE_URL = "https://karuio.github.io"
SITE_NAME = "研究员长文"
SITE_SUB = "选定研究员的 X 长帖 · 忠实中文改写"
RESEARCHERS = ROOT / "content" / "researchers.json"
SECTOR_ORDER = [
    "AI",
    "投资/宏观",
    "半导体",
    "SaaS/云",
    "消费互联网/能源数据中心",
    "生物医药",
    "能源/大宗",
    "金融科技",
    "防务/航天/工业",
    "中国产业/对华战略",
    "机器人",
    "消费/产品",
]
TZ_SH = timezone(timedelta(hours=8))

# Presentation sources; public assets are regenerated from these files.
CSS = (ROOT / "src" / "site.css").read_text(encoding="utf-8")
JS = (ROOT / "src" / "site.js").read_text(encoding="utf-8")
CSS_FILE = '/static/app.' + hashlib.sha256(CSS.encode()).hexdigest()[:12] + '.css'
JS_FILE = '/static/app.' + hashlib.sha256(JS.encode()).hexdigest()[:12] + '.js'
# Verified, rendering-only copies of small public images; never rewrite content or RSS URLs.
MEDIA_MANIFEST = json.loads((ROOT / "src" / "media-manifest.json").read_text(encoding="utf-8")) if (ROOT / "src" / "media-manifest.json").exists() else {"assets": []}
LOCAL_MEDIA = {asset["source_url"]: asset["local_url"] for asset in MEDIA_MANIFEST.get("assets", [])}


def local_media_url(url: str) -> str:
    local = LOCAL_MEDIA.get(url, "")
    if local.startswith("/media/") and (PUBLIC / local.lstrip("/")).is_file():
        return local
    return url



def md_to_html(md: str) -> str:
    return render_markdown(md)


def parse_ingested_dt(a: dict) -> datetime | None:
    """Site-first publication time. Missing/invalid values are sortable sentinels, not guessed dates."""
    raw = a.get("ingested_at")
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def ingested_sort_key(a: dict) -> tuple:
    """Newest site ingest first; invalid/missing last; stable id tie-breaker."""
    dt = parse_ingested_dt(a)
    if dt is None:
        # Predictable: undated items sink below dated ones, still stable by id.
        return (1, datetime.min.replace(tzinfo=timezone.utc), a["id"])
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TZ_SH)
    return (0, -dt.timestamp(), a["id"])


def load_articles() -> list[dict]:
    items = []
    for path in sorted(CONTENT.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        data["_file"] = path.name
        items.append(data)
    # Homepage/archive/RSS item order follow first site ingest, never rebuild time.
    items.sort(key=ingested_sort_key)
    return items


def render_original_text(a: dict) -> str:
    orig = a.get("original") or {}
    text = (orig.get("text_md") or "").strip()
    if orig.get("markdown_base_url"):
        return render_source_markdown(text, orig["markdown_base_url"])
    return md_to_html(text)


def fmt_date(date: str) -> str:
    try:
        d = datetime.strptime(date, "%Y-%m-%d")
        week = "一二三四五六日"[d.weekday()]
        return f"{d.year}年{d.month}月{d.day}日 · 周{week}"
    except ValueError:
        return date


def source_date(a: dict) -> str:
    """Calendar day of the original source; never invent from ingest or build time."""
    return a["date"]


def ingested_date(a: dict) -> str:
    """Asia/Shanghai calendar day of first site publication when recorded."""
    dt = parse_ingested_dt(a)
    if dt is None:
        return source_date(a)
    return dt.astimezone(TZ_SH).date().isoformat()


def fmt_short_date(date: str) -> str:
    if len(date) >= 10 and date[4] == "-" and date[7] == "-":
        return date[5:].replace("-", ".")
    return date


def parse_dt(a: dict) -> datetime:
    """RSS pubDate stays on the recorded original source timestamp."""
    raw = a.get("published_at") or f"{a['date']}T12:00:00+08:00"
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return datetime.strptime(a["date"], "%Y-%m-%d").replace(tzinfo=TZ_SH)


def shell(title: str, body_main: str, *, description: str = "", active: str = "home", canonical: str = "/", article: dict | None = None) -> str:
    desc = html.escape(description or SITE_SUB)
    canon = SITE_URL.rstrip("/") + canonical
    image = cover_asset(article)[0] if article else ""
    search_meta = metadata(title, description or SITE_SUB, canonical, article, image) if canonical != "/404" else '<meta name="robots" content="noindex">'
    canonical_tag = f'<link rel="canonical" href="{html.escape(canon)}">' if canonical != "/404" else ""
    is_list = active in ("home", "archive") and canonical in ("/", "/archive")
    dialog = '''<dialog class="reader-sheet" id="reader-sheet" aria-labelledby="sheet-label">
  <header class="sheet-bar"><button type="button" class="sheet-close" data-close-sheet><span aria-hidden="true">×</span>返回选刊</button><span class="sheet-brand" id="sheet-label">研究员长文 · 阅读</span><a href="/" data-sheet-permalink target="_blank" rel="noopener noreferrer">独立页面 ↗</a></header>
  <div class="sheet-scroll" tabindex="-1"></div>
</dialog>''' if is_list else ""
    def current(route):
        return ' aria-current="page"' if active == route else ""
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta name="referrer" content="no-referrer">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{desc}">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#fffefa">
<meta property="og:type" content="{'article' if canonical.startswith('/a/') else 'website'}">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{html.escape(canon)}">
{canonical_tag}
{search_meta}
<link rel="alternate" type="application/rss+xml" title="{SITE_NAME}" href="/feed.xml">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 44 44'%3E%3Crect width='44' height='44' rx='5' fill='%231b1d18'/%3E%3Crect x='12' y='9' width='20' height='26' rx='2' fill='none' stroke='%23fffefa' stroke-width='2'/%3E%3Cpath stroke='%23fffefa' stroke-width='2' d='M17 18h10M17 23h10M17 28h7'/%3E%3C/svg%3E">
<script>try{{var t=localStorage.getItem('xn.theme');if(t==='light'||t==='dark')document.documentElement.dataset.theme=t}}catch(e){{}}</script>
<style data-source="{CSS_FILE}">{CSS}</style>
</head>
<body>
<a class="skip" href="#main">跳到正文</a>
<header class="site-header">
  <a class="brand" href="/" aria-label="研究员长文首页"><span class="brand-wordmark" aria-hidden="true"><svg class="brand-mark" viewBox="0 0 44 44" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><rect x="9" y="6" width="21" height="29" rx="2"/><path d="M15 16h9M15 22h9M15 28h6"/></svg><span class="brand-name">研究员长文<span class="brand-period">。</span></span></span><span class="brand-sub">选定研究员<span>X 长帖 · 中文改写</span></span></a>
  <div class="header-side"><nav class="site-nav" aria-label="主导航"><a href="/"{current('home')}>精选</a><a class="archive-nav" href="/archive"{current('archive')}>往期</a><a href="/researchers"{current('researchers')}>研究员</a><a href="/feed.xml" aria-label="订阅全文 RSS">订阅 RSS <span aria-hidden="true">↗</span></a></nav><button type="button" class="icon-button" id="theme-btn" aria-label="切换为暗色主题" aria-pressed="false"><svg viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="12" cy="12" r="8"/><path d="M12 4a8 8 0 0 1 0 16Z" fill="currentColor" stroke="none"/></svg></button></div>
</header>
<main class="site-main" id="main">
{body_main}
</main>
<footer class="site-footer"><span>选定研究员的 X 长帖 · 忠实中文改写<br>原型站 · 中国标准时间（UTC+8）</span><nav class="footer-links" aria-label="页尾导航"><a href="/feed.xml">全文 RSS ↗</a><a href="/archive">全部文章</a><a href="/researchers">研究员</a><a href="/about">关于</a></nav></footer>
{dialog}
<script data-source="{JS_FILE}">{JS}</script>
</body>
</html>
'''


def source_label(src: dict) -> str:
    t = src.get("type", "link")
    if t == "x_post":
        return f"X · @{src.get('handle','')}"
    if t == "x_article":
        return f"X Article · @{src.get('handle','')}"
    if t == "youtube":
        return "YouTube"
    return src.get("author") or "原文"




def youtube_id(url: str) -> str:
    m = re.search(r"(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{6,})", url or "")
    return m.group(1) if m else ""


def original_notice(a: dict) -> str:
    """Describe availability, never turn stored video excerpts into claimed transcripts."""
    original = a.get("original") or {}
    if original.get("completeness") in ("excerpt", "partial") or a["id"] == "deepseek-super-agent-harness":
        return "视频原文摘录，非完整逐字稿；请以原视频为准。" if a["source"].get("type") == "youtube" else "当前保留的是原文摘录，完整内容请查看原文链接。"
    if not original.get("text_md"):
        return "此条目暂未保存原文文字；媒体与原文链接仍可查看。"
    return ""


def media_id(media: dict) -> str:
    """Persist explicit IDs for new media; existing source objects need not be rewritten."""
    explicit = media.get("id")
    if explicit:
        if not isinstance(explicit, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", explicit):
            raise ValueError("Invalid original media ID")
        return explicit
    identity = media.get("type", "") + "\n" + media.get("url", "")
    return "m_" + hashlib.sha256(identity.encode()).hexdigest()[:16]


def rewrite_media_plan(a: dict) -> tuple[dict, list]:
    """Fail closed on silent media loss, fabricated references or ambiguous placement."""
    available = {}
    for media in (a.get("original") or {}).get("media") or []:
        mid = media_id(media)
        if mid in available and available[mid] != media:
            raise ValueError(f"{a['id']}: media ID collision {mid}")
        available[mid] = media
    references = a.get("rewrite_media", [])
    if not isinstance(references, list):
        raise ValueError(f"{a['id']}: rewrite_media must be an ordered array")
    seen = set()
    for ref in references:
        mid = ref.get("media_id")
        if mid not in available or mid in seen:
            raise ValueError(f"{a['id']}: unknown or repeated rewrite media {mid}")
        seen.add(mid)
        if "omit_reason" in ref:
            if not isinstance(ref["omit_reason"], str) or not ref["omit_reason"].strip():
                raise ValueError(f"{a['id']}: omission needs an explicit reason")
            continue
        if not available[mid].get("url"):
            raise ValueError(f"{a['id']}: missing URL needs an explicit omission reason")
        if ref.get("evidence") not in ("source_metadata_only", "source_position_verified"):
            raise ValueError(f"{a['id']}: reference must state its placement evidence")
        if ref.get("placement") not in ("after_body", "after_paragraph"):
            raise ValueError(f"{a['id']}: invalid rewrite media placement")
        if ref.get("placement") == "after_body" and not (ref.get("placement_note") or "").strip():
            raise ValueError(f"{a['id']}: uncertain placement must be labeled")
        if ref.get("placement") == "after_paragraph":
            if ref.get("evidence") != "source_position_verified":
                raise ValueError(f"{a['id']}: precise placement requires source-position evidence")
            anchor = ref.get("after_md", "")
            try:
                paragraph_end(a["body_md"], anchor)
            except ValueError as error:
                raise ValueError(f"{a['id']}: {error}") from error
    if set(available) != seen:
        raise ValueError(f"{a['id']}: original media missing from rewrite_media: {sorted(set(available) - seen)}")
    return available, references


def render_rewrite(a: dict, *, rss: bool = False) -> str:
    available, refs = rewrite_media_plan(a)
    insertions = {}
    groups = {}
    omissions = []
    for ref in refs:
        if "omit_reason" in ref:
            omissions.append(f'<p class="completeness-note">原文媒体未在改写中展示：{html.escape(ref["omit_reason"])}</p>')
            continue
        key = (ref["placement"], normalize_paragraph(ref.get("after_md", "")))
        groups.setdefault(key, []).append((available[ref["media_id"]], ref.get("placement_note", "")))
    appended = []
    for (placement, anchor), entries in groups.items():
        media = [entry[0] for entry in entries]
        note = " ".join(dict.fromkeys(entry[1] for entry in entries if entry[1]))
        rendered = rss_media_html(media) if rss else render_media_html(media, a["source"]["url"])
        label = "原文附带媒体" if placement == "after_body" else "原文媒体"
        notice = f'<p class="completeness-note">{html.escape(note)}</p>' if note else ""
        heading = f'<h3 class="source-media-heading">{label}</h3>' if placement == "after_body" else ""
        block = f'<section class="rewrite-source-media" aria-label="{label}">{heading}{notice}{rendered}</section>'
        if placement == "after_paragraph":
            insertions[anchor] = block
        else:
            appended.append(block)
    body = render_markdown(a["body_md"], after_paragraph=insertions)
    return body + "\n" + "\n".join(appended + omissions)


def render_media_html(media: list, source_url: str = "") -> str:
    if not media:
        return ""
    parts = ['<div class="original-media">']
    seen = set()
    for m in media:
        mid = media_id(m)
        if mid in seen:
            continue
        seen.add(mid)
        t = (m or {}).get("type") or ""
        url = (m or {}).get("url") or ""
        if not url:
            continue
        u = html.escape(url, quote=True)
        alt = html.escape((m or {}).get("alt") or "原帖配图", quote=True)
        poster = (m or {}).get("poster") or ""
        fallback = html.escape(source_url or url, quote=True)
        if t == "image":
            rendered = f'<img src="{html.escape(local_media_url(url), quote=True)}" data-original-src="{u}" alt="{alt}" loading="lazy" decoding="async" referrerpolicy="no-referrer">'
            label = "原帖图片"
        elif t in ("video", "x_video"):
            poster_attr = f' poster="{html.escape(local_media_url(poster), quote=True)}" data-original-poster="{html.escape(poster, quote=True)}"' if poster else ""
            rendered = f'<video controls playsinline preload="none" src="{u}"{poster_attr} aria-label="原帖视频"></video>'
            if poster:
                rendered += f'<img class="video-poster-fallback" data-video-fallback src="{html.escape(local_media_url(poster), quote=True)}" alt="原视频封面" loading="lazy" hidden>'
            label = "原帖视频 · 外部播放"
        elif t == "audio":
            rendered = f'<audio controls preload="none" src="{u}" aria-label="原帖音频"></audio>'
            label = "原帖音频"
        elif t == "youtube" and youtube_id(url):
            vid = html.escape(youtube_id(url), quote=True)
            rendered = (f'<div class="yt"><iframe src="https://www.youtube-nocookie.com/embed/{vid}" '
                        'title="原视频（需手动播放）" allow="encrypted-media; picture-in-picture; fullscreen" '
                        'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen loading="lazy"></iframe></div>')
            label = "外部播放器 · 需手动播放"
        else:
            parts.append(f'<p><a href="{u}" target="_blank" rel="noopener noreferrer">打开原始媒体 ↗</a></p>')
            continue
        parts.append(f'''<figure class="media-figure" data-media-id="{html.escape(mid, quote=True)}"><div class="media-frame">{rendered}<p class="media-error" role="status" hidden>媒体未能载入，请通过下方原文链接查看。</p></div><figcaption><span>{label}</span><a href="{fallback}" target="_blank" rel="noopener noreferrer">无法显示？去原文查看 ↗</a></figcaption></figure>''')
    parts.append("</div>")
    return "\n".join(parts) if len(parts) > 2 else ""


def render_original_section(a: dict) -> str:
    orig = a.get("original") or {}
    text = (orig.get("text_md") or "").strip()
    title = (orig.get("title") or "").strip()
    title_html = f'<h3 class="original-title">{html.escape(title)}</h3>' if title else ""
    notice = original_notice(a)
    notice_html = f'<p class="completeness-note">{html.escape(notice)}</p>' if notice else ""
    body = render_original_text(a) if text else ""
    lang = html.escape(orig.get("lang") or "en", quote=True)
    return f'''<section class="reader-panel" id="original" data-reader-panel="original" aria-label="原文">
<h2 class="section-heading">原文</h2>{notice_html}{title_html}
{render_media_html(orig.get('media') or [], a['source']['url'])}
<div class="prose" lang="{lang}">{body}</div>
</section>'''


def rss_media_html(media: list) -> str:
    """Upstream media URLs, once per section; no local-path leakage into RSS."""
    parts, seen = [], set()
    for m in media:
        mid = media_id(m)
        if mid in seen:
            continue
        seen.add(mid)
        url = m.get("url") or ""
        if not url:
            continue
        u = html.escape(url, quote=True)
        alt = html.escape(m.get("alt") or "", quote=True)
        t = m.get("type", "")
        poster = m.get("poster") or ""
        poster_attr = f' poster="{html.escape(poster, quote=True)}"' if poster else ""
        if t == "image":
            rendered = f'<img src="{u}" alt="{alt}">'
        elif t in ("video", "x_video"):
            rendered = f'<video controls playsinline preload="none" src="{u}"{poster_attr}></video>'
        elif t == "audio":
            rendered = f'<audio controls preload="none" src="{u}"></audio>'
        elif t == "youtube" and youtube_id(url):
            vid = html.escape(youtube_id(url))
            rendered = f'<iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/{vid}" title="原视频（手动播放）" loading="lazy" allowfullscreen></iframe>'
        else:
            rendered = ""
        parts.append(f'<figure data-media-id="{html.escape(mid)}">{rendered}<figcaption><a href="{u}">打开原始媒体 ↗</a></figcaption></figure>')
    return "\n".join(parts)



def cover_asset(a: dict) -> tuple[str, str]:
    for media in (a.get("original") or {}).get("media") or []:
        if media.get("type") == "image" and media.get("url"):
            return local_media_url(media["url"]), media.get("alt") or "原帖配图"
        if media.get("poster"):
            return local_media_url(media["poster"]), "原视频封面"
        if media.get("type") == "youtube" and youtube_id(media.get("url") or ""):
            return f'https://i.ytimg.com/vi/{youtube_id(media["url"])}/hqdefault.jpg', "原视频封面"
    return "", ""


def story_type(a: dict) -> str:
    source_type = a["source"].get("type")
    if source_type == "youtube":
        return "视频"
    if source_type == "x_article":
        return "X Article"
    if any(m.get("type") in ("video", "x_video", "youtube") for m in (a.get("original") or {}).get("media") or []):
        return "长帖 / 视频"
    return "长帖" if source_type == "x_post" else "文章"


def cover_word(a: dict) -> str:
    # Use stored names or numbers from the actual title, not invented editorial claims.
    if "$300" in a["title"]:
        return "$300"
    name = a["source"].get("author") or a["source"].get("handle") or SITE_NAME
    if "/" in name:
        name = a["source"].get("handle") or name.split("/")[0]
    return name.split()[0] if name.split() else SITE_NAME


def reading_minutes(a: dict) -> int:
    """Approximate Chinese reading time; video duration is deliberately excluded."""
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", a.get("body_md") or "")
    units = len(re.findall(r"[\u3400-\u9fff]|[A-Za-z0-9]+", text))
    return max(1, (units + 299) // 300)


def sector_of(a: dict) -> str:
    return (a.get("sector") or "").strip()


def load_researchers() -> list[dict]:
    if not RESEARCHERS.is_file():
        return []
    data = json.loads(RESEARCHERS.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("researchers") or []
    return data


def discovery_tools(articles: list[dict], *, archive: bool = False) -> str:
    videos = sum("视频" in story_type(a) for a in articles)
    counts = {}
    for a in articles:
        sec = sector_of(a)
        if sec:
            counts[sec] = counts.get(sec, 0) + 1
    sector_buttons = ['<button type="button" data-sector-filter="all" aria-pressed="true">全部行业</button>']
    for name in SECTOR_ORDER:
        if name in counts:
            sector_buttons.append(
                f'<button type="button" data-sector-filter="{html.escape(name, quote=True)}" aria-pressed="false">{html.escape(name)} <span>{counts[name]}</span></button>'
            )
    for name, n in sorted(counts.items()):
        if name not in SECTOR_ORDER:
            sector_buttons.append(
                f'<button type="button" data-sector-filter="{html.escape(name, quote=True)}" aria-pressed="false">{html.escape(name)} <span>{n}</span></button>'
            )
    return f'''<section class="discovery" data-discovery data-default-view="{'list' if archive else 'journal'}" aria-label="查找文章" hidden>
<div class="discovery-top"><div class="filter-group" role="group" aria-label="内容类型">
<button type="button" data-filter="all" aria-pressed="true">全部 <span>{len(articles)}</span></button>
<button type="button" data-filter="text" aria-pressed="false">图文 <span>{len(articles) - videos}</span></button>
<button type="button" data-filter="video" aria-pressed="false">含视频 <span>{videos}</span></button></div>
<div class="search-field"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg><label class="sr-only" for="story-search">搜索标题、作者、行业或主题</label><input id="story-search" type="search" name="q" placeholder="搜索标题、作者、行业或主题" autocomplete="off" aria-controls="news-grid"><button type="button" data-clear-search aria-label="清除搜索" hidden>×</button></div></div>
<div class="filter-group sector-filters" role="group" aria-label="按行业筛选">{''.join(sector_buttons)}</div>
<div class="discovery-bottom"><p data-result-count role="status" aria-live="polite" aria-atomic="true"></p><div class="view-switch" role="group" aria-label="浏览方式"><button type="button" data-layout="journal" aria-pressed="true"><svg viewBox="0 0 18 18" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M2 2h5v14H2zM11 2h5v5h-5zM11 11h5v5h-5z"/></svg>影像刊</button><button type="button" data-layout="list" aria-pressed="false"><svg viewBox="0 0 18 18" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M2 3h14M2 9h14M2 15h14"/></svg>速览</button></div></div>
</section>'''


def discovery_empty() -> str:
    return '''<section class="search-empty" data-search-empty hidden><p class="empty-symbol" aria-hidden="true">↳</p><h2>没有找到匹配的文章</h2><p data-empty-description></p><button class="reset-button" type="button" data-reset-filters>查看全部文章</button></section>'''


def build_feed_items(articles: list[dict]) -> str:
    if not articles:
        return '<section class="empty-state"><h2>还没有文章</h2><p>稍后再来，或先订阅 <a href="/feed.xml">全文 RSS</a>。</p></section>'
    rows = []
    for index, a in enumerate(articles):
        src = a["source"]
        image, alt = cover_asset(a)
        slug = html.escape(a["id"], quote=True)
        kind = story_type(a)
        author = html.escape(src.get("author") or src.get("handle") or "原作者")
        classes = ["news-card", "card--media" if image else "card--text"]
        if index == 0 and image:
            classes.append("is-featured")
        if not image:
            classes.append("tone-ink" if index % 3 == 1 else "tone-sage" if index % 3 == 2 else "tone-paper")
        word = html.escape(cover_word(a))
        if image:
            badge = f'<span class="cover-badge">▶ {html.escape(kind)}</span>' if "视频" in kind else ""
            cover = f'''<div class="cover" data-cover><div class="cover-fallback" aria-hidden="true"><span class="cover-word">{word}</span></div><img src="{html.escape(image, quote=True)}" alt="{html.escape(alt, quote=True)}" loading="{'eager' if index == 0 else 'lazy'}" decoding="async" {'fetchpriority="high"' if index == 0 else ''} referrerpolicy="no-referrer">{badge}</div>'''
        else:
            cover = f'<div class="type-cover" aria-hidden="true"><span class="type-index">{index + 1:02d} / NOTES</span><span class="cover-word">{word}<span class="type-dot">.</span></span></div>'
        sector = sector_of(a)
        search = html.escape(' '.join([a['title'], a.get('dek') or '', src.get('author') or '', src.get('handle') or '', sector, ' '.join(a.get('tags') or [])]), quote=True)
        site_day = ingested_date(a)
        orig_day = source_date(a)
        if site_day != orig_day:
            date_meta = f'<time datetime="{html.escape(site_day, quote=True)}">收录 {html.escape(fmt_short_date(site_day))}</time><span>原文 {html.escape(fmt_short_date(orig_day))}</span>'
        else:
            date_meta = f'<time datetime="{html.escape(site_day, quote=True)}">{html.escape(fmt_short_date(site_day))}</time>'
        sector_label = html.escape(sector) if sector else html.escape(kind)
        card_body = f'''<div class="card-body"><div class="card-meta"><span>{sector_label} / {author}</span>{date_meta}</div>
<h2 class="card-title">{html.escape(a['title'])}</h2><p class="card-dek">{html.escape(a.get('dek') or '')}</p><div class="card-end"><span>中文约 {reading_minutes(a)} 分钟</span><span class="card-read">阅读全文 <span class="card-arrow" aria-hidden="true">→</span></span></div></div>'''
        # Lead with the headline, keeping source and visual reading order identical.
        card_content = card_body + cover if "is-featured" in classes else cover + card_body
        rows.append(f'''<article class="{' '.join(classes)}" id="story-{slug}" data-kind="{'video' if '视频' in kind else 'text'}" data-sector="{html.escape(sector, quote=True)}" data-search="{search}">
<a class="card-link" href="/a/{slug}" id="read-{slug}" data-open-reader data-reader-src="{reader_url(a)}" data-source-url="{html.escape(src['url'], quote=True)}">
{card_content}
</a><a class="cover-error-link" href="{html.escape(src['url'], quote=True)}" target="_blank" rel="noopener noreferrer">封面未能显示 · 去原文查看 ↗</a>
</article>''')
    return '\n'.join(rows)


def render_article(a: dict) -> str:
    src = a["source"]
    source_url = html.escape(src["url"], quote=True)
    source = source_label(src)
    kind = story_type(a)
    sector = sector_of(a)
    kicker = source if kind in source else f"{source} / {kind}"
    if sector:
        kicker = f"{sector} / {kicker}"
    related = f'<a href="{html.escape(src["related_url"], quote=True)}" target="_blank" rel="noopener noreferrer">相关链接 ↗</a>' if src.get("related_url") else ""
    return f'''<article class="article-reader" data-article-id="{html.escape(a['id'], quote=True)}">
<a class="article-back" href="/">← 返回选刊</a>
<header class="article-header"><p class="article-kicker">{html.escape(kicker)}</p><h1>{html.escape(a['title'])}</h1><p class="article-dek">{html.escape(a.get('dek') or '')}</p><div class="article-meta"><time datetime="{html.escape(ingested_date(a), quote=True)}">本站收录 {fmt_date(ingested_date(a))}</time><span>原文发布 {fmt_date(source_date(a))}</span><span>原作者：{html.escape(src.get('author') or '')}</span><span>中文改写：<a href="/about">研究员长文</a></span><span>{' · '.join(html.escape(t) for t in a.get('tags') or [])}</span></div></header>
<nav class="reader-tabs" aria-label="文章版本与来源"><div data-tabs><a href="#rewrite" id="tab-rewrite" data-view="rewrite">中文改写</a><a href="#original" id="tab-original" data-view="original">原文</a></div><a class="reader-source" href="{source_url}" target="_blank" rel="noopener noreferrer">原文链接 ↗</a><div class="reading-position" hidden><progress max="100" value="0" aria-label="当前版本阅读进度"></progress><span data-reading-percent aria-hidden="true">0%</span></div></nav>
<section class="reader-panel" id="rewrite" data-reader-panel="rewrite" aria-label="中文改写"><h2 class="section-heading">中文改写</h2><div class="prose">{render_rewrite(a)}</div></section>
{render_original_section(a)}
<footer class="source-box"><span>内容来自原作者；中文为忠实改写，非逐字翻译。作者主张与已核实事实分开书写。</span><div><a href="{source_url}" target="_blank" rel="noopener noreferrer">打开原文 ↗</a>{related}</div></footer>
</article>'''


def reader_document(a: dict) -> str:
    """The in-page reader needs the article, not another copy of the site shell."""
    return f'<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><title>{html.escape(a["title"])} · {SITE_NAME}</title><meta name="robots" content="noindex"></head><body>{render_article(a)}</body></html>'


def reader_url(a: dict) -> str:
    digest = hashlib.sha256(reader_document(a).encode()).hexdigest()[:12]
    return f'/read/{a["id"]}.{digest}.html'


def rss_full_html(a: dict) -> str:
    """Full article HTML for RSS readers (description + content:encoded)."""
    src = a["source"]
    body = render_rewrite(a, rss=True)
    parts = []
    dek = (a.get("dek") or "").strip()
    if dek:
        parts.append(f"<p><em>{html.escape(dek)}</em></p>")
    parts.append("<h2>中文改写</h2>")
    parts.append(body)
    orig = a.get("original") or {}
    otext = (orig.get("text_md") or "").strip()
    omedia = orig.get("media") or []
    if otext or omedia:
        parts.append("<h2>原文</h2>")
        notice = original_notice(a)
        if notice:
            parts.append(f"<p>{html.escape(notice)}</p>")
        otitle = (orig.get("title") or "").strip()
        if otitle:
            parts.append(f"<p><em>{html.escape(otitle)}</em></p>")
        media_html = rss_media_html(omedia)
        if media_html:
            parts.append(media_html)
        if otext:
            parts.append(render_original_text(a))
    parts.append(
        "<p><strong>原文链接：</strong>"
        f'<a href="{html.escape(src["url"])}">{html.escape(src["url"])}</a></p>'
    )
    if src.get("related_url"):
        parts.append(
            "<p><strong>相关链接：</strong>"
            f'<a href="{html.escape(src["related_url"])}">{html.escape(src["related_url"])}</a></p>'
        )
    return "\n".join(parts)


def markdown_label(value: str) -> str:
    """Plain metadata must not create Markdown/HTML in the exported rewrite."""
    value = html.escape(" ".join(value.split()), quote=False)
    return re.sub(r"([\\`*_{}\[\]()#!|])", r"\\\1", value)


def markdown_media(media: dict) -> str:
    # Angle-delimited destinations support parentheses; encode whitespace and
    # delimiters so a metadata URL cannot terminate the Markdown destination.
    url = quote(media["url"], safe="/:#?&=%@+;,~!$'()*[]")
    kind = media.get("type")
    if kind == "image":
        return f'![{markdown_label(media.get("alt") or "原帖图片")}](<{url}>)'
    label = "收听原始音频" if kind == "audio" else "观看原视频" if kind in ("video", "x_video", "youtube") else "打开原始媒体"
    return f"[{label}](<{url}>)"


def render_rewrite_markdown(a: dict) -> str:
    """Published body with its validated media placements; never original prose."""
    available, refs = rewrite_media_plan(a)
    groups, omissions = {}, []
    for ref in refs:
        if "omit_reason" in ref:
            omissions.append("原文媒体未在改写中展示：" + markdown_label(ref["omit_reason"]))
            continue
        key = (ref["placement"], normalize_paragraph(ref.get("after_md", "")))
        groups.setdefault(key, []).append((available[ref["media_id"]], ref.get("placement_note", "")))
    body = a["body_md"]
    # Keep the source Markdown and whitespace intact, inserting only at the
    # exact complete paragraph already checked by rewrite_media_plan.
    insertions = []
    appended = []
    for (placement, anchor), entries in groups.items():
        label = "原文附带媒体" if placement == "after_body" else "原文媒体"
        note = " ".join(dict.fromkeys(entry[1] for entry in entries if entry[1]))
        parts = ["### " + label] if placement == "after_body" else []
        if note:
            parts.append(markdown_label(note))
        parts.extend(markdown_media(media) for media, _ in entries)
        block = "\n\n".join(parts)
        if placement == "after_paragraph":
            insertions.append((paragraph_end(body, anchor), "\n\n" + block))
        else:
            appended.append(block)
    for offset, fragment in sorted(insertions, reverse=True):
        body = body[:offset] + fragment + body[offset:]
    return body + ("\n\n" + "\n\n".join(appended + omissions) if appended or omissions else "")


def rss_versions(a: dict) -> dict:
    """Version 1 transport: two self-contained bodies for aware RSS readers."""
    orig, src = a.get("original") or {}, a["source"]
    title = (orig.get("title") or "").strip() or (src.get("title_en") or "").strip() or "Original source"
    text = (orig.get("text_md") or "").strip()
    parts = [f"<h2>{html.escape(title)}</h2>"]
    notice = original_notice(a) if text else "此条目暂未保存原文文字；媒体与原文链接仍可查看。"
    if notice:
        parts.append(f"<p>{html.escape(notice)}</p>")
    media = orig.get("media") or []
    parts.append(rss_media_html(media))
    if any(not m.get("url") for m in media):
        parts.append("<p>部分原文媒体地址缺失，请通过原文链接查看。</p>")
    if text:
        parts.append(render_original_text(a))
    for label, url in (("原文链接", src["url"]), ("相关链接", src.get("related_url"))):
        if url:
            escaped = html.escape(url, quote=True)
            parts.append(f'<p>{label}：<a href="{escaped}">{escaped}</a></p>')
    return {
        "version": 1,
        "original": {"title": title, "url": src["url"], "lang": (orig.get("lang") or "").strip() or "und", "html": "\n".join(parts)},
        "rewrite": {"title": a["title"], "markdown": render_rewrite_markdown(a), "html": render_rewrite(a, rss=True)},
    }


def build_rss(articles: list[dict]) -> str:
    items = []
    for a in articles:
        link = f"{SITE_URL}/a/{a['id']}"
        dt = parse_dt(a)
        full = rss_full_html(a)
        # CDATA so readers get full HTML; escape any ]]> in body
        cdata = full.replace("]]>", "]]]]><![CDATA[>")
        versions = json.dumps(rss_versions(a), ensure_ascii=False).replace("]]>", "]]]]><![CDATA[>")
        items.append(f"""    <item>
      <title>{xml_escape(a['title'])}</title>
      <link>{xml_escape(link)}</link>
      <guid isPermaLink="true">{xml_escape(link)}</guid>
      <pubDate>{format_datetime(dt.astimezone(timezone.utc))}</pubDate>
      <author>{xml_escape(a['source'].get('author',''))}</author>
      <description><![CDATA[{cdata}]]></description>
      <content:encoded><![CDATA[{cdata}]]></content:encoded>
      <qiaomu:versions><![CDATA[{versions}]]></qiaomu:versions>
    </item>""")
    now = datetime.now(timezone.utc)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:qiaomu="https://qiaomu.ai/ns/rss/1.0">
  <channel>
    <title>{xml_escape(SITE_NAME)}</title>
    <link>{SITE_URL}/</link>
    <description>{xml_escape(SITE_SUB)}</description>
    <language>zh-CN</language>
    <lastBuildDate>{format_datetime(now)}</lastBuildDate>
    <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(items)}
  </channel>
</rss>
"""


def build() -> None:
    articles = load_articles()
    if not articles:
        raise SystemExit("No articles in content/articles/")

    PUBLIC.mkdir(parents=True, exist_ok=True)
    (PUBLIC / "a").mkdir(exist_ok=True)
    (PUBLIC / "read").mkdir(exist_ok=True)
    (PUBLIC / "static").mkdir(exist_ok=True)
    (PUBLIC / CSS_FILE.lstrip("/")).write_text(CSS, encoding="utf-8")
    (PUBLIC / JS_FILE.lstrip("/")).write_text(JS, encoding="utf-8")
    discovery_files(PUBLIC, articles)
    (PUBLIC / "app.css").write_text(CSS, encoding="utf-8")
    (PUBLIC / "app.js").write_text(JS, encoding="utf-8")
    (PUBLIC / "feed.xml").write_text(build_rss(articles), encoding="utf-8")
    (PUBLIC / "articles.json").write_text(
        json.dumps(
            [
                {
                    "id": a["id"],
                    "date": a["date"],
                    "title": a["title"],
                    "dek": a.get("dek"),
                    "url": f"/a/{a['id']}",
                    "source_url": a["source"]["url"],
                    "tags": a.get("tags", []),
                    "sector": a.get("sector"),
                }
                for a in articles
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    latest = ingested_date(articles[0])
    heading = f'''<section class="edition-line"><div><p class="edition-kicker">THE EDIT <span aria-hidden="true">/</span> 近期精选</p><h1 tabindex="-1">读完研究员自己写的长帖。</h1><p class="edition-description">跟踪选定账号新发的长帖、串帖和 X Article，写成忠实的中文，并保留原文与链接。</p></div><div class="edition-meta"><span class="edition-label">最新收录</span><time datetime="{html.escape(latest, quote=True)}">{html.escape(latest.replace('-', '.'))}</time><span class="edition-note">按行业筛选 · 原文始终可对账</span></div></section>'''
    home = heading + discovery_tools(articles) + f'<section class="news-grid" id="news-grid" data-news-grid aria-label="研究员长文选刊">{build_feed_items(articles)}</section>' + discovery_empty()
    (PUBLIC / "index.html").write_text(
        shell(f"{SITE_NAME}", home, description=SITE_SUB, active="home", canonical="/"), encoding="utf-8",
    )
    archive = f'''<section class="edition-line"><div><h1 tabindex="-1">全部文章</h1><p>按本站首次收录时间倒序，中文改写与原文一起保留；原文发布日期单独标注。</p></div><p class="edition-meta">共 {len(articles)} 篇</p></section>''' + discovery_tools(articles, archive=True) + f'<section class="news-grid" id="news-grid" data-news-grid aria-label="全部文章">{build_feed_items(articles)}</section>' + discovery_empty()
    (PUBLIC / "archive.html").write_text(
        shell(f"全部文章 · {SITE_NAME}", archive, active="archive", canonical="/archive"), encoding="utf-8",
    )
    about = f'''<article class="about-copy prose"><h1>关于 {SITE_NAME}</h1><p>这是一个跟踪选定研究员 X 长帖的中文阅读站。做法参考开源项目 <a href="https://github.com/joeseesun/xnews" target="_blank" rel="noopener noreferrer">joeseesun/xnews</a>（MIT 许可）：先保存原文，再写成忠实、好读的中文，并附上原帖链接。</p><p>中文是改写，并不是逐字翻译。作者自己的判断会写成“他认为”“他写道”，不把帖子主张说成已经独立核实的事实。视频如果没有可播放地址或逐字稿，页面会如实说明。</p><p>首页与往期按本站首次收录时间排序，同时标出原文发布日。RSS 的 pubDate 对应已记录的原作发布时间。本页是本地原型，尚未对外发布。</p><p>静态站点生成器改编自 xnews 的构建脚本，并增加了行业标签和研究员名录。</p><p><a href="/archive">全部文章</a> · <a href="/researchers">跟踪名单</a> · <a href="/feed.xml">全文 RSS</a></p></article>'''
    (PUBLIC / "about.html").write_text(shell(f"关于 · {SITE_NAME}", about, active="about", canonical="/about"), encoding="utf-8")
    people = load_researchers()
    grouped = {name: [] for name in SECTOR_ORDER}
    extra = {}
    for person in people:
        sec = person.get("sector") or "其他"
        if sec in grouped:
            grouped[sec].append(person)
        else:
            extra.setdefault(sec, []).append(person)
    blocks = []
    for sec, members in list(grouped.items()) + list(extra.items()):
        if not members:
            continue
        cards = []
        for person in members:
            handle = html.escape(person.get("handle") or "")
            name = html.escape(person.get("name") or handle)
            focus = html.escape(person.get("focus") or "")
            url = html.escape(person.get("url") or f"https://x.com/{person.get('handle','')}", quote=True)
            cards.append(f'''<article class="researcher-card"><h3>{name}</h3><p class="researcher-handle"><a href="{url}" target="_blank" rel="noopener noreferrer">@{handle} ↗</a></p><p class="researcher-focus">{focus}</p></article>''')
        blocks.append(f'<section class="researcher-section"><h2>{html.escape(sec)}</h2><div class="researcher-grid">{"".join(cards)}</div></section>')
    researchers_page = f'''<section class="edition-line"><div><h1 tabindex="-1">跟踪中的研究员</h1><p>第一批 {len(people)} 个账号，按行业分组。每篇文章也会带上对应的行业标签。</p></div><p class="edition-meta">共 {len(people)} 人</p></section>{"".join(blocks)}'''
    (PUBLIC / "researchers.html").write_text(
        shell(f"研究员 · {SITE_NAME}", researchers_page, description="第一批跟踪的研究员名单，按行业分组。", active="researchers", canonical="/researchers"),
        encoding="utf-8",
    )
    (PUBLIC / "404.html").write_text(
        shell(f"未找到 · {SITE_NAME}", '<section class="empty-state"><p>404 / 未找到</p><h1>这篇内容不在这里。</h1><p>链接可能不完整，或内容已经移动。<a href="/">返回选刊</a>，或去<a href="/archive">全部文章</a>找找。</p></section>', active="", canonical="/404"), encoding="utf-8",
    )
    for a in articles:
        (PUBLIC / reader_url(a).lstrip("/")).write_text(reader_document(a), encoding="utf-8")
        (PUBLIC / "a" / f"{a['id']}.html").write_text(
            shell(f"{a['title']} · {SITE_NAME}", render_article(a), description=a.get("dek") or a["title"], active="article", canonical=f"/a/{a['id']}", article=a), encoding="utf-8",
        )

    print(f"Built {len(articles)} articles → {PUBLIC}")


if __name__ == "__main__":
    build()
