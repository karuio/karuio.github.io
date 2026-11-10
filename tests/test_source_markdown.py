"""Source README rendering and playback request-policy regressions."""
import json
import unittest

from test_build import ROOT, Tags, build
from source_markdown import render_source_markdown

BASE = "https://github.com/sardorml/captureflow/blob/c5792345e7d5e47084c5e829b3f11c98a432c859/README.md"
RAW = "https://raw.githubusercontent.com/sardorml/captureflow/c5792345e7d5e47084c5e829b3f11c98a432c859/"


class SourceMarkdown(unittest.TestCase):
    @unittest.skip("xnews-specific corpus check")
    def test_saved_readme_has_real_tables_code_links_and_images(self):
        a = json.loads((ROOT / "content/articles/captureflow-screen-recorder.json").read_text())
        output = build.render_original_text(a)
        doc = Tags(output)
        self.assertTrue(doc.select("table"))
        self.assertTrue(doc.select("pre"))
        self.assertTrue(doc.select("code"))
        self.assertTrue(doc.select("a", href=BASE.replace("README.md", "LICENSE")))
        self.assertTrue(doc.select("img", src=RAW + ".github/assets/readme-hero.png"))
        self.assertTrue(doc.select("img", src=RAW + "apps/web/public/brand-mark-dark.svg"))
        self.assertTrue(doc.select("source", srcset=RAW + "apps/web/public/brand-mark-light.svg"))
        for artifact in ("[ci-image]:", "[chrome-url]", "```", "&lt;picture&gt;", "&lt;div align="):
            self.assertNotIn(artifact, output)
        for tag, attrs in doc.tags:
            for name in ("src", "href", "srcset"):
                if name in attrs:
                    self.assertTrue(attrs[name].startswith("https://"), (tag, attrs))
        # One source renderer feeds the page, legacy RSS, and independent original.
        self.assertIn(output, build.render_article(a))
        self.assertIn(output, build.rss_full_html(a))
        p = build.rss_versions(a)
        self.assertIn(output, p["original"]["html"])
        self.assertNotIn(output, p["rewrite"]["html"])

    def test_reference_links_fences_and_nested_lists_keep_semantics(self):
        output = render_source_markdown('''[License][license]

[license]: ./LICENSE

- Parent
  - Child

```sh
echo '<script>literal code</script>'
```

| Tool | Status |
| --- | --- |
| Chrome | Ready |
''', BASE)
        doc = Tags(output)
        self.assertEqual(len(doc.select("ul")), 2)
        self.assertTrue(doc.select("table"))
        self.assertTrue(doc.select("a", href=BASE.replace("README.md", "LICENSE")))
        self.assertIn("&lt;script&gt;literal code&lt;/script&gt;", output)

    def test_untrusted_html_and_urls_do_not_become_executable(self):
        output = render_source_markdown('''<script>badScript()</script>
<style>badStyle()</style>
<iframe src="https://evil.invalid">badFrame()</iframe>
<img src="javascript:bad()" onerror="bad()">
<source srcset="javascript:bad()">
<a href="javascript:bad()" id="rewrite" name="location" style="color:red" onclick="bad()">safe text</a>
<img src="data:image/svg+xml,evil">

[bad](javascript:bad())
''', BASE)
        doc = Tags(output)
        for forbidden in ("script", "style", "iframe"):
            self.assertFalse(doc.select(forbidden))
        for _, attrs in doc.tags:
            self.assertFalse(any(k in attrs for k in ("onerror", "onclick", "style", "id", "name")))
            for name in ("href", "src", "srcset"):
                if name in attrs:
                    self.assertTrue(attrs[name].startswith(("http:", "https:", "mailto:")))
        self.assertNotIn("badScript()", output)
        self.assertIn("safe text", output)

    def test_base_must_be_an_explicit_https_document(self):
        for base in ("", "README.md", "file:///tmp/README", "javascript:bad()"):
            with self.assertRaises(ValueError):
                render_source_markdown("text", base)

    @unittest.skip("xnews-specific corpus check")
    def test_page_referrer_policy_allows_public_media_requests(self):
        headers = (ROOT / "public/_headers").read_text()
        self.assertIn("Referrer-Policy: no-referrer", headers)
        for path in (ROOT / "public").rglob("*.html"):
            if path.parent.name == "read":
                continue  # Inert reader payload inherits the host document policy.
            self.assertTrue(Tags(path.read_text()).select("meta", name="referrer", content="no-referrer"), path)
        a = next(a for a in build.load_articles() if a["id"] == "cursor-live-apps")
        for output in (build.render_article(a), build.rss_versions(a)["original"]["html"], build.rss_versions(a)["rewrite"]["html"]):
            video = Tags(output).select("video")[0]
            self.assertEqual(video["src"], a["original"]["media"][0]["url"])
            self.assertIn("controls", video)
            self.assertEqual(video["preload"], "none")


if __name__ == "__main__":
    unittest.main()
