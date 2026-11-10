# 他山

跟踪选定研究员在 X 上的长帖、串帖和 X Article，写成忠实的中文，并始终保留原文和原帖链接。

这是本地原型，改编自 [joeseesun/xnews](https://github.com/joeseesun/xnews)（MIT 许可）。没有对外部署，也不发帖、不点赞、不转发。

## 本地预览

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python3 scripts/build.py
python3 scripts/preview.py --port 33206
```

打开 http://127.0.0.1:33206/ 。

- 首页：`/`
- 文章：`/a/<id>`
- 往期：`/archive`
- 研究员名录：`/researchers`
- RSS：`/feed.xml`

行业筛选是一等能力，URL 可用 `?sector=AI` 这样的参数分享。

## 目录

- `watchlist.md`：第一批 36 个跟踪账号
- `content/researchers.json`：名录（姓名、handle、行业、一句话关注点、X 主页）
- `content/articles/<id>.json`：每篇文章一份 JSON
- `content/SCHEMA.md`：字段说明，在 xnews 契约上增加了 `sector`
- `content/EDITORIAL_PROMPT.md`：改写规则（禁用 AI 腔、保留数据和不确定性、区分作者主张与已核实事实）
- `scripts/build.py`：生成 `public/`
- `src/site.css`、`src/site.js`：页面样式和筛选、阅读层

## 如何新增一篇文章

1. 用公开 X 读取工具抓取原帖全文（长帖看 `note_tweet`，X Article 看 `article.plain_text`，串帖按 `conversation_id` 拼接）。
2. 阅读 `content/EDITORIAL_PROMPT.md` 和 `content/SCHEMA.md`。
3. 新建 `content/articles/<kebab-id>.json`：
   - `date` / `published_at`：原文时间
   - `ingested_at`：本站首次收录时间（中国标准时间，UTC+8），之后改稿不要动
   - `sector`：与跟踪名单中的行业一致
   - `original.text_md` 和 `original.media`：原文，不改写
   - `body_md`：中文改写；作者判断写成“他写道”“他认为”
   - `rewrite_media`：为每条原文媒体写位置，或写明 `omit_reason`
4. 运行 `python3 scripts/build.py`，必要时再跑 `python3 -m unittest discover -s tests -p "test_*.py"`。

中文原文（如宝玉、李继刚）可以轻度整理，不必当翻译稿来写。不要编造数字、引语或媒体地址。

## 计划中的每日更新流程

以后可以做成例程，建议每天上午或中午各看一轮（中国标准时间，UTC+8）：

1. 用公开 X 工具按 `from:handle` 检索过去 24 小时，优先看长帖、X Article 和串帖，不把点赞量当选择标准。
2. 按事件去重，同一条消息只收一次；稿件尽量覆盖多个行业，不必每天凑满篇数。
3. 写成 JSON 后本地构建。对外发布方式和域名以后再定。
4. 控制 X 读取次数，给每日热点日报留额度。36 个账号若按行业分批检索，每天大约 10 到 20 次读取通常就够选出几篇长文。

安静日可以少收或不收，不要为了更新而灌水。
