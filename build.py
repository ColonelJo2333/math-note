#!/usr/bin/env python3
"""
极简静态博客引擎 — 数学笔记发布
用法:
    python build.py build    # 构建全站
    python build.py serve    # 本地预览（保存自动重建）
"""

import os, sys, re, shutil, time, threading
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

try:
    import markdown
except ImportError:
    print("✗  缺少依赖: pip install markdown")
    sys.exit(1)

# ── 路径 ──────────────────────────────────────────────
ROOT      = Path(__file__).resolve().parent
POSTS_DIR = ROOT / "posts"
DIST_DIR  = ROOT / "dist"
TEMPLATE  = ROOT / "template.html"
STYLE     = ROOT / "style.css"

# ── YAML front matter 解析（不依赖 pyyaml） ──────────
def parse_frontmatter(text):
    """解析 YAML front matter，只支持 key: value 单行格式"""
    if not text.startswith("---"):
        return {}, text
    end = text.find("---", 3)
    if end == -1:
        return {}, text
    block = text[3:end].strip()
    body  = text[end + 3:].strip()
    meta  = {}
    for line in block.splitlines():
        line = line.strip()
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body

# ── 数学公式保护 ─────────────────────────────────────
def protect_math(text):
    """替换数学公式为占位符，返回 (处理后文本, 占位符字典)"""
    holders = {}
    counter = 0

    def _replace(m):
        nonlocal counter
        key = f"\x00MATH{counter}\x00"
        counter += 1
        holders[key] = m.group(0)
        return key

    text = re.sub(r'\$\$[\s\S]+?\$\$', _replace, text)
    text = re.sub(r'(?<!\$)\$(?!\$)(?!\s)(.+?)(?<!\s)\$(?!\$)', _replace, text)
    return text, holders

def restore_math(html, holders):
    for key, val in holders.items():
        html = html.replace(key, val)
        escaped_key = key.replace('\x00', '&#0;')
        html = html.replace(escaped_key, val)
    return html

# ── Markdown → HTML ──────────────────────────────────
def _slugify(value, separator):
    slug = re.sub(r'[^\w\u4e00-\u9fff-]', '', value.lower().replace(' ', separator))
    return slug or f"section-{hash(value) % 10000}"

def md_to_html(md_text):
    protected, holders = protect_math(md_text)
    html = markdown.markdown(
        protected,
        extensions=["fenced_code", "tables", "toc"],
        extension_configs={"toc": {"permalink": False, "slugify": _slugify}},
    )
    return restore_math(html, holders)

# ── 目录提取 ─────────────────────────────────────────
def extract_toc(html):
    pattern = r'<(h[2-4])[^>]*\bid="([^"]*)"[^>]*>(.*?)</\1>'
    headings = re.findall(pattern, html, re.DOTALL)
    if not headings:
        return ""
    items = []
    for tag, hid, text in headings:
        clean = re.sub(r'<[^>]+>', '', text).strip()
        level = int(tag[1]) - 2
        items.append(f'<a class="toc-item toc-level-{level}" href="#{hid}">{clean}</a>')
    return "\n".join(items)

# ── 文章头部 meta ─────────────────────────────────────
def build_meta_block(meta):
    parts = []
    author   = meta.get("author", "")
    date     = meta.get("date", "")
    abstract = meta.get("abstract", "")
    category = meta.get("category", "")

    line = []
    if author:
        line.append(f'<span class="author">{author}</span>')
    if date:
        line.append(f'<time>{date}</time>')
    if line:
        parts.append('<div class="post-meta">' + " &middot; ".join(line) + '</div>')

    if category:
        parts.append(f'<div class="post-meta"><span class="category-label">{category}</span></div>')

    if abstract:
        parts.append(f'<p class="post-abstract">{abstract}</p>')

    return "\n".join(parts)

# ── 提取正文纯文本摘要 ───────────────────────────────
def extract_excerpt(body_md, length=80):
    """从 Markdown 源文本中提取前 N 个字的纯文本"""
    # 去掉标题行、公式块、空行
    lines = []
    in_math = False
    for line in body_md.splitlines():
        stripped = line.strip()
        if stripped.startswith('$$'):
            in_math = not in_math
            continue
        if in_math:
            continue
        if stripped.startswith('#'):
            continue
        if not stripped:
            continue
        # 去掉行内公式和 markdown 标记
        clean = re.sub(r'\$[^$]+\$', '', stripped)
        clean = re.sub(r'[*_`\[\]()>]', '', clean)
        clean = re.sub(r'!\[.*?\]\(.*?\)', '', clean)
        clean = clean.strip()
        if clean:
            lines.append(clean)
    text = " ".join(lines)
    if len(text) > length:
        text = text[:length] + "…"
    return text

# ── 构建单篇文章 ─────────────────────────────────────
def build_post(md_path, template):
    raw  = md_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw)

    title    = meta.get("title", md_path.stem)
    date     = meta.get("date", "")
    category = meta.get("category", "")
    abstract = meta.get("abstract", "")
    excerpt  = extract_excerpt(body)

    content_html = md_to_html(body)
    toc_html     = extract_toc(content_html)
    meta_block   = build_meta_block(meta)

    page = f'''  <div class="layout">
    <main class="content">
      <article>
        <div class="post-header">
          <h1>{title}</h1>
          {meta_block}
        </div>
        {content_html}
      </article>
    </main>

    <nav class="toc" id="toc">
      <div class="toc-title">目录</div>
      {toc_html}
    </nav>
  </div>'''

    html = template.replace("{{title}}", title).replace("{{page_content}}", page)

    slug = md_path.stem
    out  = DIST_DIR / f"{slug}.html"
    out.write_text(html, encoding="utf-8")

    return {
        "title": title, "date": date, "category": category,
        "abstract": abstract, "excerpt": excerpt,
        "slug": slug, "file": out,
    }

# ── SVG 图标 ─────────────────────────────────────────
ICON_BLOG    = '<svg viewBox="0 0 24 24"><path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0a1 1 0 01-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 01-1 1h-2z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ICON_GITHUB  = '<svg viewBox="0 0 24 24"><path d="M12 .3a12 12 0 00-3.8 23.38c.6.12.83-.26.83-.57L9 20.86c-3.37.74-4.08-1.63-4.08-1.63-.55-1.4-1.34-1.77-1.34-1.77-1.1-.75.08-.73.08-.73 1.21.08 1.85 1.24 1.85 1.24 1.08 1.84 2.82 1.31 3.51 1 .11-.78.42-1.31.76-1.61-2.69-.31-5.52-1.35-5.52-6a4.68 4.68 0 011.25-3.25 4.35 4.35 0 01.12-3.21s1.02-.33 3.34 1.24a11.52 11.52 0 016.06 0c2.31-1.57 3.33-1.24 3.33-1.24a4.35 4.35 0 01.12 3.21 4.68 4.68 0 011.25 3.25c0 4.66-2.84 5.69-5.54 5.99.44.37.82 1.12.82 2.26l-.01 3.35c0 .32.22.7.84.57A12 12 0 0012 .3"/></svg>'
ICON_PIXIV   = '<svg viewBox="0 0 24 24"><path d="M4.94 2.04c2.1-.22 4.92.22 6.53 2.04 2.7-.48 5.12.86 6.13 3.15 1.06 2.39.66 5.32-1.15 7.2-1.25 1.3-3.04 1.92-4.83 1.87-.34 1.74-.64 3.49-.97 5.24H7.87l.78-4.16c-1.56-.74-2.56-2.35-2.6-4.06a4.7 4.7 0 012.36-4.33c-.28-1.27-.52-2.55-.79-3.82-.73 0-1.46-.01-2.19-.03v-3.1h.01zm5.19 5.7a2.6 2.6 0 00-1.7 2.8c.12.95.84 1.77 1.77 1.97.44-.76.86-1.53 1.3-2.3-.5-.77-.94-1.58-1.37-2.4v-.07zm3.14-.14c-.56.93-1.08 1.87-1.6 2.82.65.67 1.27 1.38 1.95 2.02.94-.5 1.6-1.5 1.65-2.56.07-1.12-.74-2.18-1.83-2.3l-.17.02z"/></svg>'
ICON_BILIBILI = '<svg viewBox="0 0 24 24"><path d="M17.81 4.47c.08 0 .16-.02.23-.06.74-.4 1.38-.96 1.87-1.67a.26.26 0 00-.23-.38h-.01a.27.27 0 00-.21.11c-.45.63-1.02 1.15-1.68 1.52a.27.27 0 00.03.48zm-11.6 0a.27.27 0 00.03-.48A5.58 5.58 0 014.56 2.47.27.27 0 004.33 2.36h-.01a.27.27 0 00-.23.38c.49.71 1.13 1.27 1.87 1.67a.28.28 0 00.25.06zM22 8.12a2 2 0 00-2-2H4a2 2 0 00-2 2v9.5a2 2 0 002 2h16a2 2 0 002-2v-9.5zm-1.5.5v8.5a1 1 0 01-1 1H4.5a1 1 0 01-1-1v-8.5a1 1 0 011-1h15a1 1 0 011 1zM10 13.25a.74.74 0 01-.75.75H7.5a.75.75 0 010-1.5h1.75c.41 0 .75.34.75.75zm7.25 0a.74.74 0 01-.75.75H14.75a.75.75 0 010-1.5h1.75c.41 0 .75.34.75.75z"/></svg>'

# ── 构建首页 ─────────────────────────────────────────
def build_index(posts, template):
    posts.sort(key=lambda p: p["date"], reverse=True)

    categories = sorted(set(p["category"] for p in posts if p["category"]))
    cat_counts = {}
    for p in posts:
        c = p["category"]
        if c:
            cat_counts[c] = cat_counts.get(c, 0) + 1

    # ── Hero（社交链接+主博客合并一行，无下箭头） ──
    hero = f'''  <div class="hero">
    <h1 class="hero-title">流形上的涂鸦</h1>
    <p class="hero-subtitle">Scribbles on Manifolds — 一些数学笔记与思考</p>
    <div class="hero-links">
      <a class="blog-link" href="https://chenhuhuhu.space">{ICON_BLOG} 主博客</a>
      <span class="sep">/</span>
      <a href="https://www.pixiv.net/users/79490957" target="_blank">{ICON_PIXIV} Pixiv</a>
      <span class="sep">/</span>
      <a href="https://github.com/ColonelJo2333" target="_blank">{ICON_GITHUB} GitHub</a>
      <span class="sep">/</span>
      <a href="https://space.bilibili.com/506403405" target="_blank">{ICON_BILIBILI} Bilibili</a>
    </div>
  </div>'''

    # ── 左侧时间轴 ──
    sidebar_tl = '    <aside class="sidebar-timeline">\n'
    current_year = ""
    for p in posts:
        year = p["date"][:4] if p["date"] else ""
        if year != current_year:
            current_year = year
            sidebar_tl += f'      <div class="tl-year">{year}</div>\n'
        date_short = p["date"][5:] if len(p["date"]) >= 10 else p["date"]
        sidebar_tl += f'      <div class="tl-dot">{date_short}</div>\n'
    sidebar_tl += '    </aside>'

    # ── 中间文章预览（平铺，无卡片） ──
    entries = '    <div class="post-entries">\n'
    for p in posts:
        cat_html = f'<span class="post-entry-cat">{p["category"]}</span>' if p["category"] else ""
        abstract_html = f'\n        <div class="post-entry-abstract">{p["abstract"]}</div>' if p["abstract"] else ""
        excerpt_html  = f'\n        <div class="post-entry-excerpt">{p["excerpt"]}</div>' if p["excerpt"] else ""
        entries += f'''      <div class="post-entry">
        <div class="post-entry-title"><a href="{p["slug"]}.html">{p["title"]}</a></div>
        <div class="post-entry-meta"><span>{p["date"]}</span>{cat_html}</div>{abstract_html}{excerpt_html}
        <a class="post-entry-more" href="{p["slug"]}.html">Read More</a>
      </div>
'''
    entries += '    </div>'

    # ── 右侧分类 ──
    sidebar_cats = '    <aside class="sidebar-cats">\n'
    sidebar_cats += '      <div class="sidebar-cats-title">分类</div>\n'
    for c in categories:
        sidebar_cats += f'      <a href="#">{c} <span class="cat-count">{cat_counts[c]}</span></a>\n'
    sidebar_cats += '    </aside>'

    # ── 组合 ──
    page = f'''{hero}

  <div class="home-body">
{sidebar_tl}
{entries}
{sidebar_cats}
  </div>'''

    html = template.replace("{{title}}", "流形上的涂鸦").replace("{{page_content}}", page)
    out = DIST_DIR / "index.html"
    out.write_text(html, encoding="utf-8")

# ── 完整构建 ─────────────────────────────────────────
def build():
    print("⚙  构建中...")
    start = time.time()

    if DIST_DIR.exists():
        for item in DIST_DIR.iterdir():
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
            except PermissionError:
                pass
    else:
        DIST_DIR.mkdir(parents=True)

    shutil.copy2(STYLE, DIST_DIR / "style.css")
    template = TEMPLATE.read_text(encoding="utf-8")

    md_files = sorted(POSTS_DIR.glob("*.md"))
    if not md_files:
        print("⚠  posts/ 目录下没有 .md 文件")

    posts = []
    for md in md_files:
        info = build_post(md, template)
        posts.append(info)
        print(f"   ✓ {md.name} → {info['file'].name}")

    build_index(posts, template)
    print(f"   ✓ index.html")

    elapsed = time.time() - start
    print(f"✔  构建完成 ({len(posts)} 篇, {elapsed:.2f}s)")

# ── 本地预览服务器 ───────────────────────────────────
class QuietHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST_DIR), **kwargs)
    def log_message(self, fmt, *args):
        if args and str(args[1]) != "200":
            super().log_message(fmt, *args)

def watch_and_rebuild(interval=1.0):
    watch_files = [TEMPLATE, STYLE]
    def get_mtimes():
        mtimes = {}
        for f in watch_files:
            if f.exists():
                mtimes[str(f)] = f.stat().st_mtime
        for md in POSTS_DIR.glob("*.md"):
            mtimes[str(md)] = md.stat().st_mtime
        return mtimes

    last_mtimes = get_mtimes()
    while True:
        time.sleep(interval)
        current = get_mtimes()
        if current != last_mtimes:
            print("\n♻  检测到变化，重建...")
            try:
                build()
            except Exception as e:
                print(f"✗  构建失败: {e}")
            last_mtimes = get_mtimes()

def serve(port=8000):
    build()
    watcher = threading.Thread(target=watch_and_rebuild, daemon=True)
    watcher.start()
    print(f"\n🌐 预览服务器: http://localhost:{port}")
    print("   (保存文件自动重建，Ctrl+C 退出)\n")
    server = HTTPServer(("", port), QuietHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 再见")
        server.shutdown()

# ── 入口 ─────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "build":
        build()
    elif sys.argv[1] == "serve":
        p = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
        serve(p)
    else:
        print(f"用法: python {sys.argv[0]} [build|serve]")
        sys.exit(1)
